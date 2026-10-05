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
    default_upload = "/tmp/uploads" if os.environ.get("VERCEL") else str(BASE_DIR / "uploads")
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", default_upload)
    MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32MB max upload
    ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif", "bmp"}
    ALLOWED_PDF_EXTENSIONS = {"pdf"}
    ALLOWED_CSV_EXTENSIONS = {"csv", "tsv", "txt"}
    
    # Session & Security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    WTF_CSRF_ENABLED = False


def get_database_uri():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        db_url = "postgresql+psycopg2://localhost:5432/coreclicks"
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+psycopg2://", 1)
    elif db_url.startswith("postgresql://") and not db_url.startswith("postgresql+"):
        db_url = db_url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return db_url


class DevelopmentConfig(Config):
    """Development Configuration."""
    DEBUG = True

    def __init__(self):
        super().__init__()
        self.SQLALCHEMY_DATABASE_URI = get_database_uri()


class TestingConfig(Config):
    """Testing Configuration."""
    TESTING = True
    DEBUG = False
    WTF_CSRF_ENABLED = False
    UPLOAD_FOLDER = str(BASE_DIR / "test_uploads")

    def __init__(self):
        super().__init__()
        self.SQLALCHEMY_DATABASE_URI = get_database_uri()


class ProductionConfig(Config):
    """Production Configuration."""
    DEBUG = False
    TESTING = False

    def __init__(self):
        super().__init__()
        self.SQLALCHEMY_DATABASE_URI = get_database_uri()


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
