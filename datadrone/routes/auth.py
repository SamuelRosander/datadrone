from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user
from datetime import datetime
from datadrone.forms import RegistrationForm, LoginForm, RequestResetForm, \
    ResetPasswordForm
from datadrone.extensions import bcrypt, db, send_reset_email
from datadrone.models import User

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode("utf-8")
        user = User(username=form.username.data,
                    email=form.email.data.lower(),
                    password=hashed_password,
                    register_date=datetime.utcnow())
        db.session.add(user)
        db.session.commit()
        flash("Account created.", "info")
        return redirect(url_for("auth.login"))
    return render_template("register.html", form=form)


@bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and bcrypt.check_password_hash(
                user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(
                url_for("main.index"))
        else:
            flash("Incorrect email or password.", "error")
    return render_template("login.html", form=form)


@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@bp.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        send_reset_email(user)
        flash(
            f"A password reset request has been sent to {user.email}.",
            "info")
        return redirect(url_for("auth.login"))

    return render_template("reset_request.html", form=form)


@bp.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    user = User.verify_reset_token(token)
    if not user:
        flash("Invalid or expired token.", "warning")
        return redirect(url_for("auth.reset_request"))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode("utf-8")
        user.password = hashed_password
        db.session.commit()
        flash(f"Password for {user.username} has been updated.", "info")
        return redirect(url_for("auth.login"))

    return render_template("reset_token.html", form=form, user=user)
