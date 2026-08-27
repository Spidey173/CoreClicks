from datetime import datetime
from flask import Blueprint, Response, jsonify, render_template, request
from flask_login import current_user, login_required
from app.extensions import db
from app.models.short_url import ShortURL
from app.services.url_service import (
    generate_qr_code_bytes,
    generate_short_code,
    is_valid_url,
    normalize_url,
)
from app.services.auth_service import log_activity
from app.utils.decorators import api_or_login_required

url_shortener_bp = Blueprint("url_shortener", __name__)


@url_shortener_bp.route("/url-shortener")
@login_required
def view():
    return render_template("tools/url_shortener.html")


@url_shortener_bp.route("/api/v1/url-shortener", methods=["GET", "POST"])
@api_or_login_required
def urls():
    user_id = current_user.id
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        raw_url = data.get("url", "").strip()
        title = data.get("title", "").strip() or "Short Link"
        custom_code = data.get("custom_code", "").strip()
        password = data.get("password", "").strip()
        expires_at_str = data.get("expires_at")

        if not raw_url or not is_valid_url(raw_url):
            return jsonify({"status": "error", "message": "Please enter a valid destination URL."}), 400

        clean_url = normalize_url(raw_url)

        if custom_code:
            if ShortURL.query.filter_by(short_code=custom_code).first():
                return jsonify({"status": "error", "message": "Custom alias is already in use."}), 409
            short_code = custom_code
        else:
            for _ in range(5):
                candidate = generate_short_code()
                if not ShortURL.query.filter_by(short_code=candidate).first():
                    short_code = candidate
                    break
            else:
                short_code = generate_short_code(8)

        expires_at = None
        if expires_at_str:
            try:
                expires_at = datetime.fromisoformat(expires_at_str)
            except ValueError:
                pass

        short_url = ShortURL(
            user_id=user_id,
            original_url=clean_url,
            short_code=short_code,
            title=title,
            expires_at=expires_at,
        )
        if password:
            short_url.set_password(password)

        try:
            db.session.add(short_url)
            db.session.commit()
            log_activity(user_id, "shortened_url", "url_shortener", f"Created link: /{short_code}")
            return jsonify({"status": "success", "short_url": short_url.to_dict()}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"status": "error", "message": str(e)}), 500

    links = ShortURL.query.filter_by(user_id=user_id).order_by(ShortURL.created_at.desc()).all()
    return jsonify([l.to_dict() for l in links])


@url_shortener_bp.route("/api/v1/url-shortener/<int:url_id>", methods=["DELETE"])
@api_or_login_required
def delete_url(url_id):
    user_id = current_user.id
    u = ShortURL.query.filter_by(id=url_id, user_id=user_id).first_or_404()
    db.session.delete(u)
    db.session.commit()
    return jsonify({"status": "success", "message": "Short link deleted."})


@url_shortener_bp.route("/api/v1/url-shortener/<int:url_id>/qr", methods=["GET"])
def get_qr_code(url_id):
    u = db.session.get(ShortURL, url_id)
    if not u:
        return jsonify({"status": "error", "message": "Link not found"}), 404
    fmt = request.args.get("format", "png").lower()
    full_url = f"{request.host_url}{u.short_code}"

    qr_bytes, mime = generate_qr_code_bytes(full_url, format_type=fmt)
    ext = "svg" if fmt == "svg" else "png"

    return Response(
        qr_bytes,
        mimetype=mime,
        headers={"Content-Disposition": f"inline;filename=qr_{u.short_code}.{ext}"},
    )
