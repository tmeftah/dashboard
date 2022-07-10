"""Flask configuration."""
from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
dotenv_path = path.join(basedir, ".env")
if path.exists(dotenv_path):
    load_dotenv(dotenv_path)


class Config:
    """Base config."""

    ENV = environ.get("ENV")
    SECRET_KEY = environ.get("SECRET_KEY")
    SESSION_COOKIE_NAME = environ.get("SESSION_COOKIE_NAME")
    STATIC_FOLDER = "static"
    TEMPLATES_FOLDER = "templates"

    SESSION_COOKIE_SAMESITE = "Strict"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True

    UPLOAD_FOLDER = environ.get("UPLOAD_FOLDER")
    ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}
    MAX_CONTENT_LENGTH = 2 * 1000 * 1000

    CLIENT_NAME = environ.get("CLIENT_NAME")

    @staticmethod
    def init_app(app):
        pass


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    DATABASE_URI = environ.get("PROD_DATABASE_URI") or "sqlite:///test.db"


class DevelopmentConfig(Config):
    DEBUG = True
    DATABASE_URI = environ.get("DEV_DATABASE_URI") or "sqlite:///test.db"


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    DATABASE_URI = environ.get("TEST_DATABASE_URI") or "sqlite://"


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
