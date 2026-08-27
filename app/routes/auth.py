from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from app.extensions import db
from app.services.auth_service import authenticate_user, log_activity, register_user

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip()
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember"))

        user = authenticate_user(identifier, password)
        if user:
            login_user(user, remember=remember)
            log_activity(user.id, "login", "auth", f"User logged in from {request.remote_addr}", request.remote_addr)
            flash(f"Welcome back, {user.username}!", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("main.dashboard"))

        flash("Invalid email/username or password.", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if password != confirm:
            flash("Passwords do not match.", "warning")
            return render_template("auth/register.html")

        user, err = register_user(email, username, password)
        if user:
            login_user(user)
            flash("Account registered successfully! Welcome to CoreClicks.", "success")
            return redirect(url_for("main.dashboard"))

        flash(err or "Registration failed. Please check your details.", "danger")

    return render_template("auth/register.html")


@auth_bp.route("/logout")
@login_required
def logout():
    log_activity(current_user.id, "logout", "auth", "User logged out.")
    logout_user()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("auth.login"))
