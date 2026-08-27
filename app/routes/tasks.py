from datetime import datetime
from flask import Blueprint, jsonify, render_template, request
from flask_login import current_user, login_required
from app.extensions import db
from app.models.task import Task
from app.services.task_service import (
    get_kanban_columns,
    get_task_statistics,
    get_user_tasks,
    update_task_position,
)
from app.services.auth_service import log_activity
from app.services.notification_service import send_notification
from app.utils.decorators import api_or_login_required

tasks_bp = Blueprint("tasks", __name__)


@tasks_bp.route("/tasks")
@login_required
def view():
    stats = get_task_statistics(current_user.id)
    return render_template("tools/tasks.html", stats=stats)


@tasks_bp.route("/api/v1/tasks", methods=["GET"])
@api_or_login_required
def get_tasks():
    user_id = current_user.id
    status = request.args.get("status")
    priority = request.args.get("priority")
    category = request.args.get("category")
    search = request.args.get("search")

    tasks = get_user_tasks(user_id, status=status, priority=priority, category=category, search=search)
    return jsonify([t.to_dict() for t in tasks])


@tasks_bp.route("/api/v1/tasks/kanban", methods=["GET"])
@api_or_login_required
def get_kanban():
    user_id = current_user.id
    columns = get_kanban_columns(user_id)
    return jsonify(columns)


@tasks_bp.route("/api/v1/tasks", methods=["POST"])
@api_or_login_required
def create_task():
    user_id = current_user.id
    data = request.get_json(silent=True) or {}
    title = data.get("title", "").strip()

    if not title:
        return jsonify({"status": "error", "message": "Task title is required."}), 400

    description = data.get("description", "").strip()
    status = data.get("status", "todo")
    priority = data.get("priority", "medium")
    category = data.get("category", "General").strip() or "General"
    due_date_str = data.get("due_date")

    due_date = None
    if due_date_str:
        try:
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        except ValueError:
            pass

    task = Task(
        user_id=user_id,
        title=title,
        description=description,
        status=status,
        priority=priority,
        category=category,
        due_date=due_date,
    )

    try:
        db.session.add(task)
        db.session.commit()
        log_activity(user_id, "created_task", "tasks", f"Created task: {title}")

        if priority == "high":
            send_notification(user_id, "High Priority Task Created", f"Task '{title}' has been added with high priority.", "warning", "/tasks")

        return jsonify({"status": "success", "task": task.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500


@tasks_bp.route("/api/v1/tasks/<int:task_id>", methods=["PUT", "PATCH"])
@api_or_login_required
def update_task(task_id):
    user_id = current_user.id
    task = Task.query.filter_by(id=task_id, user_id=user_id).first_or_404()
    data = request.get_json(silent=True) or {}

    if "title" in data:
        task.title = data["title"].strip() or task.title
    if "description" in data:
        task.description = data["description"].strip()
    if "status" in data:
        task.status = data["status"]
    if "priority" in data:
        task.priority = data["priority"]
    if "category" in data:
        task.category = data["category"].strip() or "General"
    if "due_date" in data:
        try:
            task.due_date = datetime.strptime(data["due_date"], "%Y-%m-%d").date() if data["due_date"] else None
        except ValueError:
            pass

    try:
        db.session.commit()
        return jsonify({"status": "success", "task": task.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500


@tasks_bp.route("/api/v1/tasks/<int:task_id>/position", methods=["PUT"])
@api_or_login_required
def update_position(task_id):
    user_id = current_user.id
    data = request.get_json(silent=True) or {}
    new_status = data.get("status", "todo")
    new_pos = int(data.get("position", 0))

    task = update_task_position(task_id, user_id, new_status, new_pos)
    if not task:
        return jsonify({"status": "error", "message": "Task not found."}), 404

    return jsonify({"status": "success", "task": task.to_dict()})


@tasks_bp.route("/api/v1/tasks/<int:task_id>", methods=["DELETE"])
@api_or_login_required
def delete_task(task_id):
    user_id = current_user.id
    task = Task.query.filter_by(id=task_id, user_id=user_id).first_or_404()
    db.session.delete(task)
    db.session.commit()
    return jsonify({"status": "success", "message": "Task deleted."})


@tasks_bp.route("/api/v1/tasks/statistics", methods=["GET"])
@api_or_login_required
def statistics():
    stats = get_task_statistics(current_user.id)
    return jsonify(stats)
