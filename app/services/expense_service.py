import io
import csv
from datetime import date, datetime, timezone
from typing import Any, Dict, List
from sqlalchemy import extract, func
from app.extensions import db
from app.models.expense import Budget, ExpenseTransaction


def get_monthly_expense_summary(user_id: int, year: int = None, month: int = None) -> Dict[str, Any]:
    """Computes monthly income, expenses, net cash flow, and budget comparisons."""
    today = date.today()
    if year is None:
        year = today.year
    if month is None:
        month = today.month

    # Get transactions for month
    txs = ExpenseTransaction.query.filter(
        ExpenseTransaction.user_id == user_id,
        extract("year", ExpenseTransaction.transaction_date) == year,
        extract("month", ExpenseTransaction.transaction_date) == month,
    ).all()

    total_income = sum(t.amount for t in txs if t.type == "income")
    total_expense = sum(t.amount for t in txs if t.type == "expense")
    net_savings = total_income - total_expense
    savings_rate = round((net_savings / total_income * 100), 1) if total_income > 0 else 0.0

    # Category breakdown
    category_totals: Dict[str, float] = {}
    for t in txs:
        if t.type == "expense":
            category_totals[t.category] = category_totals.get(t.category, 0.0) + t.amount

    # Budgets comparison
    budgets = Budget.query.filter_by(user_id=user_id).all()
    budget_status = []
    total_budget_limit = 0.0

    for b in budgets:
        spent = category_totals.get(b.category, 0.0)
        pct = round((spent / b.monthly_limit * 100), 1) if b.monthly_limit > 0 else 0.0
        total_budget_limit += b.monthly_limit
        budget_status.append({
            "category": b.category,
            "limit": b.monthly_limit,
            "spent": round(spent, 2),
            "remaining": round(b.monthly_limit - spent, 2),
            "percentage": min(100.0, pct),
            "is_exceeded": spent > b.monthly_limit,
        })

    # 6-Month Cash Flow Trend
    trend_labels = []
    income_trend = []
    expense_trend = []

    for i in range(5, -1, -1):
        target_month = (month - i - 1) % 12 + 1
        target_year = year if month - i > 0 else year - 1
        m_name = datetime(target_year, target_month, 1).strftime("%b %y")
        trend_labels.append(m_name)

        m_txs = ExpenseTransaction.query.filter(
            ExpenseTransaction.user_id == user_id,
            extract("year", ExpenseTransaction.transaction_date) == target_year,
            extract("month", ExpenseTransaction.transaction_date) == target_month,
        ).all()

        income_trend.append(sum(t.amount for t in m_txs if t.type == "income"))
        expense_trend.append(sum(t.amount for t in m_txs if t.type == "expense"))

    return {
        "period": {"year": year, "month": month, "month_name": datetime(year, month, 1).strftime("%B %Y")},
        "total_income": round(total_income, 2),
        "total_expense": round(total_expense, 2),
        "net_savings": round(net_savings, 2),
        "savings_rate": savings_rate,
        "total_budget_limit": round(total_budget_limit, 2),
        "category_breakdown": {k: round(v, 2) for k, v in category_totals.items()},
        "budgets": budget_status,
        "cash_flow_trend": {
            "labels": trend_labels,
            "income": income_trend,
            "expenses": expense_trend,
        },
    }


def export_expenses_to_csv(user_id: int) -> str:
    """Generates CSV text representation of all user transactions."""
    txs = ExpenseTransaction.query.filter_by(user_id=user_id).order_by(ExpenseTransaction.transaction_date.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Date", "Type", "Amount", "Category", "Merchant", "Is Recurring", "Notes"])

    for t in txs:
        writer.writerow([t.id, t.transaction_date.isoformat(), t.type, t.amount, t.category, t.merchant, t.is_recurring, t.notes])

    return output.getvalue()
