from flask import Blueprint, render_template, url_for, flash, redirect, \
    request, abort
from datadrone.extensions import db, cache
from datadrone.forms import AddItemForm, DetailsSearchScopeForm, \
    EditItemForm, AddTagForm, EditTagForm
from datadrone.models import Item, Entry, Tag, EntryTag
import datadrone.stats as stats
from flask_login import current_user, login_required
import datetime
from flask_csv import send_csv
from os import environ

bp = Blueprint("items", __name__, url_prefix="/items")


@bp.route("/<int:item_id>/", methods=["GET", "POST"])
@cache.cached(query_string=True)
@login_required
def details(item_id):
    item = Item.query.get_or_404(item_id)

    if item.owner != current_user:
        abort(403)

    days = 90
    if request.args.get('days'):
        if request.args.get('days') == "all":
            days = "all"
        else:
            days = int(request.args.get('days'))

    form = DetailsSearchScopeForm()

    if form.validate_on_submit():
        entries = Entry.query.filter(
            Entry.item_id == item_id, Entry.deleted.is_(False),
            Entry.timestamp >= form.scope_from.data,
            Entry.timestamp <= form.scope_to.data +
            datetime.timedelta(days=1)).order_by(
            Entry.timestamp)
        entries_list = convert_entries_to_list(entries)
        filter_entry_list(entries_list, form)
        all_stats = stats.get_all(
            entries_list, form.scope_from.data, form.scope_to.data)
    elif days == "all":
        entries = Entry.query.filter_by(
            item_id=item_id, deleted=False).order_by(
            Entry.timestamp)
        entries_list = convert_entries_to_list(entries)
        filter_entry_list(entries_list, form)
        all_stats = stats.get_all(entries_list)
    else:
        now = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        scope_from = (now - datetime.timedelta(days=days)).date()
        entries = Entry.query.filter(
            Entry.item_id == item_id, Entry.deleted.is_(False),
            Entry.timestamp >= scope_from).order_by(Entry.timestamp)
        entries_list = convert_entries_to_list(entries)
        filter_entry_list(entries_list, form)
        all_stats = stats.get_all(
            entries_list, scope_from=scope_from, days=days)

    MAP_KEY = environ.get('GOOGLEMAPS_KEY')

    return render_template(
        "details.html", item=item, entries=entries_list, stats=all_stats,
        form=form, days=days, map_key=MAP_KEY)


@bp.route("/add", methods=["POST"])
@login_required
def add():
    form = AddItemForm()
    if form.validate_on_submit():
        item = Item(user_id=current_user.user_id,
                    itemname=form.itemname.data)
        db.session.add(item)
        db.session.commit()
    return redirect(url_for("main.index"))


@bp.route("/<int:item_id>/edit", methods=["GET", "POST"])
@login_required
def edit(item_id):
    item = Item.query.get_or_404(item_id)
    if item.owner != current_user:
        abort(403)

    form = EditItemForm()
    add_tag_form = AddTagForm()
    edit_tag_form = EditTagForm()

    if form.validate_on_submit():
        item.itemname = form.itemname.data
        db.session.commit()
        flash("Item has been updated!", "success")
        return redirect(url_for("items.details", item_id=item.item_id))
    elif request.method == "GET":
        form.itemname.data = item.itemname

    return render_template(
        "item_edit.html", item=item, form=form, add_tag_form=add_tag_form,
        edit_tag_form=edit_tag_form)


@bp.route("/<int:item_id>/delete")
@login_required
def delete(item_id):
    item = Item.query.get_or_404(item_id)
    if item.owner != current_user:
        abort(403)
    item.deleted = True
    db.session.commit()

    flash("Item has been deleted.", "warning")
    return redirect(url_for("main.index"))


@bp.route("/<int:item_id>/download")
@login_required
def download(item_id):
    item = Item.query.get_or_404(item_id)
    if item.owner != current_user:
        abort(403)

    entries = Entry.query.filter_by(
        item_id=item_id, deleted=False).order_by(
        Entry.timestamp)
    entries_list = get_csv_list(entries)

    return send_csv(
        entries_list, item.itemname + ".csv",
        ["timestamp", "comment", "longitude", "latitude", "entrytags"])


def convert_entries_to_list(sql):
    """ takes a sql input and converts it to a list with dict values """
    entries_list = []
    for row in sql:
        entrytags = EntryTag.query.filter_by(entry_id=row.entry_id)
        entry = row.__dict__
        entry["entrytags"] = entrytags
        entries_list.append(entry)
    return entries_list


def get_csv_list(sql):
    """ generates a list of entries formatted for csv export """
    entries_list = []
    for row in sql:
        tags_tuple = db.session.query(
            Tag.name).outerjoin(
            EntryTag, Tag.tag_id == EntryTag.tag_id).filter_by(
            entry_id=row.entry_id).all()
        tags = [i[0] for i in tags_tuple]

        entry = row.__dict__
        entry["entrytags"] = ",".join(tags)
        del entry["_sa_instance_state"]
        del entry["utc_timestamp"]
        del entry["entry_id"]
        del entry["deleted"]
        del entry["item_id"]
        entries_list.append(entry)
    return entries_list


def filter_entry_list(all_entries, form):
    if form.filter_geo.data == "all":
        filter_geo = None
    else:
        filter_geo = form.filter_geo.data

    if form.filter_comment.data == "all":
        filter_comment = None
    else:
        filter_comment = form.filter_comment.data

    for i in range(len(all_entries)-1, -1, -1):
        removed = False
        entry = all_entries[i]

        entry_has_geo = bool(entry.get("longitude") and entry.get("latitude"))
        if filter_geo:
            if eval(filter_geo) != entry_has_geo:
                if not removed:
                    del all_entries[i]
                    removed = True

        entry_has_comment = bool(entry.get("comment"))
        if filter_comment:
            if eval(filter_comment) != entry_has_comment:
                if not removed:
                    del all_entries[i]
                    removed = True

    return all_entries
