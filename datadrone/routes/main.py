from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user
from datadrone.forms import AddItemForm, AddEntryForm
from datadrone.models import Item, Entry
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


def error(error):
    return render_template("error.html", error=error), error.code
