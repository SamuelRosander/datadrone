from flask import Flask
from .extensions import db, login_manager, bcrypt, mail
from .routes import main, auth, locations, items, entries, tags


def create_app(test_config=None):
    app = Flask(__name__)

    if test_config:
        app.config.from_mapping(test_config)
    else:
        app.config.from_pyfile("config.py")

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    bcrypt.init_app(app)
    mail.init_app(app)

    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(items.bp)
    app.register_blueprint(entries.bp)
    app.register_blueprint(tags.bp)
    app.register_blueprint(locations.bp)

    app.register_error_handler(403, main.error_403)
    app.register_error_handler(404, main.error_404)
    app.register_error_handler(500, main.error_500)

    return app
