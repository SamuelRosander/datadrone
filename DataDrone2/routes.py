from flask import render_template, url_for, flash, redirect, request, abort
from DataDrone2 import app, db, bcrypt
from DataDrone2.forms import *
from DataDrone2.models import *
from flask_login import login_user, current_user, logout_user, login_required

@app.route("/")
def index():
	if current_user.is_authenticated:
		item_form = AddItemForm()
		entry_form = AddEntryForm()
		items = Item.query.filter_by(user_id=current_user.user_id).all()
		tags = Tag.query.filter_by(user_id=current_user.user_id).all()
		taglinks = TagLink.query.filter(Item.user_id == current_user.user_id).all()
		return render_template("list.html", items=items, tags=tags, taglinks=taglinks, item_form=item_form, entry_form=entry_form)
	else:
		return render_template("home.html")

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

@app.route("/logout")
def logout():
	logout_user()
	return redirect(url_for("login"))

@app.route("/details")
@login_required
def details():
	return render_template("details.html")

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

@app.route("/entry/<int:entry_id>")
def entry(entry_id):
	entry = Entry.query.get(entry_id)
	return render_template("entry.html", entry=entry)

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
	taglinks = TagLink.query.filter_by(item_id=item_id).all()
	form = AddEntryForm()

	if item.owner != current_user:
		abort(403)

	if form.geo.data:	#if geo checkbox is checked
		entry = Entry(item_id = item_id, latitude = form.latitude.data, longitude = form.longitude.data)	#add entry with geo
		item.geo_default = True;	#used as a "remember" function for the geo checkbox
	else:
		entry = Entry(item_id = item_id)	#add entry without geo
		item.geo_default = False;

	db.session.add(entry)
	db.session.add(item)
	db.session.commit()	#needed for entry.entry_id in tag section below

	checked_tags = []
	form_data = request.form	#get all form data
	for f in form_data:
		if f[:4] == "tag-":	#if id is tag-X and it's checked (doesn't show if not checked)
			checked_tags.append(int(f[4:]))	#add it to the list of checked tags

	for taglink in taglinks:	#loop through all visible tags for the item
		taglink.is_default = False	#set all as default. will be changed again below if it's checked. Used for saving the "checked"-value

		if taglink.tag_id in checked_tags:	#if any visible tags (taglinks) are checked
			taglink.is_default = True	#the tag will now be checked per default in the future
			entry_tag = EntryTag(entry_id = entry.entry_id, tag_id = taglink.tag_id)	#create an entrytag object...
			db.session.add(entry_tag)	#...and add it to the db

	db.session.commit()	#commit tag changes
	flash("Entry added!", "info")
	return redirect(url_for("entry", entry_id=entry.entry_id))
