import json
from datetime import datetime, timezone
from app.extensions import db


class ApiRequest(db.Model):
    __tablename__ = "api_requests"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = db.Column(db.String(128), default="Untitled Request", nullable=False)
    method = db.Column(db.String(16), default="GET", nullable=False)
    url = db.Column(db.String(2048), nullable=False)
    headers_json = db.Column(db.Text, default="{}", nullable=False)
    body = db.Column(db.Text, nullable=True)
    auth_type = db.Column(db.String(32), default="none", nullable=False)  # 'none', 'bearer', 'basic', 'apikey'
    status_code = db.Column(db.Integer, nullable=True)
    latency_ms = db.Column(db.Float, default=0.0, nullable=False)
    is_saved = db.Column(db.Boolean, default=False, nullable=False, index=True)
    collection_name = db.Column(db.String(64), default="Default", nullable=False)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )

    @property
    def headers(self):
        try:
            return json.loads(self.headers_json)
        except Exception:
            return {}

    @headers.setter
    def headers(self, value):
        self.headers_json = json.dumps(value if isinstance(value, dict) else {})

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "method": self.method,
            "url": self.url,
            "headers": self.headers,
            "body": self.body,
            "auth_type": self.auth_type,
            "status_code": self.status_code,
            "latency_ms": round(self.latency_ms, 1),
            "is_saved": self.is_saved,
            "collection_name": self.collection_name,
            "created_at": self.created_at.isoformat(),
        }
