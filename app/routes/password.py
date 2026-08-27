from flask import Blueprint, jsonify, render_template, request
from flask_login import current_user, login_required
from app.extensions import db
from app.models.password_audit import PasswordAudit
from app.services.password_service import (
    analyze_password,
    generate_passphrase,
    generate_secure_password,
)
from app.services.auth_service import log_activity
from app.utils.decorators import api_or_login_required

password_bp = Blueprint("password", __name__)


@password_bp.route("/password-security")
@login_required
def view():
    return render_template("tools/password_security.html")


@password_bp.route("/api/v1/password-security/analyze", methods=["POST"])
@api_or_login_required
def analyze():
    user_id = current_user.id
    data = request.get_json(silent=True) or {}
    password = data.get("password", "")

    analysis = analyze_password(password)

    if password:
        audit = PasswordAudit(
            user_id=user_id,
            masked_password=analysis["masked"],
            score=analysis["score"],
            strength=analysis["strength"],
            entropy_bits=analysis["entropy_bits"],
            crack_time_est=analysis["crack_time"],
        )
        db.session.add(audit)
        db.session.commit()
        log_activity(user_id, "password_audit", "password_security", f"Audited password ({analysis['strength']})")

    return jsonify({"status": "success", "analysis": analysis}), 201


@password_bp.route("/api/v1/password-security/generate", methods=["POST"])
@api_or_login_required
def generate():
    data = request.get_json(silent=True) or {}
    gen_type = data.get("type", "random")

    if gen_type == "passphrase":
        words = int(data.get("words", 4))
        separator = data.get("separator", "-")
        pwd = generate_passphrase(word_count=words, separator=separator)
    else:
        length = int(data.get("length", 16))
        upper = bool(data.get("uppercase", True))
        nums = bool(data.get("numbers", True))
        syms = bool(data.get("symbols", True))
        pwd = generate_secure_password(length=length, uppercase=upper, numbers=nums, symbols=syms)

    analysis = analyze_password(pwd)
    return jsonify({
        "status": "success",
        "password": pwd,
        "analysis": analysis,
    })


@password_bp.route("/api/v1/password-security/history", methods=["GET"])
@api_or_login_required
def history():
    user_id = current_user.id
    audits = PasswordAudit.query.filter_by(user_id=user_id).order_by(PasswordAudit.created_at.desc()).limit(20).all()
    return jsonify([a.to_dict() for a in audits])
