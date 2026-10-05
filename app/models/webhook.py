import json
import uuid
from datetime import datetime, timezone
from app.extensions import db


class WebhookEndpoint(db.Model):
    """Temporary or persistent Webhook endpoints for intercepting developer webhooks."""
    __tablename__ = "webhook_endpoints"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    endpoint_token = db.Column(db.String(64), unique=True, nullable=False, index=True)
    name = db.Column(db.String(128), default="Custom Webhook", nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    deliveries = db.relationship("WebhookDelivery", backref="endpoint", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "endpoint_token": self.endpoint_token,
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "is_active": self.is_active,
            "total_deliveries": len(self.deliveries),
        }


class WebhookDelivery(db.Model):
    """Captured payload, headers, HMAC signature, and telemetry for incoming webhooks."""
    __tablename__ = "webhook_deliveries"

    id = db.Column(db.Integer, primary_key=True)
    endpoint_id = db.Column(db.Integer, db.ForeignKey("webhook_endpoints.id", ondelete="CASCADE"), nullable=False, index=True)
    method = db.Column(db.String(10), default="POST", nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)
    headers_json = db.Column(db.Text, nullable=False, default="{}")
    payload_json = db.Column(db.Text, nullable=True)
    query_params_json = db.Column(db.Text, nullable=False, default="{}")
    content_type = db.Column(db.String(128), nullable=True)
    signature_header = db.Column(db.String(255), nullable=True)
    received_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "endpoint_id": self.endpoint_id,
            "method": self.method,
            "ip_address": self.ip_address,
            "headers": json.loads(self.headers_json) if self.headers_json else {},
            "payload": json.loads(self.payload_json) if self.payload_json else self.payload_json,
            "query_params": json.loads(self.query_params_json) if self.query_params_json else {},
            "content_type": self.content_type,
            "signature_header": self.signature_header,
            "received_at": self.received_at.isoformat(),
        }
