from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from datadrone.forms import AddItemForm, AddEntryForm, UpdateAccountForm
from datadrone.models import Item, Entry
from datadrone.extensions import bcrypt, db
import datadrone.stats as stats

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    if current_user.is_authenticated:
        item_form = AddItemForm()
        entry_form = AddEntryForm()
        items = Item.query.filter_by(
            user_id=current_user.user_id, deleted=False).order_by(
            Item.item_id)
        spotlight_stat = {}
        for item in items:
            latest_entry = Entry.query.filter_by(
                item_id=item.item_id, deleted=False).order_by(
                Entry.timestamp.desc()).first()
            if latest_entry:
                spotlight_stat[item.item_id] = stats.get_time_since_last(
                    latest_entry)
            else:
                spotlight_stat[item.item_id] = "-"
        return render_template(
            "list.html", items=items, item_form=item_form,
            entry_form=entry_form, spotlight_stat=spotlight_stat)
    else:
        return redirect(url_for("auth.login"))


@bp.route("/account", methods=["GET", "POST"])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data.lower()
        if form.password.data:
            current_user.password = bcrypt.generate_password_hash(
                form.password.data).decode("utf-8")
        db.session.commit()
        flash("Account has been updated.", "info")
        return redirect(url_for("main.account"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template("account.html", form=form)


def error_403(error):
    return render_template("errors/403.html"), 403


def error_404(error):
    return render_template("errors/404.html"), 404


def error_500(error):
    return render_template("errors/500.html"), 500
