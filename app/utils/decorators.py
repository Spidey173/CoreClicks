import hashlib
from functools import wraps
from flask import abort, g, jsonify, request
from flask_login import current_user
from app.models.user import APIKey, User


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def api_or_login_required(f):
    """Allows either session login (current_user) or API token (Bearer cck_...)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            g.current_user = current_user
            return f(*args, **kwargs)

        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1].strip()
            key_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
            api_key = APIKey.query.filter_by(key_hash=key_hash, is_active=True).first()
            if api_key:
                user = User.query.get(api_key.user_id)
                if user and user.is_active:
                    g.current_user = user
                    return f(*args, **kwargs)

        # If user is not authenticated
        if request.path.startswith("/api/"):
            return jsonify({"status": "error", "message": "Authentication required."}), 401
        abort(401)

    return decorated_function
