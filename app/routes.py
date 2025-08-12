import io, os
from flask import Blueprint, jsonify, request
from .storage import upload_bytes, presign_get
from . import db

bp = Blueprint("main", __name__)

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
    if not f: return jsonify(error="file required"), 400
    key = f"uploads/{f.filename}"
    sha = upload_bytes(f.stream if hasattr(f,"stream") else io.BytesIO(f.read()), key, f.mimetype or "application/octet-stream")
    url = presign_get(key, 300)
    return jsonify(key=key, sha256=sha, url=url)
