from flask import render_template, url_for, flash, redirect, request, abort
from DataDrone2 import app, db, bcrypt
from DataDrone2.forms import *
from DataDrone2.models import *
from flask_login import login_user, current_user, logout_user, login_required

@app.route("/")
def index():
	if current_user.is_authenticated:
		form = AddItemForm()
		items = Item.query.filter_by(user_id=current_user.user_id).all()
		return render_template("list.html", items=items, form=form)
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
	if item.owner != current_user:
		abort(403)
	entry = Entry(item_id = item_id)
	db.session.add(entry)
	db.session.commit()
	flash("Entry added!", "info")
	return redirect(url_for("entry", entry_id=entry.entry_id))
