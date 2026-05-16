from datetime import datetime

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, logout_user

from auth.email_service import send_otp_email
from auth.otp_service import generate_otp, store_otp, verify_otp
from auth.password_service import hash_password, verify_password
from auth.session_manager import login_hr
from auth.validators import sanitize, validate_email, validate_otp, validate_password
from config.constants import OTP_EXPIRY_MINUTES
from database.db import db
from database.models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        company_name = sanitize(request.form.get("company_name"))
        hr_name = sanitize(request.form.get("hr_name"))
        email = sanitize(request.form.get("email")).lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        ok, password_error = validate_password(password)
        if not all([company_name, hr_name, email, password, confirm_password]):
            flash("Please complete all fields.", "error")
        elif not validate_email(email):
            flash("Enter a valid email address.", "error")
        elif password != confirm_password:
            flash("Passwords do not match.", "error")
        elif not ok:
            flash(password_error, "error")
        elif User.query.filter_by(email=email).first():
            flash("An account with this email already exists.", "error")
        else:
            user = User(company_name=company_name, hr_name=hr_name, email=email, password_hash=hash_password(password))
            db.session.add(user)
            db.session.commit()
            flash("Account created. Welcome to HireLens AI.", "success")
            login_hr(user, remember=True)
            return redirect(url_for("dashboard"))
    return render_template("register.html", title="Register")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        email = sanitize(request.form.get("email")).lower()
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember"))
        user = User.query.filter_by(email=email).first()
        if user and verify_password(password, user.password_hash):
            user.last_login = datetime.utcnow()
            db.session.commit()
            login_hr(user, remember=remember)
            flash("Logged in successfully.", "success")
            return redirect(url_for("dashboard"))
        flash("Invalid email or password.", "error")
    return render_template("login.html", title="Login")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("landing"))


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = sanitize(request.form.get("email")).lower()
        if not validate_email(email):
            flash("Enter a valid email address.", "error")
            return render_template("forgot_password.html", title="Forgot Password")
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("If that email exists, an OTP has been sent.", "success")
            return redirect(url_for("auth.verify_otp_page"))
        otp = generate_otp()
        store_otp(user, otp)
        ok, message = send_otp_email(current_app_mail(), email, otp, OTP_EXPIRY_MINUTES)
        session["reset_email"] = email
        flash(message, "success" if ok else "warning")
        return redirect(url_for("auth.verify_otp_page"))
    return render_template("forgot_password.html", title="Forgot Password")


def current_app_mail():
    return current_app.extensions["mail"]


@auth_bp.route("/verify-otp", methods=["GET", "POST"])
def verify_otp_page():
    if request.method == "POST":
        email = sanitize(request.form.get("email") or session.get("reset_email", "")).lower()
        otp = sanitize(request.form.get("otp"))
        if not validate_email(email) or not validate_otp(otp):
            flash("Enter your email and a valid 6-digit OTP.", "error")
        else:
            ok, message = verify_otp(email, otp)
            flash(message, "success" if ok else "error")
            if ok:
                session["otp_verified_email"] = email
                return redirect(url_for("auth.reset_password"))
    return render_template("verify_otp.html", title="Verify OTP", email=session.get("reset_email", ""))


@auth_bp.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    email = session.get("otp_verified_email")
    if not email:
        flash("Verify your OTP before resetting password.", "error")
        return redirect(url_for("auth.forgot_password"))
    if request.method == "POST":
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        ok, password_error = validate_password(password)
        if password != confirm_password:
            flash("Passwords do not match.", "error")
        elif not ok:
            flash(password_error, "error")
        else:
            user = User.query.filter_by(email=email).first()
            user.password_hash = hash_password(password)
            db.session.commit()
            session.pop("otp_verified_email", None)
            session.pop("reset_email", None)
            flash("Password reset successfully. Please log in.", "success")
            return redirect(url_for("auth.login"))
    return render_template("reset_password.html", title="Reset Password")
