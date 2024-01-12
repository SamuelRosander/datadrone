from flask import render_template, url_for, flash, redirect, request, abort
from .extensions import db, bcrypt, mail
from .forms import RegistrationForm, LoginForm, UpdateAccountForm, \
    AddItemForm, AddEntryForm, UpdateEntryForm, DetailsSearchScopeForm, \
    EditItemForm, AddTagForm, RequestResetForm, ResetPasswordForm, \
    EditTagForm, AddLocationForm, EditLocationForm
from .models import User, Item, Entry, Tag, EntryTag, Location
import datadrone.stats as stats
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
import datetime
from flask_csv import send_csv
from os import environ


def create_routes(app):
    @app.route("/")
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
            return redirect(url_for("login"))

    @app.route("/register", methods=["GET", "POST"])
    def register():
        form = RegistrationForm()
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(
                form.password.data).decode("utf-8")
            user = User(username=form.username.data,
                        email=form.email.data.lower(),
                        password=hashed_password,
                        register_date=datetime.datetime.utcnow())
            db.session.add(user)
            db.session.commit()
            flash("Account created.", "info")
            return redirect(url_for("login"))
        return render_template("register.html", form=form)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data.lower()).first()
            if user and bcrypt.check_password_hash(
                    user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                next_page = request.args.get("next")
                return redirect(next_page) if next_page else redirect(
                    url_for("index"))
            else:
                flash("Incorrect email or password.", "error")
        return render_template("login.html", form=form)

    @app.route("/logout")
    def logout():
        logout_user()
        return redirect(url_for("login"))

    @app.route("/reset_password", methods=["GET", "POST"])
    def reset_request():
        form = RequestResetForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data.lower()).first()
            send_reset_email(user)
            flash(
                f"A password reset request has been sent to {user.email}.",
                "info")
            return redirect(url_for("login"))

        return render_template("reset_request.html", form=form)

    @app.route("/reset_password/<token>", methods=["GET", "POST"])
    def reset_token(token):
        user = User.verify_reset_token(token)
        if not user:
            flash("Invalid or expired token.", "warning")
            return redirect(url_for("reset_request"))

        form = ResetPasswordForm()
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(
                form.password.data).decode("utf-8")
            user.password = hashed_password
            db.session.commit()
            flash(f"Password for {user.username} has been updated.", "info")
            return redirect(url_for("login"))

        return render_template("reset_token.html", form=form, user=user)

    @app.route("/account", methods=["GET", "POST"])
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
            return redirect(url_for("account"))
        elif request.method == "GET":
            form.username.data = current_user.username
            form.email.data = current_user.email
        return render_template("account.html", form=form)

    @app.route("/details/<int:item_id>", methods=["GET", "POST"])
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

        MAP_KEY = environ.get('DD_GOOGLEMAPS_KEY')

        return render_template(
            "details.html", item=item, entries=entries_list, stats=all_stats,
            form=form, days=days, map_key=MAP_KEY)

    @app.route("/item/add", methods=["POST"])
    @login_required
    def item_add():
        form = AddItemForm()
        if form.validate_on_submit():
            item = Item(user_id=current_user.user_id,
                        itemname=form.itemname.data)
            db.session.add(item)
            db.session.commit()
        return redirect(url_for("index"))

    @app.route("/item/<int:item_id>/addentry", methods=["POST"])
    @login_required
    def item_addentry(item_id):
        item = Item.query.get_or_404(item_id)
        form = AddEntryForm()

        if item.owner != current_user:
            abort(403)

        if form.geo.data:
            entry = Entry(
                item_id=item_id, latitude=form.latitude.data,
                longitude=form.longitude.data, timestamp=form.timestamp.data,
                utc_timestamp=datetime.datetime.utcnow(),
                deleted=False)
            item.geo_default = True
        else:
            entry = Entry(
                item_id=item_id, timestamp=form.timestamp.data,
                utc_timestamp=datetime.datetime.utcnow(),
                deleted=False)
            item.geo_default = False

        db.session.add(entry)
        db.session.add(item)
        db.session.commit()

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
        flash("Entry added!", "info")
        return redirect(url_for("entry", entry_id=entry.entry_id))

    @app.route("/item/<int:item_id>/addtag", methods=["POST"])
    @login_required
    def item_addtag(item_id):
        item = Item.query.get_or_404(item_id)
        if item.owner != current_user:
            abort(403)

        tag_form = AddTagForm()

        if tag_form.validate_on_submit():
            tag = Tag(item_id=item_id, name=tag_form.tagname.data)
            db.session.add(tag)
            db.session.commit()
            flash("Tag has been added.", "info")
        else:
            flash("Tags needs to be between 1 and 32 characters long.",
                  "error")

        return redirect(url_for("item_edit", item_id=item.item_id))

    @app.route("/tag/edit/<int:tag_id>", methods=["POST"])
    @login_required
    def item_edittag(tag_id):
        tag = Tag.query.get_or_404(tag_id)
        form = EditTagForm()

        if tag.item.owner != current_user:
            abort(403)

        if form.validate_on_submit():
            tag.name = form.tagname.data
            tag.hidden = form.hidden.data
            tag.archived = form.archived.data
            db.session.commit()
            flash("Tag has been updated!", "info")

        return redirect(url_for("item_edit", item_id=tag.item.item_id))

    @app.route("/item/<int:item_id>/edit", methods=["GET", "POST"])
    @login_required
    def item_edit(item_id):
        item = Item.query.get_or_404(item_id)
        if item.owner != current_user:
            abort(403)

        form = EditItemForm()
        add_tag_form = AddTagForm()
        edit_tag_form = EditTagForm()

        if form.validate_on_submit():
            item.itemname = form.itemname.data
            db.session.commit()
            flash("Item has been updated!", "info")
            return redirect(url_for("details", item_id=item.item_id))
        elif request.method == "GET":
            form.itemname.data = item.itemname

        return render_template(
            "item_edit.html", item=item, form=form, add_tag_form=add_tag_form,
            edit_tag_form=edit_tag_form)

    @app.route("/item/<int:item_id>/delete")
    @login_required
    def item_delete(item_id):
        item = Item.query.get_or_404(item_id)
        if item.owner != current_user:
            abort(403)
        item.deleted = True
        db.session.commit()

        flash("Item has been deleted.", "info")
        return redirect(url_for("index"))

    @app.route("/item/<int:item_id>/download")
    @login_required
    def item_download(item_id):
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

    @app.route("/entry/<int:entry_id>", methods=["GET", "POST"])
    @login_required
    def entry(entry_id):
        entry = Entry.query.get_or_404(entry_id)

        if entry.item.owner != current_user:
            abort(403)

        form = UpdateEntryForm()

        if form.validate_on_submit():
            time_diff = entry.timestamp - datetime.datetime.combine(
                form.date.data, form.time.data)
            entry.timestamp = datetime.datetime.combine(
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
            flash("Entry has been updated.", "info")
        elif request.method == "GET":
            form.date.data = entry.timestamp.date()
            form.time.data = entry.timestamp.time()
            form.latitude.data = entry.latitude
            form.longitude.data = entry.longitude
            form.comment.data = entry.comment

        MAP_KEY = environ.get('DD_GOOGLEMAPS_KEY')

        locations = Location.query.filter_by(user_id=current_user.user_id)

        return render_template(
            "entry.html", entry=entry, form=form, map_key=MAP_KEY,
            locations=locations)

    @app.route("/entry/<int:entry_id>/delete")
    @login_required
    def entry_delete(entry_id):
        entry = Entry.query.get_or_404(entry_id)

        if entry.item.owner != current_user:
            abort(403)

        entry.deleted = True
        db.session.commit()

        flash("Entry has been deleted.", "info")
        return redirect(url_for("details", item_id=entry.item.item_id))

    @app.route("/tag/<int:tag_id>/delete")
    @login_required
    def tag_delete(tag_id):
        tag = Tag.query.get_or_404(tag_id)

        if tag.item.owner != current_user:
            abort(403)

        tag.deleted = True
        db.session.commit()

        flash("Tag has been deleted.", "info")
        return redirect(url_for("item_edit", item_id=tag.item.item_id))

    @app.errorhandler(403)
    def error_403(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def error_404(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def error_500(error):
        return render_template("errors/500.html"), 500

    @app.route("/locations")
    @login_required
    def locations():
        add_form = AddLocationForm()
        edit_form = EditLocationForm()

        locations = Location.query.all()

        MAP_KEY = environ.get('DD_GOOGLEMAPS_KEY')

        return render_template(
            "locations.html", add_form=add_form, edit_form=edit_form,
            map_key=MAP_KEY, locations=locations)

    @app.route("/locations/add", methods=["POST"])
    @login_required
    def locations_add():
        form = AddLocationForm()

        if form.validate_on_submit():
            location = Location(
                user_id=current_user.user_id, name=form.name.data,
                latitude=form.latitude.data, longitude=form.longitude.data)

            db.session.add(location)
            db.session.commit()

        return redirect(url_for("locations"))

    @app.route("/locations/<int:location_id>/edit", methods=["POST"])
    @login_required
    def locations_edit(location_id):
        location = Location.query.get_or_404(location_id)
        form = EditLocationForm()

        if location.owner != current_user:
            abort(403)

        if form.validate_on_submit():
            location.name = form.name.data
            location.latitude = form.latitude.data
            location.longitude = form.longitude.data
            db.session.commit()
            flash("Location has been updated!", "info")

        return redirect(url_for("locations"))

    @app.route("/locations/<int:location_id>/delete")
    def locations_delete(location_id):
        location = Location.query.get_or_404(location_id)

        if location.owner != current_user:
            abort(403)

        location.deleted = True
        db.session.commit()

        flash("Location has been deleted.", "info")
        return redirect(url_for("locations"))


def tagentry_already_exists(checked_tag_id, existing_entrytags):
    """ returns True if checked_tag_id already exists in existing_entrytags """
    for eet in existing_entrytags:
        if checked_tag_id == eet.tag.tag_id:
            return True
    return False


def convert_entries_to_list(sql):
    """ takes a sql input and converts it to a list with dict values """
    entries_list = []
    for row in sql:
        # extra query to get all entrytags for the entry
        entrytags = EntryTag.query.filter_by(entry_id=row.entry_id)
        entry = row.__dict__  # convert the result to dict
        entry["entrytags"] = entrytags  # add the entrytags to the dict
        entries_list.append(entry)
    return entries_list  # return a list with each value as a dict


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


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message(
        "DataDrone Password Reset", sender="noreply@samuelrosander.se",
        recipients=[user.email])
    msg.body = f"""To reset your password visit the following link:

{url_for("reset_token", token=token, _external=True)}
"""
    mail.send(msg)


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
