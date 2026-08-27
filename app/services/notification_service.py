from typing import List
from app.extensions import db
from app.models.activity import Notification


def send_notification(user_id: int, title: str, message: str, notif_type: str = "info", link: str = None) -> Notification:
    """Creates a persistent notification for a user."""
    notif = Notification(user_id=user_id, title=title, message=message, type=notif_type, link=link)
    try:
        db.session.add(notif)
        db.session.commit()
        return notif
    except Exception:
        db.session.rollback()
        return None


def get_user_notifications(user_id: int, limit: int = 15) -> List[Notification]:
    """Retrieves recent notifications for a user."""
    return Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).limit(limit).all()


def mark_notification_as_read(notif_id: int, user_id: int) -> bool:
    """Marks a single notification as read."""
    notif = Notification.query.filter_by(id=notif_id, user_id=user_id).first()
    if notif:
        notif.is_read = True
        db.session.commit()
        return True
    return False


def mark_all_notifications_read(user_id: int):
    """Marks all notifications for a user as read."""
    Notification.query.filter_by(user_id=user_id, is_read=False).update({"is_read": True})
    db.session.commit()
