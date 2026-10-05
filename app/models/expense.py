from datetime import datetime, timezone, date
from app.extensions import db


class ExpenseTransaction(db.Model):
    __tablename__ = "expense_transactions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = db.Column(db.String(16), default="expense", nullable=False, index=True)  # 'expense' or 'income'
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(64), default="General", nullable=False, index=True)
    merchant = db.Column(db.String(128), default="", nullable=False)
    transaction_date = db.Column(db.Date, default=date.today, nullable=False, index=True)
    is_recurring = db.Column(db.Boolean, default=False, nullable=False)
    notes = db.Column(db.String(255), default="", nullable=True)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "amount": round(self.amount, 2),
            "category": self.category,
            "merchant": self.merchant,
            "transaction_date": self.transaction_date.isoformat(),
            "is_recurring": self.is_recurring,
            "notes": self.notes or "",
            "created_at": self.created_at.isoformat(),
        }


class Budget(db.Model):
    __tablename__ = "budgets"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category = db.Column(db.String(64), nullable=False)
    monthly_limit = db.Column(db.Float, nullable=False)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    def to_dict(self):
        return {
            "id": self.id,
            "category": self.category,
            "monthly_limit": round(self.monthly_limit, 2),
            "created_at": self.created_at.isoformat(),
        }
