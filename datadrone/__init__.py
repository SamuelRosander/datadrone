from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_sslify import SSLify
import pymysql

app = Flask(__name__)
sslify = SSLify(app)
app.config.from_pyfile("config.py")
pymysql.install_as_MySQLdb()
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
mail = Mail(app)

from datadrone import routes
