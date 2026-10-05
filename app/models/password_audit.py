from datetime import datetime, timezone
from app.extensions import db


class PasswordAudit(db.Model):
    __tablename__ = "password_audits"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    masked_password = db.Column(db.String(128), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    strength = db.Column(db.String(32), nullable=False)
    entropy_bits = db.Column(db.Float, nullable=False)
    crack_time_est = db.Column(db.String(64), nullable=False)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )

    def to_dict(self):
        return {
            "id": self.id,
            "masked_password": self.masked_password,
            "score": self.score,
            "strength": self.strength,
            "entropy_bits": round(self.entropy_bits, 1),
            "crack_time_est": self.crack_time_est,
            "created_at": self.created_at.isoformat(),
        }
