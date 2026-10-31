"""Flask application factory."""

from pathlib import Path

from flask import Flask

PACKAGE_DIR = Path(__file__).resolve().parent.parent


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder=str(PACKAGE_DIR / "templates"),
        static_folder=str(PACKAGE_DIR / "static"),
    )
    from numerology.web.routes import bp

    app.register_blueprint(bp)
    return app
