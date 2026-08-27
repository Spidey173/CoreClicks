from datetime import date, datetime
from flask import Blueprint, Response, jsonify, render_template, request
from flask_login import current_user, login_required
from app.extensions import db
from app.models.expense import Budget, ExpenseTransaction
from app.services.expense_service import export_expenses_to_csv, get_monthly_expense_summary
from app.services.auth_service import log_activity
from app.services.notification_service import send_notification
from app.utils.decorators import api_or_login_required

expenses_bp = Blueprint("expenses", __name__)


@expenses_bp.route("/expenses")
@login_required
def view():
    return render_template("tools/expenses.html")


@expenses_bp.route("/api/v1/expenses/summary", methods=["GET"])
@api_or_login_required
def summary():
    user_id = current_user.id
    year = request.args.get("year", type=int)
    month = request.args.get("month", type=int)
    res = get_monthly_expense_summary(user_id, year=year, month=month)
    return jsonify(res)


@expenses_bp.route("/api/v1/expenses/transactions", methods=["GET", "POST"])
@api_or_login_required
def transactions():
    user_id = current_user.id
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        tx_type = data.get("type", "expense")
        amount = float(data.get("amount", 0))
        category = data.get("category", "General").strip() or "General"
        merchant = data.get("merchant", "").strip()
        date_str = data.get("date")
        is_recurring = bool(data.get("is_recurring", False))
        notes = data.get("notes", "").strip()

        if amount <= 0:
            return jsonify({"status": "error", "message": "Amount must be greater than 0."}), 400

        tx_date = date.today()
        if date_str:
            try:
                tx_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                pass

        tx = ExpenseTransaction(
            user_id=user_id,
            type=tx_type,
            amount=amount,
            category=category,
            merchant=merchant,
            transaction_date=tx_date,
            is_recurring=is_recurring,
            notes=notes,
        )

        try:
            db.session.add(tx)
            db.session.commit()
            log_activity(user_id, "logged_transaction", "expenses", f"Logged {tx_type}: ${amount:.2f} ({category})")

            # Check budget threshold
            if tx_type == "expense":
                budget = Budget.query.filter_by(user_id=user_id, category=category).first()
                if budget:
                    total_spent = sum(t.amount for t in ExpenseTransaction.query.filter_by(user_id=user_id, category=category, type="expense").all())
                    if total_spent > budget.monthly_limit:
                        send_notification(user_id, "Budget Exceeded!", f"You have exceeded your ${budget.monthly_limit:.0f} budget for {category} (Total: ${total_spent:.2f}).", "danger", "/expenses")

            return jsonify({"status": "success", "transaction": tx.to_dict()}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"status": "error", "message": str(e)}), 500

    txs = ExpenseTransaction.query.filter_by(user_id=user_id).order_by(ExpenseTransaction.transaction_date.desc()).limit(50).all()
    return jsonify([t.to_dict() for t in txs])


@expenses_bp.route("/api/v1/expenses/transactions/<int:tx_id>", methods=["DELETE"])
@api_or_login_required
def delete_transaction(tx_id):
    user_id = current_user.id
    tx = ExpenseTransaction.query.filter_by(id=tx_id, user_id=user_id).first_or_404()
    db.session.delete(tx)
    db.session.commit()
    return jsonify({"status": "success", "message": "Transaction deleted."})


@expenses_bp.route("/api/v1/expenses/budgets", methods=["GET", "POST"])
@api_or_login_required
def budgets():
    user_id = current_user.id
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        category = data.get("category", "").strip()
        limit = float(data.get("limit", 0))

        if not category or limit <= 0:
            return jsonify({"status": "error", "message": "Valid category and limit are required."}), 400

        budget = Budget.query.filter_by(user_id=user_id, category=category).first()
        if budget:
            budget.monthly_limit = limit
        else:
            budget = Budget(user_id=user_id, category=category, monthly_limit=limit)
            db.session.add(budget)

        db.session.commit()
        return jsonify({"status": "success", "budget": budget.to_dict()}), 201

    all_budgets = Budget.query.filter_by(user_id=user_id).all()
    return jsonify([b.to_dict() for b in all_budgets])


@expenses_bp.route("/api/v1/expenses/budgets/<int:b_id>", methods=["DELETE"])
@api_or_login_required
def delete_budget(b_id):
    user_id = current_user.id
    b = Budget.query.filter_by(id=b_id, user_id=user_id).first_or_404()
    db.session.delete(b)
    db.session.commit()
    return jsonify({"status": "success", "message": "Budget removed."})


@expenses_bp.route("/api/v1/expenses/export", methods=["GET"])
@api_or_login_required
def export_csv():
    csv_text = export_expenses_to_csv(current_user.id)
    return Response(
        csv_text,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename=expenses_{current_user.username}.csv"},
    )
