import io, os
from flask import Blueprint, jsonify, request
from .storage import upload_bytes, presign_get
from . import db

# 1) Create the blueprint FIRST
bp = Blueprint("main", __name__)

# 2) Then add routes that use it
@bp.get("/")
def index():
    return "<h1>Pro Photo Starter</h1><p>It works ✅</p>"

@bp.get("/healthz")
def health():
    # DB ping
    try:
        db.session.execute(db.text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False
    return jsonify(status="ok", db=db_ok)

@bp.post("/upload")
def upload():
    f = request.files.get("file")
    if not f:
        return jsonify(error="file required"), 400
    key = f"uploads/{f.filename}"
    sha = upload_bytes(
        f.stream if hasattr(f, "stream") else io.BytesIO(f.read()),
        key,
        f.mimetype or "application/octet-stream"
    )
    url = presign_get(key, 300)
    return jsonify(key=key, sha256=sha, url=url)
