import json
import uuid
from flask import Blueprint, jsonify, render_template, request, Response
from flask_login import current_user, login_required
from app.extensions import db
from app.models.webhook import WebhookEndpoint, WebhookDelivery
from app.utils.decorators import api_or_login_required

webhooks_bp = Blueprint("webhooks", __name__)


@webhooks_bp.route("/webhooks")
@login_required
def view():
    """Renders the developer webhook interceptor and inspection dashboard."""
    return render_template("tools/webhooks.html")


@webhooks_bp.route("/api/v1/webhooks/endpoints", methods=["GET", "POST"])
@api_or_login_required
def manage_endpoints():
    """Create or list webhook listener endpoints for the user."""
    user_id = current_user.id
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        name = data.get("name", "Custom Webhook").strip() or "Custom Webhook"
        token = str(uuid.uuid4()).replace("-", "")[:16]
        endpoint = WebhookEndpoint(user_id=user_id, endpoint_token=token, name=name)
        db.session.add(endpoint)
        db.session.commit()
        return jsonify({"status": "success", "endpoint": endpoint.to_dict()}), 201

    endpoints = WebhookEndpoint.query.filter_by(user_id=user_id).order_by(WebhookEndpoint.created_at.desc()).all()
    return jsonify([e.to_dict() for e in endpoints])


@webhooks_bp.route("/api/v1/webhooks/endpoints/<int:endpoint_id>/deliveries", methods=["GET"])
@api_or_login_required
def get_deliveries(endpoint_id):
    """Retrieves captured payloads, headers, and metadata for an endpoint."""
    user_id = current_user.id
    endpoint = WebhookEndpoint.query.filter_by(id=endpoint_id, user_id=user_id).first_or_404()
    deliveries = (
        WebhookDelivery.query.filter_by(endpoint_id=endpoint.id)
        .order_by(WebhookDelivery.received_at.desc())
        .limit(50)
        .all()
    )
    return jsonify([d.to_dict() for d in deliveries])


@webhooks_bp.route("/hook/<string:token>", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
def capture_webhook(token):
    """
    Public webhook receiver that intercepts third-party webhooks (Stripe, GitHub, etc.)
    and records payload, headers, and signatures.
    """
    endpoint = WebhookEndpoint.query.filter_by(endpoint_token=token, is_active=True).first_or_404()

    # Capture headers (convert multidict to standard dict)
    headers = {k: v for k, v in request.headers.items()}
    query_params = {k: v for k, v in request.args.items()}

    # Capture raw payload or JSON
    raw_payload = request.get_data(as_text=True)
    
    # Check common signature headers
    sig_header = (
        request.headers.get("X-Hub-Signature-256")
        or request.headers.get("Stripe-Signature")
        or request.headers.get("X-Razorpay-Signature")
        or request.headers.get("X-Signature")
    )

    delivery = WebhookDelivery(
        endpoint_id=endpoint.id,
        method=request.method,
        ip_address=request.headers.get("X-Forwarded-For", request.remote_addr),
        headers_json=json.dumps(headers),
        payload_json=raw_payload,
        query_params_json=json.dumps(query_params),
        content_type=request.content_type,
        signature_header=sig_header,
    )
    db.session.add(delivery)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Webhook payload captured successfully",
        "delivery_id": delivery.id,
    }), 200
