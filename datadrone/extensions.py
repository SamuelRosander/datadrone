from flask import url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail, Message

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
mail = Mail()


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message(
        "DataDrone Password Reset", sender="noreply@samuelrosander.se",
        recipients=[user.email])
    msg.body = f"""To reset your password visit the following link:

{url_for("auth.reset_token", token=token, _external=True)}
"""
    mail.send(msg)
