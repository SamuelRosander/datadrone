from DataDrone2 import db, login_manager
from datetime import datetime
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
	return Users.query.get(int(user_id))

class Users(db.Model, UserMixin):
	__tablename__ = "ddusers"
	userID = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(32), unique=True, nullable=False)
	password = db.Column(db.String(60), nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	register_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

	def __repr__(self):
		return f"Users('{self.userID}', '{self.username}', '{self.email}', '{self.register_date}')"

	def get_id(self):
		return self.userID
