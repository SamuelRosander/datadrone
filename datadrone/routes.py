from flask import render_template, url_for, flash, redirect, request, abort
from datadrone import app, db, bcrypt
from datadrone.forms import RegistrationForm, LoginForm, UpdateAccountForm, AddItemForm, AddEntryForm, UpdateEntryForm, DetailsSearchScopeForm, EditItemForm, AddTagForm
from datadrone.models import User, Item, Entry, Tag, EntryTag
import datadrone.stats as stats
from flask_login import login_user, current_user, logout_user, login_required
import datetime

@app.route("/")
def index():
	if current_user.is_authenticated:
		item_form = AddItemForm()
		entry_form = AddEntryForm()
		items = Item.query.filter_by(user_id=current_user.user_id, deleted=False).order_by(Item.item_id)
		spotlight_stat = {}
		for item in items:
			latest_entry = Entry.query.filter_by(item_id=item.item_id, deleted=False).order_by(Entry.timestamp.desc()).first()
			if latest_entry:
				spotlight_stat[item.item_id] = stats.get_days_since_last(latest_entry)
			else:
				spotlight_stat[item.item_id] = 0
		return render_template("list.html", items=items, item_form=item_form, entry_form=entry_form, spotlight_stat=spotlight_stat)
	else:
		return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
	form = RegistrationForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
		user = User(username=form.username.data, email=form.email.data, password=hashed_password)
		db.session.add(user)
		db.session.commit()
		flash("Account created.", "info")
		return redirect(url_for("login"))
	return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember=form.remember.data)
			next_page = request.args.get("next")
			return redirect(next_page) if next_page else redirect(url_for("index"))
		else:
			flash("Incorrect username or password.", "error")
	return render_template("login.html", form=form)

@app.route("/logout")
def logout():
	logout_user()
	return redirect(url_for("login"))

@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
	form = UpdateAccountForm()
	if form.validate_on_submit():
		current_user.username = form.username.data
		current_user.email = form.email.data
		if form.password.data:
			current_user.password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
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

	form = DetailsSearchScopeForm()
	if form.validate_on_submit():
		entries = Entry.query.filter(Entry.item_id==item_id\
									,Entry.deleted == False\
									,Entry.timestamp >= form.scope_from.data\
									,Entry.timestamp <= form.scope_to.data + datetime.timedelta(days=1))\
							  .order_by(Entry.timestamp)
		all_stats = stats.get_all(entries, form.scope_from.data, form.scope_to.data)
	else:
		entries = Entry.query.filter_by(item_id=item_id, deleted=False).order_by(Entry.timestamp)
		all_stats = stats.get_all(entries)

	return render_template("details.html", item=item, entries=entries, stats=all_stats, form=form)

