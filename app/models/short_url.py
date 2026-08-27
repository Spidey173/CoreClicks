from datetime import datetime, timezone
from app.extensions import db, bcrypt


class ShortURL(db.Model):
    __tablename__ = "short_urls"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    original_url = db.Column(db.String(2048), nullable=False)
    short_code = db.Column(db.String(32), unique=True, nullable=False, index=True)
    title = db.Column(db.String(128), default="Short Link", nullable=False)
    clicks = db.Column(db.Integer, default=0, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)
    expires_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )
    last_accessed = db.Column(db.DateTime, nullable=True)

    def set_password(self, password: str):
        if password and password.strip():
            self.password_hash = bcrypt.generate_password_hash(password.strip()).decode("utf-8")
        else:
            self.password_hash = None

    def check_password(self, password: str) -> bool:
        if not self.password_hash:
            return True
        return bcrypt.check_password_hash(self.password_hash, password)

    @property
    def is_expired(self) -> bool:
        if not self.expires_at:
            return False
        # Normalize timezone
        exp = self.expires_at.replace(tzinfo=timezone.utc) if self.expires_at.tzinfo is None else self.expires_at
        return datetime.now(timezone.utc) > exp

    def increment_clicks(self):
        self.clicks += 1
        self.last_accessed = datetime.now(timezone.utc)
        db.session.commit()

    def to_dict(self):
        return {
            "id": self.id,
            "original_url": self.original_url,
            "short_code": self.short_code,
            "title": self.title,
            "clicks": self.clicks,
            "has_password": bool(self.password_hash),
            "is_expired": self.is_expired,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None,
        }
