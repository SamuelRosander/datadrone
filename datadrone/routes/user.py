from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from datadrone.forms import RegistrationForm, RequestResetForm, \
    ResetPasswordForm, UpdateAccountForm
from datadrone.extensions import bcrypt, db, send_reset_email
from datadrone.models import User

bp = Blueprint("user", __name__, url_prefix="/user")


@bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode("utf-8")
        user = User(
            email=form.email.data.lower(), password=hashed_password,
            local_login=True)
        db.session.add(user)
        db.session.commit()
        flash("Account created.", "success")
        return redirect(url_for("auth.login"))
    return render_template("register.html", form=form)


@bp.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        send_reset_email(user)
        flash(
            f"A password reset request has been sent to {user.email}.",
            "message")
        return redirect(url_for("auth.login"))

    return render_template("reset_request.html", form=form)


@bp.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    user = User.verify_reset_token(token)
    if not user:
        flash("Invalid or expired token.", "error")
        return redirect(url_for("user.reset_request"))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode("utf-8")
        user.password = hashed_password
        user.local_login = True
        db.session.commit()
        flash(f"Password for {user.email} has been updated.", "message")
        return redirect(url_for("auth.login"))

    return render_template("reset_token.html", form=form, user=user)


@bp.route("/account", methods=["GET", "POST"])
@login_required
def account():
    form = UpdateAccountForm()

    if form.validate_on_submit():
        if form.password.data:
            current_user.password = bcrypt.generate_password_hash(
                form.password.data).decode("utf-8")
        db.session.commit()
        flash("Account has been updated.", "success")
        return redirect(url_for("user.account"))
    else:
        form.email.data = current_user.email
    return render_template("account.html", form=form)
