import io
import os
from pathlib import Path
import secrets
from flask import Blueprint, Response, jsonify, render_template, request, send_file
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from app.config import Config
from app.extensions import db
from app.models.file_job import FileJob
from app.services.file_service import (
    inspect_pdf_metadata,
    merge_pdfs,
    process_image,
    protect_pdf_with_password,
    split_or_extract_pdf_pages,
)
from app.services.auth_service import log_activity
from app.services.notification_service import send_notification
from app.utils.decorators import api_or_login_required

file_tools_bp = Blueprint("file_tools", __name__)


@file_tools_bp.route("/file-tools")
@login_required
def view():
    return render_template("tools/file_tools.html")


@file_tools_bp.route("/api/v1/file-tools/image/process", methods=["POST"])
@api_or_login_required
def handle_image():
    user_id = current_user.id
    if "file" not in request.files:
        return jsonify({"status": "error", "message": "No image file uploaded."}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"status": "error", "message": "No file selected."}), 400

    filename = secure_filename(file.filename)
    raw_bytes = file.read()
    orig_size = len(raw_bytes)

    action = request.form.get("action", "convert")
    target_format = request.form.get("target_format", "png")
    width = request.form.get("width", type=int)
    height = request.form.get("height", type=int)
    quality = request.form.get("quality", 85, type=int)
    rotation = request.form.get("rotation", 0, type=int)
    watermark = request.form.get("watermark", "").strip()

    try:
        out_bytes, ext, mime = process_image(
            raw_bytes,
            action=action,
            target_format=target_format,
            width=width,
            height=height,
            quality=quality,
            rotation_angle=rotation,
            watermark_text=watermark,
        )

        # Save to temporary storage with token
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        token = secrets.token_urlsafe(16)
        out_name = f"{Path(filename).stem}_processed.{ext}"
        saved_path = os.path.join(Config.UPLOAD_FOLDER, f"proc_{token}_{out_name}")

        with open(saved_path, "wb") as f:
            f.write(out_bytes)

        job = FileJob(
            user_id=user_id,
            job_type=f"image_{action}",
            original_filename=filename,
            processed_filename=out_name,
            original_size=orig_size,
            processed_size=len(out_bytes),
            download_token=token,
        )
        db.session.add(job)
        db.session.commit()

        log_activity(user_id, "processed_image", "file_tools", f"Transformed image: {filename} -> {out_name}")
        send_notification(user_id, "Image Processed Successfully", f"Transformed {filename} into {out_name}.", "success", "/file-tools")

        return jsonify({
            "status": "success",
            "download_token": token,
            "filename": out_name,
            "original_size": orig_size,
            "processed_size": len(out_bytes),
            "savings_pct": round((1 - len(out_bytes) / orig_size) * 100, 1) if orig_size > 0 else 0,
        })

    except Exception as e:
        return jsonify({"status": "error", "message": f"Image processing failed: {str(e)}"}), 500


@file_tools_bp.route("/api/v1/file-tools/pdf/merge", methods=["POST"])
@api_or_login_required
def handle_pdf_merge():
    user_id = current_user.id
    uploaded_files = request.files.getlist("files")
    if not uploaded_files or len(uploaded_files) < 2:
        return jsonify({"status": "error", "message": "At least 2 PDF files are required for merging."}), 400

    pdf_bytes_list = []
    total_in_size = 0
    for f in uploaded_files:
        data = f.read()
        pdf_bytes_list.append(data)
        total_in_size += len(data)

    try:
        merged_bytes = merge_pdfs(pdf_bytes_list)
        token = secrets.token_urlsafe(16)
        out_name = "merged_document.pdf"
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        saved_path = os.path.join(Config.UPLOAD_FOLDER, f"proc_{token}_{out_name}")

        with open(saved_path, "wb") as f:
            f.write(merged_bytes)

        job = FileJob(
            user_id=user_id,
            job_type="pdf_merge",
            original_filename=f"{len(uploaded_files)} PDF Files",
            processed_filename=out_name,
            original_size=total_in_size,
            processed_size=len(merged_bytes),
            download_token=token,
        )
        db.session.add(job)
        db.session.commit()

        return jsonify({
            "status": "success",
            "download_token": token,
            "filename": out_name,
            "processed_size": len(merged_bytes),
        })
    except Exception as e:
        return jsonify({"status": "error", "message": f"PDF merge failed: {str(e)}"}), 500


@file_tools_bp.route("/api/v1/file-tools/pdf/split", methods=["POST"])
@api_or_login_required
def handle_pdf_split():
    user_id = current_user.id
    if "file" not in request.files:
        return jsonify({"status": "error", "message": "No PDF file uploaded."}), 400

    file = request.files["file"]
    pages_str = request.form.get("pages", "1").strip()
    raw_bytes = file.read()

    # Parse pages like "1, 2, 3-5"
    pages_to_extract = []
    for part in pages_str.split(","):
        part = part.strip()
        if "-" in part:
            try:
                start, end = map(int, part.split("-"))
                pages_to_extract.extend(range(start, end + 1))
            except ValueError:
                pass
        elif part.isdigit():
            pages_to_extract.append(int(part))

    if not pages_to_extract:
        return jsonify({"status": "error", "message": "Invalid page specification."}), 400

    try:
        split_bytes = split_or_extract_pdf_pages(raw_bytes, pages_to_extract)
        token = secrets.token_urlsafe(16)
        out_name = f"{Path(secure_filename(file.filename)).stem}_extracted.pdf"
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        saved_path = os.path.join(Config.UPLOAD_FOLDER, f"proc_{token}_{out_name}")

        with open(saved_path, "wb") as f:
            f.write(split_bytes)

        job = FileJob(
            user_id=user_id,
            job_type="pdf_split",
            original_filename=secure_filename(file.filename),
            processed_filename=out_name,
            original_size=len(raw_bytes),
            processed_size=len(split_bytes),
            download_token=token,
        )
        db.session.add(job)
        db.session.commit()

        log_activity(user_id, "split_pdf", "file_tools", f"Split PDF: {file.filename} -> {out_name}")
        send_notification(user_id, "PDF Split Successfully", f"Extracted pages from {file.filename}.", "success", "/file-tools")

        return jsonify({
            "status": "success",
            "download_token": token,
            "filename": out_name,
            "processed_size": len(split_bytes),
        })
    except Exception as e:
        return jsonify({"status": "error", "message": f"PDF split failed: {str(e)}"}), 500


@file_tools_bp.route("/api/v1/file-tools/download/<string:token>", methods=["GET"])
def download_file(token):
    job = FileJob.query.filter_by(download_token=token).first_or_404()
    saved_path = os.path.join(Config.UPLOAD_FOLDER, f"proc_{token}_{job.processed_filename}")

    if not os.path.exists(saved_path):
        return jsonify({"status": "error", "message": "File has expired or was removed."}), 404

    return send_file(saved_path, as_attachment=True, download_name=job.processed_filename)
