from flask import Blueprint, render_template, redirect, url_for, abort, flash
from flask_login import login_required, current_user
from os import environ
from datadrone.extensions import db
from datadrone.forms import AddLocationForm, EditLocationForm
from datadrone.models import Location

bp = Blueprint("locations", __name__, url_prefix="/locations")


@bp.route("/")
@login_required
def locations():
    add_form = AddLocationForm()
    edit_form = EditLocationForm()
    locations = Location.query.all()
    MAP_KEY = environ.get('DD_GOOGLEMAPS_KEY')

    return render_template(
        "locations.html", add_form=add_form, edit_form=edit_form,
        map_key=MAP_KEY, locations=locations)


@bp.route("/add", methods=["POST"])
@login_required
def add():
    form = AddLocationForm()

    if form.validate_on_submit():
        location = Location(
            user_id=current_user.user_id, name=form.name.data,
            latitude=form.latitude.data, longitude=form.longitude.data)

        db.session.add(location)
        db.session.commit()
    else:
        flash(form.name.errors[0], "error")

    return redirect(url_for("locations.locations"))


@bp.route("/<int:location_id>/edit", methods=["POST"])
@login_required
def edit(location_id):
    location = Location.query.get_or_404(location_id)
    form = EditLocationForm()

    if location.owner != current_user:
        abort(403)

    if form.validate_on_submit():
        location.name = form.name.data
        location.latitude = form.latitude.data
        location.longitude = form.longitude.data
        db.session.commit()
        flash("Location has been updated!", "success")

    return redirect(url_for("locations.locations"))


@bp.route("/<int:location_id>/delete")
def delete(location_id):
    location = Location.query.get_or_404(location_id)

    if location.owner != current_user:
        abort(403)

    location.deleted = True
    db.session.commit()

    flash("Location has been deleted.", "warning")
    return redirect(url_for("locations.locations"))
