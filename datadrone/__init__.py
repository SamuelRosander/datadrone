from flask import Flask
from .extensions import db, login_manager, bcrypt, mail
from .routes import create_routes


def create_app(test_config=None):
    app = Flask(__name__)

    if test_config:
        app.config.from_mapping(test_config)
    else:
        app.config.from_pyfile("config.py")

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "login"
    bcrypt.init_app(app)
    mail.init_app(app)

    create_routes(app)

    return app
