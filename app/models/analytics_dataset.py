import json
from datetime import datetime, timezone
from app.extensions import db


class AnalyticsDataset(db.Model):
    __tablename__ = "analytics_datasets"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = db.Column(db.String(255), nullable=False)
    stored_path = db.Column(db.String(512), nullable=False)
    row_count = db.Column(db.Integer, default=0, nullable=False)
    col_count = db.Column(db.Integer, default=0, nullable=False)
    file_size = db.Column(db.Integer, default=0, nullable=False)
    summary_json = db.Column(db.Text, default="{}", nullable=False)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )

    @property
    def summary(self):
        try:
            return json.loads(self.summary_json)
        except Exception:
            return {}

    @summary.setter
    def summary(self, value):
        self.summary_json = json.dumps(value if isinstance(value, dict) else {})

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "row_count": self.row_count,
            "col_count": self.col_count,
            "file_size": self.file_size,
            "summary": self.summary,
            "created_at": self.created_at.isoformat(),
        }
