from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from app.extensions import db
from app.models.task import Task


def get_user_tasks(
    user_id: int,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
) -> List[Task]:
    """Retrieves filtered tasks for a user."""
    query = Task.query.filter_by(user_id=user_id)

    if status and status != "all":
        query = query.filter_by(status=status)
    if priority and priority != "all":
        query = query.filter_by(priority=priority)
    if category and category != "all":
        query = query.filter_by(category=category)
    if search:
        pattern = f"%{search.strip()}%"
        query = query.filter((Task.title.ilike(pattern)) | (Task.description.ilike(pattern)))

    return query.order_by(Task.position.asc(), Task.created_at.desc()).all()


def get_kanban_columns(user_id: int) -> Dict[str, List[Dict[str, Any]]]:
    """Groups tasks into 4 Kanban columns."""
    all_tasks = Task.query.filter_by(user_id=user_id).order_by(Task.position.asc(), Task.created_at.desc()).all()

    columns = {
        "todo": [],
        "in_progress": [],
        "review": [],
        "done": [],
    }

    for t in all_tasks:
        col = t.status if t.status in columns else "todo"
        columns[col].append(t.to_dict())

    return columns


def get_task_statistics(user_id: int) -> Dict[str, Any]:
    """Computes task metrics and completion progress for dashboard."""
    total = Task.query.filter_by(user_id=user_id).count()
    done = Task.query.filter_by(user_id=user_id, status="done").count()
    in_progress = Task.query.filter_by(user_id=user_id, status="in_progress").count()
    todo = Task.query.filter_by(user_id=user_id, status="todo").count()
    high_priority = Task.query.filter_by(user_id=user_id, priority="high").filter(Task.status != "done").count()

    rate = round((done / total * 100), 1) if total > 0 else 0.0

    return {
        "total": total,
        "done": done,
        "in_progress": in_progress,
        "todo": todo,
        "high_priority": high_priority,
        "completion_rate": rate,
    }


def update_task_position(task_id: int, user_id: int, new_status: str, new_position: int) -> Optional[Task]:
    """Updates status and drag-and-drop position of a task."""
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    if not task:
        return None

    if new_status in ("todo", "in_progress", "review", "done"):
        task.status = new_status
    task.position = max(0, new_position)
    db.session.commit()
    return task
