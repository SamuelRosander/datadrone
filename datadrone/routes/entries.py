from flask import Blueprint, render_template, url_for, flash, redirect, \
    request, abort
from datadrone.extensions import db, cache
from datadrone.forms import UpdateEntryForm, AddEntryForm
from datadrone.models import Entry, EntryTag, Location, Item
from flask_login import current_user, login_required
from datetime import datetime
from os import environ

bp = Blueprint("entries", __name__, url_prefix="/entries")


@bp.route("/<int:entry_id>/", methods=["GET", "POST"])
@login_required
def entry(entry_id):
    entry = Entry.query.get_or_404(entry_id)

    if entry.item.owner != current_user:
        abort(403)

    form = UpdateEntryForm()

    if form.validate_on_submit():
        time_diff = entry.timestamp - datetime.combine(
            form.date.data, form.time.data)
        entry.timestamp = datetime.combine(
            form.date.data, form.time.data)
        entry.utc_timestamp = entry.utc_timestamp - time_diff
        entry.latitude = form.latitude.data
        entry.longitude = form.longitude.data
        entry.comment = form.comment.data

        checked_tags = []
        for f in request.form:
            if f[:4] == "tag-":
                checked_tags.append(int(f[4:]))

        for tag in entry.item.tags:
            if not tag.deleted:
                if tagentry_already_exists(
                        tag.tag_id, entry.entrytags):
                    if tag.tag_id not in checked_tags:
                        EntryTag.query.filter_by(
                            tag_id=tag.tag_id,
                            entry_id=entry.entry_id).delete()
                elif tag.tag_id in checked_tags:
                    entry_tag = EntryTag(
                        entry_id=entry.entry_id, tag_id=tag.tag_id)
                    db.session.add(entry_tag)

        db.session.commit()
        cache.clear()
        flash("Entry has been updated.", "success")
    elif request.method == "GET":
        form.date.data = entry.timestamp.date()
        form.time.data = entry.timestamp.time()
        form.latitude.data = entry.latitude
        form.longitude.data = entry.longitude
        form.comment.data = entry.comment

    MAP_KEY = environ.get('GOOGLEMAPS_KEY')

    locations = Location.query.filter_by(
        user_id=current_user.user_id, deleted=False)

    return render_template(
        "entry.html", entry=entry, form=form, map_key=MAP_KEY,
        locations=locations)


@bp.route("/add/<int:item_id>", methods=["POST"])
@login_required
def add(item_id):
    item = Item.query.get_or_404(item_id)
    form = AddEntryForm()

    if item.owner != current_user:
        abort(403)

    if form.geo.data:
        entry = Entry(
            item_id=item_id, latitude=form.latitude.data,
            longitude=form.longitude.data, timestamp=form.timestamp.data,
            utc_timestamp=datetime.utcnow(),
            deleted=False)
        item.geo_default = True
    else:
        entry = Entry(
            item_id=item_id, timestamp=form.timestamp.data,
            utc_timestamp=datetime.utcnow(),
            deleted=False)
        item.geo_default = False

    db.session.add(entry)
    db.session.add(item)
    db.session.commit()
    cache.clear()

    checked_tags = []
    for f in request.form:
        if f[:4] == "tag-":
            checked_tags.append(int(f[4:]))

    for tag in item.tags:
        tag.is_default = False

        if tag.tag_id in checked_tags:
            tag.is_default = True
            entry_tag = EntryTag(
                entry_id=entry.entry_id, tag_id=tag.tag_id)
            db.session.add(entry_tag)

    db.session.commit()
    flash("Entry added!", "success")
    return redirect(url_for("entries.entry", entry_id=entry.entry_id))


@bp.route("/<int:entry_id>/delete")
@login_required
def delete(entry_id):
    entry = Entry.query.get_or_404(entry_id)

    if entry.item.owner != current_user:
        abort(403)

    entry.deleted = True
    db.session.commit()
    cache.clear()

    flash("Entry has been deleted.", "warning")
    return redirect(url_for("items.details", item_id=entry.item.item_id))


def tagentry_already_exists(checked_tag_id, existing_entrytags):
    """ returns True if checked_tag_id already exists in existing_entrytags """
    for eet in existing_entrytags:
        if checked_tag_id == eet.tag.tag_id:
            return True
    return False
