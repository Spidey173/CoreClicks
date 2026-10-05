from flask import Blueprint, jsonify, request
from flask_login import current_user
from app.services.notification_service import (
    get_user_notifications,
    mark_all_notifications_read,
    mark_notification_as_read,
)
from app.utils.decorators import api_or_login_required

notifications_api_bp = Blueprint("api_notifications", __name__)


@notifications_api_bp.route("/api/v1/notifications", methods=["GET"])
@api_or_login_required
def get_notifications():
    user_id = current_user.id
    notifs = get_user_notifications(user_id, limit=20)
    unread_count = sum(1 for n in notifs if not n.is_read)
    return jsonify({
        "status": "success",
        "unread_count": unread_count,
        "notifications": [n.to_dict() for n in notifs],
    })


@notifications_api_bp.route("/api/v1/notifications/<int:notif_id>/read", methods=["POST"])
@api_or_login_required
def mark_read(notif_id):
    user_id = current_user.id
    success = mark_notification_as_read(notif_id, user_id)
    return jsonify({"status": "success" if success else "error"})


@notifications_api_bp.route("/api/v1/notifications/mark-all-read", methods=["POST"])
@api_or_login_required
def mark_all_read():
    user_id = current_user.id
    mark_all_notifications_read(user_id)
    return jsonify({"status": "success", "message": "All notifications marked as read."})
