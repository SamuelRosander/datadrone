from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import pymysql

app = Flask(__name__)
app.config["SECRET_KEY"] = "001e218a814e52e63f40bd4917a223a8"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:@localhost/datadrone"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
pymysql.install_as_MySQLdb()
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

from DataDrone2 import routes
