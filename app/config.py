import os
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    """Base SaaS Configuration."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "coreclicks-saas-secret-key-prod-change")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
    
    # Uploads directory
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", str(BASE_DIR / "uploads"))
    MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32MB max upload
    ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif", "bmp"}
    ALLOWED_PDF_EXTENSIONS = {"pdf"}
    ALLOWED_CSV_EXTENSIONS = {"csv", "tsv", "txt"}
    
    # Session & Security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    WTF_CSRF_ENABLED = False


class DevelopmentConfig(Config):
    """Development Configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'database.db'}"
    )


class TestingConfig(Config):
    """Testing Configuration."""
    TESTING = True
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    UPLOAD_FOLDER = str(BASE_DIR / "test_uploads")


class ProductionConfig(Config):
    """Production Configuration."""
    DEBUG = False
    TESTING = False
    db_url = os.environ.get("DATABASE_URL", f"sqlite:///{BASE_DIR / 'database.db'}")
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = db_url


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
