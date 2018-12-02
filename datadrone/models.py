from datadrone import db, login_manager
from datetime import datetime
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

class User(db.Model, UserMixin):
	__tablename__ = "ddusers"
	user_id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(32), unique=True, nullable=False)
	password = db.Column(db.String(60), nullable=False)
	email = db.Column(db.String(128), unique=True, nullable=False)
	register_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
	items = db.relationship("Item", backref="owner", lazy=True)

	def __repr__(self):
		return f"User('{self.user_id}', '{self.username}', '{self.email}')"

	def get_id(self):
		return self.user_id

class Item(db.Model):
	__tablename__ = "dditems"
	item_id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey("ddusers.user_id"), nullable=False)
	itemname = db.Column(db.String(64), nullable=False)
	geo_default = db.Column(db.Boolean, default=False)
	deleted = db.Column(db.Boolean, default=False)
	entries = db.relationship("Entry", backref="item", lazy=True)
	tags = db.relationship("Tag", backref="item", lazy=True)

	def __repr__(self):
		return f"Item('{self.item_id}', '{self.user_id}', '{self.itemname}')"

class Entry(db.Model):
	__tablename__ = "ddentries"
	entry_id = db.Column(db.Integer, primary_key=True)
	item_id = db.Column(db.Integer, db.ForeignKey("dditems.item_id"), nullable=False)
	timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now)
	comment = db.Column(db.String(256))
	latitude = db.Column(db.Float)
	longitude = db.Column(db.Float)
	entrytags = db.relationship("EntryTag", backref="entry", lazy=True)
	deleted = db.Column(db.Boolean, default=False)

	def __repr__(self):
		return f"Entry('{self.entry_id}', '{self.item_id}', '{self.timestamp}')"

class Tag(db.Model):
	__tablename__ = "ddtags"
	tag_id = db.Column(db.Integer, primary_key=True)
	item_id = db.Column(db.Integer, db.ForeignKey("dditems.item_id"), nullable=False)
	name = db.Column(db.String(32), nullable=False)
	is_default = db.Column(db.Boolean, default=False)
	tagentries = db.relationship("EntryTag", backref="tag", lazy=True)

	def __repr__(self):
		return f"Tag('{self.tag_id}', '{self.name}')"

class EntryTag(db.Model):
	__tablename__ = "ddentrytags"
	entrytag_id = db.Column(db.Integer, primary_key=True)
	entry_id = db.Column(db.Integer, db.ForeignKey("ddentries.entry_id"), nullable=False)
	tag_id = db.Column(db.Integer, db.ForeignKey("ddtags.tag_id"), nullable=False)

	def __repr__(self):
		return f"EntryTag('self.entrytag_id', 'self.entry_id', 'self.tag_id')"
