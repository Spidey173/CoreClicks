from typing import Any, Dict, List
from app.models.task import Task
from app.models.note import Note
from app.models.expense import ExpenseTransaction
from app.models.calculation import Calculation
from app.models.short_url import ShortURL
from app.models.api_request import ApiRequest


def global_omni_search(user_id: int, query: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Searches across all SaaS modules for matching records belonging to user.
    """
    query = query.strip()
    if not query or len(query) < 2:
        return {"tasks": [], "notes": [], "expenses": [], "calculations": [], "urls": [], "api_requests": []}

    search_pattern = f"%{query}%"

    # Tasks
    tasks = Task.query.filter(
        Task.user_id == user_id,
        (Task.title.ilike(search_pattern)) | (Task.description.ilike(search_pattern)) | (Task.category.ilike(search_pattern)),
    ).limit(8).all()

    # Notes
    notes = Note.query.filter(
        Note.user_id == user_id,
        (Note.title.ilike(search_pattern)) | (Note.content.ilike(search_pattern)) | (Note.folder.ilike(search_pattern)),
    ).limit(8).all()

    # Expenses
    expenses = ExpenseTransaction.query.filter(
        ExpenseTransaction.user_id == user_id,
        (ExpenseTransaction.category.ilike(search_pattern)) | (ExpenseTransaction.merchant.ilike(search_pattern)) | (ExpenseTransaction.notes.ilike(search_pattern)),
    ).limit(8).all()

    # Calculations
    calculations = Calculation.query.filter(
        Calculation.user_id == user_id,
        (Calculation.expression.ilike(search_pattern)) | (Calculation.result.ilike(search_pattern)),
    ).limit(8).all()

    # Short URLs
    urls = ShortURL.query.filter(
        ShortURL.user_id == user_id,
        (ShortURL.title.ilike(search_pattern)) | (ShortURL.short_code.ilike(search_pattern)) | (ShortURL.original_url.ilike(search_pattern)),
    ).limit(8).all()

    # API Requests
    api_requests = ApiRequest.query.filter(
        ApiRequest.user_id == user_id,
        (ApiRequest.name.ilike(search_pattern)) | (ApiRequest.url.ilike(search_pattern)) | (ApiRequest.method.ilike(search_pattern)),
    ).limit(8).all()

    return {
        "tasks": [t.to_dict() for t in tasks],
        "notes": [n.to_dict() for n in notes],
        "expenses": [e.to_dict() for e in expenses],
        "calculations": [c.to_dict() for c in calculations],
        "urls": [u.to_dict() for u in urls],
        "api_requests": [a.to_dict() for a in api_requests],
    }
