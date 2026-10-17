from flask import jsonify, current_app
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


@bp.route("/manifest.json")
def manifest():
    if current_app.config.get("ENVIRONMENT") == "test":
        app_name = "DataDrone (Test)"
        short_name = "DataDrone (Test)"
        theme_color = "#62c4ea"
    else:
        app_name = "DataDrone"
        short_name = "DataDrone"
        theme_color = "#62c4ea"

    return jsonify({
        "id": "/",
        "name": app_name,
        "short_name": short_name,
        "description": app_name,
        "start_url": "/",
        "scope": "/",
        "display": "standalone",
        "background_color": "#333333",
        "theme_color": theme_color,
        "icons": [
            {
                "src": "/static/img/favicon-192.png",
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "any"
            },
            {
                "src": "/static/img/favicon-512.png",
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "any"
            }
        ]
    })


def error(error):
    return render_template("error.html", error=error), error.code