@app.route("/item/add", methods=["POST"])
@login_required
def item_add():
	form = AddItemForm()
	if form.validate_on_submit():
		item = Item(user_id=current_user.user_id, itemname=form.itemname.data)
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

	timestamp = (datetime.datetime.utcnow() + datetime.timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")	# hardcoded to CET
	if form.geo.data:	#if geo checkbox is checked
		entry = Entry(item_id = item_id, latitude = form.latitude.data, longitude = form.longitude.data, timestamp = timestamp)	#add entry with geo
		item.geo_default = True;	#used as a "remember" function for the geo checkbox
	else:
		entry = Entry(item_id = item_id, timestamp = timestamp)	#add entry without geo
		item.geo_default = False;

	db.session.add(entry)
	db.session.add(item)
	db.session.commit()	#needed for entry.entry_id in tag section below

	checked_tags = []
	form_data = request.form	#get all form data
	for f in form_data:
		if f[:4] == "tag-":	#if name is tag-X and it's checked (doesn't show if not checked)
			checked_tags.append(int(f[4:]))	#add it to the list of checked tags

	for tag in item.tags:	#loop through all visible tags for the item
		tag.is_default = False	#set all as default. will be changed again below if it's checked. Used for saving the "checked"-value

		if tag.tag_id in checked_tags:	#if any visible tags (taglinks) are checked
			tag.is_default = True	#the tag will now be checked per default in the future
			entry_tag = EntryTag(entry_id = entry.entry_id, tag_id = tag.tag_id)	#create an entrytag object...
			db.session.add(entry_tag)	#...and add it to the db

	db.session.commit()	#commit tag changes
	flash("Entry added!", "info")
	return redirect(url_for("entry", entry_id=entry.entry_id))

@app.route("/item/<int:item_id>/addtag", methods=["POST"])
@login_required
def item_addtag(item_id):
	item = Item.query.get_or_404(item_id)
	form = AddTagForm()

	if item.owner != current_user:
		abort(403)

	tag = Tag(item_id=item_id, name=form.tagname.data)

	db.session.add(tag)
	db.session.commit()

	flash("Tag has been added.", "info")
	return redirect(url_for("item_edit", item_id=item.item_id))

@app.route("/item/<int:item_id>/edit", methods=["GET", "POST"])
@login_required
def item_edit(item_id):
	item = Item.query.get_or_404(item_id)

	if item.owner != current_user:
		abort(403)

	form = EditItemForm();
	tag_form = AddTagForm();

	if form.validate_on_submit():
		item.itemname = form.itemname.data
		db.session.commit()
		flash("Item has been updated!", "info")
		return redirect(url_for("details", item_id=item.item_id))
	elif request.method == "GET":
		form.itemname.data = item.itemname

	return(render_template("item_edit.html", item=item, form=form, tag_form=tag_form))

@app.route("/item/<int:item_id>/delete")
def item_delete(item_id):
	item = Item.query.get(item_id)
	if item.owner != current_user:
		abort(403)
	item.deleted = True
	db.session.commit()

	flash("Item has been deleted.", "info")
	return redirect(url_for("index"))

@app.route("/entry/<int:entry_id>", methods=["GET", "POST"])
def entry(entry_id):
	entry = Entry.query.get(entry_id)

	if entry.item.owner != current_user:
		abort(403)

	form = UpdateEntryForm()

	if form.validate_on_submit():
		entry.timestamp = datetime.datetime.combine(form.date.data, form.time.data)
		entry.latitude = form.latitude.data
		entry.longitude = form.longitude.data
		entry.comment = form.comment.data

		checked_tags = []	# will be populated by all checked tag_ids
		form_data = request.form	#get all form data
		for f in form_data:
			if f[:4] == "tag-":	#if name is tag-X and it's checked (doesn't show if not checked)
				checked_tags.append(int(f[4:]))	#add it to the list of checked tags

		for tag in entry.item.tags:	# loop through all possible tags for the item
			if not tag.deleted:	# ignore entrytags for deleted tags
				if tagentry_already_exists(tag.tag_id, entry.entrytags):	# if there is an entrytag on this entry for this tag already
					if tag.tag_id not in checked_tags:	# ...and its unchecked
						EntryTag.query.filter_by(tag_id=tag.tag_id, entry_id=entry.entry_id).delete()	# remove the entrytag
				elif tag.tag_id in checked_tags:	# if theres NOT an entrytag on this entry for this tag already AND it's checked
					entry_tag = EntryTag(entry_id = entry.entry_id, tag_id = tag.tag_id)	# create a new entrytag
					db.session.add(entry_tag)	# ... and add it

		db.session.commit()
		flash("Entry has been updated.", "info")
	elif request.method == "GET":
		form.date.data = entry.timestamp.date()
		form.time.data = entry.timestamp.time()
		form.latitude.data = entry.latitude
		form.longitude.data = entry.longitude
		form.comment.data = entry.comment

	return render_template("entry.html", entry=entry, form=form)

@app.route("/entry/<int:entry_id>/delete")
def entry_delete(entry_id):
	entry = Entry.query.get(entry_id)

	if entry.item.owner != current_user:
		abort(403)

	entry.deleted = True
	db.session.commit()

	flash("Entry has been deleted.", "info")
	return redirect(url_for("details", item_id=entry.item.item_id))

@app.route("/tag/<int:tag_id>/delete")
def tag_delete(tag_id):
	tag = Tag.query.get(tag_id)

	if tag.item.owner != current_user:
		abort(403)

	tag.deleted = True
	db.session.commit()

	flash("Tag has been deleted.", "info")
	return redirect(url_for("item_edit", item_id=tag.item.item_id))

def tagentry_already_exists(checked_tag_id, existing_entrytags):
	""" returns True if checked_tag_id already exists in existing_entrytags """
	for eet in existing_entrytags:
		if checked_tag_id == eet.tag.tag_id:
			return True
	return False
