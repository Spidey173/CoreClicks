from datetime import datetime, timezone
from app.extensions import db


class Calculation(db.Model):
    __tablename__ = "calculations"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    expression = db.Column(db.String(512), nullable=False)
    result = db.Column(db.String(256), nullable=False)
    mode = db.Column(db.String(32), default="scientific", nullable=False)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )

    def to_dict(self):
        return {
            "id": self.id,
            "expression": self.expression,
            "result": self.result,
            "mode": self.mode,
            "created_at": self.created_at.isoformat(),
        }
