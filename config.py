"""Flask configuration."""
from os import environ


class Config:
    """Base config."""

    ENV = environ.get("ENV")
    SECRET_KEY = environ.get("SECRET_KEY")
    SESSION_COOKIE_NAME = environ.get("SESSION_COOKIE_NAME")
    STATIC_FOLDER = "static"
    TEMPLATES_FOLDER = "templates"

    SESSION_COOKIE_SAMESITE = "Strict"
    SESSION_COOKIE_HTTPONLY = False
    SESSION_COOKIE_SECURE = True

    UPLOAD_FOLDER = environ.get("UPLOAD_FOLDER")
    ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}
    MAX_CONTENT_LENGTH = 2 * 1000 * 1000

    CLIENT_NAME = environ.get("CLIENT_NAME")


class ProdConfig(Config):
    DEBUG = False
    TESTING = False
    DATABASE_URI = environ.get("PROD_DATABASE_URI")


class DevConfig(Config):
    DEBUG = True
    TESTING = True
    DATABASE_URI = environ.get("DEV_DATABASE_URI")
