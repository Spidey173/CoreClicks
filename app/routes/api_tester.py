from flask import Blueprint, jsonify, render_template, request
from flask_login import current_user, login_required
from app.extensions import db
from app.models.api_request import ApiRequest
from app.services.api_tester_service import execute_http_request
from app.services.auth_service import log_activity
from app.utils.decorators import api_or_login_required

api_tester_bp = Blueprint("api_tester", __name__)


@api_tester_bp.route("/api-tester")
@login_required
def view():
    return render_template("tools/api_tester.html")


@api_tester_bp.route("/api/v1/api-tester/send", methods=["POST"])
@api_or_login_required
def send_request():
    user_id = current_user.id
    data = request.get_json(silent=True) or {}

    method = data.get("method", "GET").upper()
    url = data.get("url", "").strip()
    headers = data.get("headers", {})
    body = data.get("body")
    auth_type = data.get("auth_type", "none")
    auth_data = data.get("auth_data", {})
    req_name = data.get("name", f"{method} {url}")

    if not url:
        return jsonify({"status": "error", "message": "Target URL is required."}), 400

    resp_result = execute_http_request(
        method=method,
        url=url,
        headers=headers,
        body=body,
        auth_type=auth_type,
        auth_data=auth_data,
    )

    # Save to history log
    api_log = ApiRequest(
        user_id=user_id,
        name=req_name,
        method=method,
        url=url,
        body=body,
        auth_type=auth_type,
        status_code=resp_result.get("status_code"),
        latency_ms=resp_result.get("latency_ms", 0.0),
        is_saved=False,
    )
    api_log.headers = headers

    try:
        db.session.add(api_log)
        db.session.commit()
        log_activity(user_id, "api_test", "api_tester", f"{method} {url} ({resp_result.get('status_code')})")
    except Exception:
        db.session.rollback()

    resp_result["id"] = api_log.id
    return jsonify(resp_result)


@api_tester_bp.route("/api/v1/api-tester/history", methods=["GET"])
@api_or_login_required
def history():
    user_id = current_user.id
    logs = ApiRequest.query.filter_by(user_id=user_id).order_by(ApiRequest.created_at.desc()).limit(20).all()
    return jsonify([l.to_dict() for l in logs])


@api_tester_bp.route("/api/v1/api-tester/history", methods=["DELETE"])
@api_or_login_required
def clear_history():
    user_id = current_user.id
    ApiRequest.query.filter_by(user_id=user_id, is_saved=False).delete()
    db.session.commit()
    return jsonify({"status": "success", "message": "History cleared."})


@api_tester_bp.route("/api/v1/api-tester/saved", methods=["GET", "POST"])
@api_or_login_required
def saved_requests():
    user_id = current_user.id
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        req_obj = ApiRequest(
            user_id=user_id,
            name=data.get("name", "Saved Request"),
            method=data.get("method", "GET").upper(),
            url=data.get("url", ""),
            body=data.get("body", ""),
            auth_type=data.get("auth_type", "none"),
            collection_name=data.get("collection_name", "Default"),
            is_saved=True,
        )
        req_obj.headers = data.get("headers", {})
        db.session.add(req_obj)
        db.session.commit()
        return jsonify({"status": "success", "request": req_obj.to_dict()}), 201

    saved = ApiRequest.query.filter_by(user_id=user_id, is_saved=True).order_by(ApiRequest.created_at.desc()).all()
    return jsonify([s.to_dict() for s in saved])
