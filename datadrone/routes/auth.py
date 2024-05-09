from flask import Blueprint, render_template, redirect, url_for, flash, \
    request, session, current_app, abort
from flask_login import login_user, logout_user, current_user
from urllib.parse import urlencode
import secrets
import requests
import random
import string
from datadrone.forms import LoginForm
from datadrone.extensions import bcrypt, db
from datadrone.models import User


bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()

        if user is None:
            flash("User does not exist.", "error")
        elif not user.local_login:
            flash("Local login not activated. Use Google instead.", "error")
        elif not bcrypt.check_password_hash(user.password, form.password.data):
            flash("Incorrect password.", "error")
        elif user.password is None:
            flash("Local login not activated for user.", "error")
        else:
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(
                url_for("main.index"))

    return render_template("login.html", form=form)


@bp.route("/logout")
def logout():
    logout_user()
    flash('You have been logged out.', "message")
    return redirect(url_for("auth.login"))


@bp.route("/<provider>")
def oauth2_authorize(provider):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    provider_data = current_app.config['OAUTH2_PROVIDERS'].get(provider)
    if provider_data is None:
        abort(404)

    if request.args.get("remember") == "true":
        session['remember_login'] = True
    else:
        session['remember_login'] = False

    session['oauth2_state'] = secrets.token_urlsafe(16)

    qs = urlencode({
        'client_id': provider_data['client_id'],
        'redirect_uri': url_for('auth.oauth2_callback', provider=provider,
                                _external=True),
        'response_type': 'code',
        'scope': ' '.join(provider_data['scopes']),
        'state': session['oauth2_state'],
    })

    return redirect(provider_data['authorize_url'] + '?' + qs)


@bp.route('/callback/<provider>')
def oauth2_callback(provider):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    provider_data = current_app.config['OAUTH2_PROVIDERS'].get(provider)
    if provider_data is None:
        abort(404)

    if 'error' in request.args:
        for k, v in request.args.items():
            if k.startswith('error'):
                flash(f'{k}: {v}', "error")
        return redirect(url_for('main.index'))

    if request.args['state'] != session.get('oauth2_state'):
        abort(401)

    if 'code' not in request.args:
        abort(401)

    response = requests.post(
        provider_data['token_url'],
        data={'client_id': provider_data['client_id'],
              'client_secret': provider_data['client_secret'],
              'code': request.args['code'],
              'grant_type': 'authorization_code',
              'redirect_uri':
              url_for(
            'auth.oauth2_callback', provider=provider, _external=True), },
        headers={'Accept': 'application/json'})
    if response.status_code != 200:
        abort(401)
    oauth2_token = response.json().get('access_token')
    if not oauth2_token:
        abort(401)

    response = requests.get(
        provider_data['userinfo']['url'],
        headers={'Authorization': 'Bearer ' + oauth2_token,
                 'Accept': 'application/json', })
    if response.status_code != 200:
        abort(401)
    email = provider_data['userinfo']['email'](response.json())

    user = User.query.filter_by(email=email).first()
    if user is None:
        user = User(email=email.lower(), password=generate_random_password())
        db.session.add(user)
        db.session.commit()

    login_user(user, remember=session.get('remember_login'))

    return redirect(url_for('main.index'))


def generate_random_password() -> str:
    characters = string.ascii_letters + string.digits + string.punctuation
    result = ''.join(random.choice(characters) for i in range(32))

    return result
