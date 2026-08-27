import hashlib
import json
import secrets
from datetime import datetime, timezone
from flask_login import UserMixin
from app.extensions import db, bcrypt


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(190), unique=True, nullable=False, index=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="user", nullable=False)  # 'admin' or 'user'
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    settings = db.relationship("UserSettings", backref="user", uselist=False, cascade="all, delete-orphan")
    api_keys = db.relationship("APIKey", backref="user", lazy=True, cascade="all, delete-orphan")
    tasks = db.relationship("Task", backref="user", lazy=True, cascade="all, delete-orphan")
    notes = db.relationship("Note", backref="user", lazy=True, cascade="all, delete-orphan")
    expenses = db.relationship("ExpenseTransaction", backref="user", lazy=True, cascade="all, delete-orphan")
    budgets = db.relationship("Budget", backref="user", lazy=True, cascade="all, delete-orphan")
    calculations = db.relationship("Calculation", backref="user", lazy=True, cascade="all, delete-orphan")
    short_urls = db.relationship("ShortURL", backref="user", lazy=True, cascade="all, delete-orphan")
    color_palettes = db.relationship("ColorPalette", backref="user", lazy=True, cascade="all, delete-orphan")
    api_requests = db.relationship("ApiRequest", backref="user", lazy=True, cascade="all, delete-orphan")
    analytics_datasets = db.relationship("AnalyticsDataset", backref="user", lazy=True, cascade="all, delete-orphan")
    file_jobs = db.relationship("FileJob", backref="user", lazy=True, cascade="all, delete-orphan")
    activity_logs = db.relationship("ActivityLog", backref="user", lazy=True, cascade="all, delete-orphan")
    notifications = db.relationship("Notification", backref="user", lazy=True, cascade="all, delete-orphan")

    def set_password(self, password: str):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, password)

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
        }


class UserSettings(db.Model):
    __tablename__ = "user_settings"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    theme = db.Column(db.String(16), default="dark", nullable=False)  # 'dark', 'light', 'system'
    timezone = db.Column(db.String(64), default="UTC", nullable=False)
    language = db.Column(db.String(16), default="en", nullable=False)
    notifications_enabled = db.Column(db.Boolean, default=True, nullable=False)

    def to_dict(self):
        return {
            "theme": self.theme,
            "timezone": self.timezone,
            "language": self.language,
            "notifications_enabled": self.notifications_enabled,
        }


class APIKey(db.Model):
    __tablename__ = "api_keys"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = db.Column(db.String(64), default="Default Key", nullable=False)
    key_prefix = db.Column(db.String(16), nullable=False)  # First few chars like ck_live_xxxx
    key_hash = db.Column(db.String(255), nullable=False, unique=True, index=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    last_used_at = db.Column(db.DateTime, nullable=True)

    @staticmethod
    def generate(user_id: int, name: str = "API Key"):
        raw_key = f"cck_{secrets.token_urlsafe(32)}"
        prefix = raw_key[:10]
        hashed = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
        record = APIKey(user_id=user_id, name=name, key_prefix=prefix, key_hash=hashed)
        return raw_key, record

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "key_prefix": self.key_prefix,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None,
        }
