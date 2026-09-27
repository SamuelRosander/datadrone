from flask import Blueprint, render_template, url_for, flash, redirect, \
    request, abort
from datadrone.extensions import db, cache
from datadrone.forms import AddItemForm, EditItemForm, AddTagForm, EditTagsForm
from datadrone.models import Item, Entry, Tag, EntryTag
import datadrone.stats as stats
from flask_login import current_user, login_required
from sqlalchemy import or_, and_
import datetime
from flask_csv import send_csv
from os import environ

bp = Blueprint("items", __name__, url_prefix="/items")


@bp.route("/<int:item_id>/", methods=["GET", "POST"])
@cache.cached(query_string=True, unless=lambda: current_user.is_anonymous)
@login_required
def details(item_id):
    item = Item.query.get_or_404(item_id)

    if item.owner != current_user:
        abort(403)

    # removes empty arguments from the URL
    filtered_args = {k: v for k, v in request.args.items() if v}
    if filtered_args != dict(request.args):
        return redirect(
            url_for('items.details', item_id=item_id, **filtered_args))

    edit_name_form = EditItemForm()

    entries = Entry.query.filter(
        Entry.item_id == item_id,
        Entry.deleted.is_(False))

    from_date = None
    stat_args = {}

    # default view and used in quick select days
    if not request.args.get("filter"):
        days = request.args.get('days', '90')
        days = int(days) if days.isdigit() else "all"

        now = datetime.datetime.utcnow() + datetime.timedelta(hours=1)

        if days != "all":
            from_date = (now - datetime.timedelta(days=days)).date()

        to_date = now.date()

        stat_args["scope_to"] = to_date
        stat_args["days"] = days
    # filtered view
    else:
        from_date_string = request.args.get("from")
        from_date = datetime.datetime.strptime(
            from_date_string, "%Y-%m-%d").date() if from_date_string else None

        has_geo = request.args.get("has_geo")
        if (has_geo == "true"):
            entries = entries.filter(
                Entry.latitude.isnot(None), Entry.longitude.isnot(None))
        elif (has_geo == "false"):
            entries = entries.filter(
                or_(Entry.latitude.is_(None), Entry.longitude.is_(None)))

        tags = {
            int(k.replace("tag-", "")): v for k, v in request.args.items()
            if k.startswith("tag-")}
        true_tag_ids = [tag_id for tag_id,
                        value in tags.items() if value == 'true']
        false_tag_ids = [tag_id for tag_id,
                         value in tags.items() if value == 'false']

        entries = entries.filter(
            and_(
                *[
                    Entry.entrytags.any(EntryTag.tag_id == tag_id)
                    for tag_id in true_tag_ids
                ],
                *[
                    ~Entry.entrytags.any(EntryTag.tag_id == tag_id)
                    for tag_id in false_tag_ids
                ]
            )
        )

    if from_date:
        entries = entries.filter(Entry.timestamp >= from_date)
        stat_args["scope_from"] = from_date

    if to_date_string := request.args.get("to"):
        to_date = datetime.datetime.strptime(
            to_date_string, "%Y-%m-%d").date() + datetime.timedelta(days=1)
        entries = entries.filter(Entry.timestamp <= to_date)
        stat_args["scope_to"] = to_date

    entries = entries.order_by(Entry.timestamp)
    entries_list = convert_entries_to_list(entries)

    all_stats = stats.get_all(entries_list, **stat_args)

    MAP_KEY = environ.get('GOOGLEMAPS_KEY')

    return render_template(
        "details.html", item=item, entries=entries_list, stats=all_stats,
        map_key=MAP_KEY, edit_name_form=edit_name_form)


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


@bp.route("/<int:item_id>/edit", methods=["POST"])
@login_required
def edit(item_id):
    item = Item.query.get_or_404(item_id)
    if item.owner != current_user:
        abort(403)

    form = EditItemForm()

    if form.validate_on_submit():
        item.itemname = form.itemname.data
        db.session.commit()
        cache.clear()

    return redirect(url_for("items.details", item_id=item.item_id))


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


@bp.route("/<int:item_id>/tags", methods=["GET", "POST"])
@login_required
def tags(item_id):
    item = Item.query.get_or_404(item_id)
    if item.owner != current_user:
        abort(403)

    add_tag_form = AddTagForm()
    edit_tags_form = EditTagsForm()

    if edit_tags_form.validate_on_submit():
        for form_tag in edit_tags_form.tags:
            tag = Tag.query.get_or_404(form_tag.tag_id.data)

            if tag.item.owner != current_user:
                abort(403)

            tag.name = form_tag.tagname.data
            tag.hidden = form_tag.hidden.data
            tag.archived = form_tag.archived.data

        db.session.commit()
        flash("Tags has been updated.", "success")

    elif request.method == "GET":
        active_tags = [tag for tag in item.tags if not tag.deleted]
        for _ in range(len(active_tags)):
            edit_tags_form.tags.append_entry()

            for tag, form_tag in zip(active_tags, edit_tags_form.tags):
                form_tag["tagname"].data = tag.name
                form_tag["hidden"].data = tag.hidden
                form_tag["archived"].data = tag.archived
                form_tag["tag_id"].data = tag.tag_id
    else:
        flash(edit_tags_form.errors, "error")

    return render_template(
        "item_edit.html", item=item, add_tag_form=add_tag_form,
        edit_tags_form=edit_tags_form)


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
