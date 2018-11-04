from flask import render_template, url_for, flash, redirect, request
from DataDrone2 import app, db, bcrypt
from DataDrone2.forms import *
from DataDrone2.models import *
from flask_login import login_user, current_user, logout_user, login_required

@app.route("/")
def index():
	if current_user.is_authenticated:
		return render_template("list.html")
	else:
		return render_template("home.html")

@app.route("/login", methods=["GET", "POST"])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = Users.query.filter_by(username=form.username.data).first()
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
		user = Users(username=form.username.data, email=form.email.data, password=hashed_password)
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
