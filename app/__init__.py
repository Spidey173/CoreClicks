import os
from datetime import date, datetime, timezone
from flask import Flask, jsonify, render_template
from app.config import config_by_name
from app.extensions import bcrypt, db, login_manager
from app.models.user import User, UserSettings
from app.models.task import Task
from app.models.note import Note
from app.models.expense import Budget, ExpenseTransaction
from app.models.calculation import Calculation
from app.models.short_url import ShortURL
from app.models.color_palette import ColorPalette


def create_app(config_name: str = "development") -> Flask:
    """Application factory for CoreClicks Commercial SaaS Hub."""
    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name["development"]))

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Register Blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.admin import admin_bp
    from app.routes.calculator import calculator_bp
    from app.routes.password import password_bp
    from app.routes.tasks import tasks_bp
    from app.routes.notes import notes_bp
    from app.routes.api_tester import api_tester_bp
    from app.routes.analytics import analytics_bp
    from app.routes.expenses import expenses_bp
    from app.routes.file_tools import file_tools_bp
    from app.routes.color_tools import color_tools_bp
    from app.routes.url_shortener import url_shortener_bp
    from app.routes.api.search import search_api_bp
    from app.routes.api.notifications import notifications_api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(calculator_bp)
    app.register_blueprint(password_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(notes_bp)
    app.register_blueprint(api_tester_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(file_tools_bp)
    app.register_blueprint(color_tools_bp)
    app.register_blueprint(url_shortener_bp)
    app.register_blueprint(search_api_bp)
    app.register_blueprint(notifications_api_bp)

    # Security Headers
    @app.after_request
    def set_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

    # Error Handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template("errors/500.html"), 500

    # Ensure Uploads Directory
    os.makedirs(app.config.get("UPLOAD_FOLDER", "uploads"), exist_ok=True)

    # Seed Database & Default Demo Users
    with app.app_context():
        db.create_all()
        seed_demo_data()

    return app


def seed_demo_data():
    """Seeds default admin and demo user accounts with initial sample data."""
    if User.query.filter_by(email="admin@coreclicks.dev").first():
        return

    # 1. Admin User
    admin = User(email="admin@coreclicks.dev", username="admin", role="admin")
    admin.set_password("Admin@12345")
    admin_settings = UserSettings(user=admin, theme="dark", timezone="UTC", language="en")
    db.session.add(admin)
    db.session.add(admin_settings)
    db.session.flush()

    # 2. Demo Standard User
    demo_user = User(email="user@coreclicks.dev", username="demouser", role="user")
    demo_user.set_password("User@12345")
    demo_settings = UserSettings(user=demo_user, theme="dark", timezone="UTC", language="en")
    db.session.add(demo_user)
    db.session.add(demo_settings)
    db.session.flush()

    # Seed sample tasks for admin & user
    for uid in (admin.id, demo_user.id):
        sample_tasks = [
            Task(user_id=uid, title="Deploy CoreClicks SaaS to Cloud", description="Verify Gunicorn WSGI and PostgreSQL connection.", status="in_progress", priority="high", category="DevOps", due_date=date.today()),
            Task(user_id=uid, title="Run automated security vulnerability scan", description="Inspect headers and input sanitization.", status="todo", priority="high", category="Security", due_date=date.today()),
            Task(user_id=uid, title="Review monthly financial budgets", description="Analyze category variances in expense tracker.", status="todo", priority="medium", category="Finance"),
            Task(user_id=uid, title="Design WCAG 2.1 AAA accessible theme", description="Export brand palette to Tailwind config.", status="done", priority="low", category="Design"),
        ]
        db.session.add_all(sample_tasks)

        # Sample Notes
        sample_note = Note(
            user_id=uid,
            title="CoreClicks Product Architecture",
            content="# CoreClicks 2.0\n\nCommercial-grade SaaS Utility Hub powered by Flask, SQLAlchemy, Pandas, and Chart.js.\n\n### Included 10 Tools:\n- **Safe Calculator**\n- **Password Auditor**\n- **Task Manager (Kanban)**\n- **Notes & Markdown**\n- **REST API Tester**\n- **CSV Analytics Studio**\n- **Expense Tracker**\n- **File Converter Studio**\n- **Color Palette & WCAG**\n- **URL Shortener & QR**",
            folder="Engineering",
            is_pinned=True,
        )
        sample_note.tags = ["SaaS", "Architecture", "Python"]
        db.session.add(sample_note)

        # Sample Expenses
        sample_expenses = [
            ExpenseTransaction(user_id=uid, type="income", amount=4500.0, category="Salary", merchant="Stripe Payout", transaction_date=date.today()),
            ExpenseTransaction(user_id=uid, type="expense", amount=120.0, category="Cloud Hosting", merchant="AWS Infrastructure", transaction_date=date.today()),
            ExpenseTransaction(user_id=uid, type="expense", amount=45.0, category="SaaS Subscriptions", merchant="GitHub Enterprise", transaction_date=date.today()),
            ExpenseTransaction(user_id=uid, type="expense", amount=65.0, category="Office & Hardware", merchant="Logitech", transaction_date=date.today()),
        ]
        db.session.add_all(sample_expenses)

        # Sample Budgets
        sample_budgets = [
            Budget(user_id=uid, category="Cloud Hosting", monthly_limit=250.0),
            Budget(user_id=uid, category="SaaS Subscriptions", monthly_limit=100.0),
            Budget(user_id=uid, category="Office & Hardware", monthly_limit=200.0),
        ]
        db.session.add_all(sample_budgets)

        # Sample Calculations
        sample_calcs = [
            Calculation(user_id=uid, expression="sqrt(1024) * 8", result="256", mode="scientific"),
            Calculation(user_id=uid, expression="factorial(5) + 42", result="162", mode="scientific"),
        ]
        db.session.add_all(sample_calcs)

        # Sample Short URL
        sample_url = ShortURL(
            user_id=uid,
            original_url="https://github.com/Spidey173/tyytyyt",
            short_code="repo" if uid == admin.id else "coreclicks",
            title="CoreClicks Repository",
            clicks=12,
        )
        db.session.add(sample_url)

        # Sample Color Palette
        sample_palette = ColorPalette(
            user_id=uid,
            name="Vibrant Indigo",
            harmony_type="Complementary",
            is_favorite=True,
        )
        sample_palette.colors = ["#4f46e5", "#6366f1", "#f59e0b", "#fbbf24", "#10b981"]
        db.session.add(sample_palette)

    db.session.commit()
