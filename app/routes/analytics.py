import os
from flask import Blueprint, jsonify, render_template, request
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from app.config import Config
from app.extensions import db
from app.models.analytics_dataset import AnalyticsDataset
from app.services.analytics_service import parse_csv_bytes
from app.services.auth_service import log_activity
from app.services.notification_service import send_notification
from app.utils.decorators import api_or_login_required

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.route("/analytics")
@login_required
def view():
    return render_template("tools/analytics.html")


@analytics_bp.route("/api/v1/analytics/upload", methods=["POST"])
@api_or_login_required
def upload_csv():
    user_id = current_user.id
    if "file" not in request.files:
        return jsonify({"status": "error", "message": "No CSV file provided."}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"status": "error", "message": "No file selected."}), 400

    filename = secure_filename(file.filename)
    file_bytes = file.read()

    try:
        profile_res = parse_csv_bytes(file_bytes, filename)

        # Save record
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        stored_path = os.path.join(Config.UPLOAD_FOLDER, f"ds_{user_id}_{filename}")
        with open(stored_path, "wb") as f:
            f.write(file_bytes)

        ds = AnalyticsDataset(
            user_id=user_id,
            filename=filename,
            stored_path=stored_path,
            row_count=profile_res["overview"]["row_count"],
            col_count=profile_res["overview"]["col_count"],
            file_size=len(file_bytes),
        )
        ds.summary = profile_res

        db.session.add(ds)
        db.session.commit()

        log_activity(user_id, "uploaded_csv", "analytics", f"Analyzed dataset: {filename} ({ds.row_count} rows)")
        send_notification(user_id, "CSV Dataset Processed", f"Successfully profiled {filename} with {ds.row_count} rows and {ds.col_count} columns.", "success", "/analytics")

        profile_res["dataset_id"] = ds.id
        profile_res["filename"] = filename
        return jsonify({"status": "success", "analysis": profile_res}), 201

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@analytics_bp.route("/api/v1/analytics/datasets", methods=["GET"])
@api_or_login_required
def get_datasets():
    user_id = current_user.id
    datasets = AnalyticsDataset.query.filter_by(user_id=user_id).order_by(AnalyticsDataset.created_at.desc()).all()
    return jsonify([d.to_dict() for d in datasets])


@analytics_bp.route("/api/v1/analytics/datasets/<int:ds_id>", methods=["GET"])
@api_or_login_required
def get_dataset(ds_id):
    user_id = current_user.id
    ds = AnalyticsDataset.query.filter_by(id=ds_id, user_id=user_id).first_or_404()
    return jsonify({"status": "success", "analysis": ds.summary, "dataset": ds.to_dict()})


@analytics_bp.route("/api/v1/analytics/datasets/<int:ds_id>", methods=["DELETE"])
@api_or_login_required
def delete_dataset(ds_id):
    user_id = current_user.id
    ds = AnalyticsDataset.query.filter_by(id=ds_id, user_id=user_id).first_or_404()
    if os.path.exists(ds.stored_path):
        try:
            os.remove(ds.stored_path)
        except Exception:
            pass
    db.session.delete(ds)
    db.session.commit()
    return jsonify({"status": "success", "message": "Dataset deleted."})
