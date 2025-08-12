import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
from flask_talisman import Talisman

db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()

def _staging_basic_auth(app):
    from flask import request, Response
    user = os.getenv("STAGING_USER")
    pwd  = os.getenv("STAGING_PASS")
    def ask():
        return Response("Restricted staging", 401, {"WWW-Authenticate": 'Basic realm="Staging"'})
    @app.before_request
    def _gate():
        if os.getenv("FLASK_ENV") != "staging": return
        a = request.authorization
        if not a or a.username != user or a.password != pwd:
            return ask()

def create_app():
    from .routes import bp as main_bp
    from .models import *  # noqa

    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY","dev"),
        SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL","sqlite:///app.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.getenv("FLASK_ENV")=="production",
    )

    # Security headers / HTTPS in prod
    Talisman(app, force_https=bool(os.getenv("FLASK_ENV")=="production"), frame_options="DENY")

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    Limiter(get_remote_address, app=app, default_limits=["200/hour"])

    _staging_basic_auth(app)

    app.register_blueprint(main_bp)
    return app
