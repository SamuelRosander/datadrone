from flask import url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail, Message
from flask_caching import Cache

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
mail = Mail()
cache = Cache()


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message(
        "DataDrone Password Reset", sender="noreply@samuelrosander.se",
        recipients=[user.email])
    msg.body = f"""To reset your password visit the following link:

{url_for("user.reset_token", token=token, _external=True)}
"""
    mail.send(msg)
