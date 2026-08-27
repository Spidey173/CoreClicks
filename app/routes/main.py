from datetime import date
from flask import Blueprint, abort, jsonify, redirect, render_template, request
from flask_login import current_user, login_required
from sqlalchemy import extract
from app.models.task import Task
from app.models.note import Note
from app.models.expense import ExpenseTransaction
from app.models.calculation import Calculation
from app.models.api_request import ApiRequest
from app.models.file_job import FileJob
from app.models.short_url import ShortURL
from app.services.expense_service import get_monthly_expense_summary
from app.services.task_service import get_task_statistics

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """Main route: Always renders the public showcase landing page on initial load."""
    return render_template("landing.html")


@main_bp.route("/landing")
def landing():
    """Public marketing landing page."""
    return render_template("landing.html")


@main_bp.route("/dashboard")
@login_required
def dashboard():
    """Authenticated SaaS Overview Dashboard."""
    user_id = current_user.id
    task_stats = get_task_statistics(user_id)
    expense_summary = get_monthly_expense_summary(user_id)

    # Widgets
    recent_tasks = Task.query.filter_by(user_id=user_id).filter(Task.status != "done").order_by(Task.due_date.asc().nulls_last(), Task.created_at.desc()).limit(5).all()
    recent_notes = Note.query.filter_by(user_id=user_id).order_by(Note.updated_at.desc()).limit(4).all()
    recent_calcs = Calculation.query.filter_by(user_id=user_id).order_by(Calculation.created_at.desc()).limit(4).all()
    recent_api_tests = ApiRequest.query.filter_by(user_id=user_id).order_by(ApiRequest.created_at.desc()).limit(4).all()
    recent_files = FileJob.query.filter_by(user_id=user_id).order_by(FileJob.created_at.desc()).limit(4).all()
    short_urls_count = ShortURL.query.filter_by(user_id=user_id).count()

    return render_template(
        "index.html",
        task_stats=task_stats,
        expense_summary=expense_summary,
        recent_tasks=recent_tasks,
        recent_notes=recent_notes,
        recent_calcs=recent_calcs,
        recent_api_tests=recent_api_tests,
        recent_files=recent_files,
        short_urls_count=short_urls_count,
    )


@main_bp.route("/health")
def health():
    return jsonify({"status": "healthy", "service": "CoreClicks Commercial SaaS Hub"}), 200


@main_bp.route("/<string:short_code>", methods=["GET", "POST"])
def redirect_short_url(short_code):
    """Smart link redirection handler with password protection check."""
    reserved = (
        "login", "register", "logout", "admin", "settings", "calculator", 
        "password-security", "tasks", "notes", "api-tester", "analytics", 
        "expenses", "file-tools", "color-tools", "url-shortener", "api", 
        "static", "health", "landing", "dashboard"
    )
    if short_code in reserved:
        abort(404)

    url_obj = ShortURL.query.filter_by(short_code=short_code).first()
    if not url_obj:
        abort(404)

    if url_obj.is_expired:
        return render_template("errors/expired_link.html", url=url_obj), 410

    if url_obj.password_hash:
        if request.method == "POST":
            pwd = request.form.get("password", "")
            if url_obj.check_password(pwd):
                url_obj.increment_clicks()
                return redirect(url_obj.original_url)
            return render_template("auth/link_password.html", url=url_obj, error="Incorrect password."), 401
        return render_template("auth/link_password.html", url=url_obj)

    url_obj.increment_clicks()
    return redirect(url_obj.original_url)
