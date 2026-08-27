import os
import sys
from datetime import datetime, timezone
from flask import Blueprint, abort, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from app.extensions import db
from app.models.user import User
from app.models.activity import ActivityLog
from app.models.task import Task
from app.models.note import Note
from app.models.expense import ExpenseTransaction
from app.models.calculation import Calculation
from app.models.short_url import ShortURL
from app.models.file_job import FileJob
from app.utils.decorators import admin_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("")
@admin_bp.route("/")
@login_required
@admin_required
def index():
    users = User.query.order_by(User.created_at.desc()).all()
    logs = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(50).all()

    # System counts
    system_metrics = {
        "total_users": len(users),
        "total_tasks": Task.query.count(),
        "total_notes": Note.query.count(),
        "total_expenses": ExpenseTransaction.query.count(),
        "total_calcs": Calculation.query.count(),
        "total_urls": ShortURL.query.count(),
        "total_file_jobs": FileJob.query.count(),
        "python_version": sys.version.split()[0],
        "server_time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    }

    return render_template("admin/index.html", users=users, logs=logs, metrics=system_metrics)


@admin_bp.route("/users/<int:user_id>/toggle-role", methods=["POST"])
@login_required
@admin_required
def toggle_role(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You cannot modify your own administrative role.", "warning")
        return redirect(url_for("admin.index"))

    user.role = "user" if user.role == "admin" else "admin"
    db.session.commit()
    flash(f"Updated role for {user.username} to {user.role}.", "success")
    return redirect(url_for("admin.index"))


@admin_bp.route("/users/<int:user_id>/toggle-status", methods=["POST"])
@login_required
@admin_required
def toggle_status(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You cannot deactivate your own account.", "warning")
        return redirect(url_for("admin.index"))

    user.is_active = not user.is_active
    db.session.commit()
    status_str = "activated" if user.is_active else "deactivated"
    flash(f"Account for {user.username} has been {status_str}.", "info")
    return redirect(url_for("admin.index"))
