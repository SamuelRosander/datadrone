from flask import current_app
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import aliased
from .extensions import db, login_manager
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer as Serializer
from itsdangerous import SignatureExpired
from datetime import datetime


class User(db.Model, UserMixin):
    __tablename__ = "ddusers"
    user_id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(128), nullable=False)
    local_login = db.Column(db.Boolean, default=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    register_date = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow())
    items = db.relationship("Item", backref="owner", lazy=True,
                            order_by="Item.item_id")
    locations = db.relationship("Location", backref="owner", lazy=True,
                                order_by="Location.location_id")

    def get_reset_token(self):
        s = Serializer(current_app.config["SECRET_KEY"])
        return s.dumps({"user_id": self.user_id})

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            user_id = s.loads(token, max_age=1800)["user_id"]
        except SignatureExpired:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.user_id}', '{self.email}')"

    def get_id(self):
        return self.user_id


class Item(db.Model):
    __tablename__ = "dditems"
    item_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("ddusers.user_id"),
                        nullable=False)
    itemname = db.Column(db.String(64), nullable=False)
    geo_default = db.Column(db.Boolean, default=False)
    deleted = db.Column(db.Boolean, default=False)
    entries = db.relationship("Entry", backref="item", lazy=True,
                              order_by="Entry.entry_id")
    tags = db.relationship("Tag", backref="item", lazy=True,
                           order_by="Tag.tag_id")

    def __repr__(self):
        return f"Item('{self.item_id}', '{self.user_id}', '{self.itemname}')"

    @hybrid_property
    def active_tags(self):
        return [tag for tag in self.tags
                if not tag.deleted and not tag.archived and not tag.hidden]

    @active_tags.expression
    def active_tags(cls):
        TagAlias = aliased(Tag)
        return (
            db.session.query(TagAlias)
            .filter(TagAlias.item_id == cls.item_id)
            .filter(TagAlias.deleted.is_(False))
            .filter(TagAlias.archived.is_(False))
            .filter(TagAlias.hidden.is_(False))
        )


class Entry(db.Model):
    __tablename__ = "ddentries"
    entry_id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey(
        "dditems.item_id"), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    utc_timestamp = db.Column(db.DateTime, nullable=False)
    comment = db.Column(db.String(256))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    entrytags = db.relationship(
        "EntryTag", backref="entry", lazy=True,
        order_by="EntryTag.entrytag_id")
    deleted = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"Entry('{self.entry_id}', '{self.item_id}', " \
            f"'{self.timestamp}')"


class Tag(db.Model):
    __tablename__ = "ddtags"
    tag_id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey(
        "dditems.item_id"), nullable=False)
    name = db.Column(db.String(32), nullable=False)
    is_default = db.Column(db.Boolean, default=False)
    hidden = db.Column(db.Boolean, default=False)
    archived = db.Column(db.Boolean, default=False)
    deleted = db.Column(db.Boolean, default=False)
    tagentries = db.relationship("EntryTag", backref="tag", lazy=True,
                                 order_by="EntryTag.entrytag_id")

    def __repr__(self):
        return f"Tag('{self.tag_id}', '{self.name}')"


class EntryTag(db.Model):
    __tablename__ = "ddentrytags"
    entrytag_id = db.Column(db.Integer, primary_key=True)
    entry_id = db.Column(db.Integer, db.ForeignKey(
        "ddentries.entry_id"), nullable=False)
    tag_id = db.Column(
        db.Integer, db.ForeignKey("ddtags.tag_id"), nullable=False)

    def __repr__(self):
        return f"EntryTag('{self.entrytag_id}', '{self.entry_id}', " \
            f"'{self.tag_id}')"


class Location(db.Model):
    __tablename__ = "ddlocations"
    location_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        "ddusers.user_id"), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    deleted = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"Location('{self.location_id}', '{self.name}', " \
            f"'{self.latitude}', '{self.longitude}')"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
