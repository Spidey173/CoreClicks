from datetime import datetime, timezone
from typing import Optional, Tuple
from app.extensions import db
from app.models.user import APIKey, User, UserSettings
from app.models.activity import ActivityLog


def register_user(email: str, username: str, password: str, role: str = "user") -> Tuple[Optional[User], Optional[str]]:
    """Registers a new user with hashed password and default settings."""
    email = email.strip().lower()
    username = username.strip()

    if not email or "@" not in email:
        return None, "A valid email address is required."
    if not username or len(username) < 3:
        return None, "Username must be at least 3 characters long."
    if not password or len(password) < 6:
        return None, "Password must be at least 6 characters long."

    if User.query.filter_by(email=email).first():
        return None, "An account with this email already exists."
    if User.query.filter_by(username=username).first():
        return None, "This username is already taken."

    user = User(email=email, username=username, role=role)
    user.set_password(password)

    settings = UserSettings(user=user, theme="dark", timezone="UTC", language="en")

    try:
        db.session.add(user)
        db.session.add(settings)
        db.session.commit()
        log_activity(user.id, "registered", "auth", "User account registered successfully.")
        return user, None
    except Exception as e:
        db.session.rollback()
        return None, f"Registration failed: {str(e)}"


def authenticate_user(identifier: str, password: str) -> Optional[User]:
    """Authenticates a user by either email or username."""
    identifier = identifier.strip().lower()
    user = User.query.filter((User.email == identifier) | (User.username == identifier)).first()

    if user and user.check_password(password) and user.is_active:
        return user
    return None


def log_activity(user_id: int, action: str, module: str, details: str = "", ip: str = None):
    """Records an activity event for a user."""
    try:
        log = ActivityLog(user_id=user_id, action=action, module=module, details=details, ip_address=ip)
        db.session.add(log)
        db.session.commit()
    except Exception:
        db.session.rollback()


def create_api_key(user_id: int, name: str = "Default Key") -> Tuple[str, APIKey]:
    """Generates and stores a new API key."""
    raw_key, api_key_obj = APIKey.generate(user_id, name)
    db.session.add(api_key_obj)
    db.session.commit()
    log_activity(user_id, "created_api_key", "settings", f"Generated API key: {name}")
    return raw_key, api_key_obj
