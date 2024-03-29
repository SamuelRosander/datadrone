from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, \
    HiddenField, FloatField, RadioField, DateField, TimeField
from wtforms.validators import Length, Email, EqualTo, ValidationError, \
    Optional, DataRequired
from .extensions import bcrypt
from .models import User


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[Length(min=2, max=32)])
    email = StringField("Email", validators=[Email()])
    password = PasswordField("Password", validators=[Length(min=4, max=64)])
    confirm_password = PasswordField(
        "Confirm Password", validators=[EqualTo("password")])
    submit = SubmitField("Sign Up")

    def validate_username(self, field):
        user = User.query.with_entities(
            User.username).filter(
            User.username.ilike(field.data)).all()
        if user:
            raise ValidationError("Username already exists.")

    def validate_email(self, field):
        email = User.query.filter_by(email=field.data.lower()).first()
        if email:
            raise ValidationError("Email adress already exists.")


class LoginForm(FlaskForm):
    email = StringField("Email")
    password = PasswordField("Password")
    remember = BooleanField("Remember Me")
    submit = SubmitField("Log In")


class RequestResetForm(FlaskForm):
    email = StringField("Email", validators=[Email()])
    submit = SubmitField("Send reset link")

    def validate_email(self, field):
        email = User.query.filter_by(email=field.data.lower()).first()
        if not email:
            raise ValidationError("Email not found in database.")


class ResetPasswordForm(FlaskForm):
    password = PasswordField("Password", validators=[Length(min=4, max=64)])
    confirm_password = PasswordField(
        "Confirm Password", validators=[EqualTo("password")])
    submit = SubmitField("Reset password")


class UpdateAccountForm(FlaskForm):
    username = StringField("Username", validators=[Length(min=2, max=32)])
    email = StringField("Email", validators=[Email()])
    password = PasswordField("Password")
    confirm_password = PasswordField(
        "Confirm Password", validators=[EqualTo("password")])
    current_password = PasswordField("Current Password")
    submit = SubmitField("Update")

    def validate_username(self, field):
        if current_user.username.lower() != field.data.lower():
            user = User.query.with_entities(
                User.username).filter(
                User.username.ilike(field.data)).all()
            if user:
                raise ValidationError("Username already exists.")

    def validate_email(self, field):
        if current_user.email.lower() != field.data.lower():
            email = User.query.filter_by(email=field.data.lower()).first()
            if email:
                raise ValidationError("Email adress already exists.")

    def validate_current_password(self, field):
        user = User.query.filter_by(username=current_user.username).first()
        if not bcrypt.check_password_hash(user.password, field.data):
            raise ValidationError("Wrong password.")


class AddItemForm(FlaskForm):
    itemname = StringField("Itemname", validators=[Length(min=1, max=64)])


class AddEntryForm(FlaskForm):
    geo = BooleanField("Geo")
    latitude = HiddenField("Latitude")
    longitude = HiddenField("Longitude")
    timestamp = HiddenField("Timestamp")


class UpdateEntryForm(FlaskForm):
    date = DateField("Date")
    time = TimeField("Time")
    latitude = FloatField("Latitude", validators=[Optional()])
    longitude = FloatField("Longitude", validators=[Optional()])
    comment = StringField("Comment")
    submit = SubmitField("Update")


class DetailsSearchScopeForm(FlaskForm):
    choices = [("True", 'Yes'), ("False", 'No'), ("all", 'All')]
    scope_from = DateField("From")
    scope_to = DateField("To")
    filter_geo = RadioField('Geo', choices=choices, default="all")
    filter_comment = RadioField('Comment', choices=choices, default="all")
    submit = SubmitField("Search")


class EditItemForm(FlaskForm):
    itemname = StringField("Itemname", validators=[Length(min=1, max=64)])
    submit = SubmitField("Update")


class AddTagForm(FlaskForm):
    tagname = StringField("Tagname", validators=[Length(min=1, max=32)])
    submit = SubmitField("Add")


class EditTagForm(FlaskForm):
    tagname = StringField("Tagname", validators=[Length(min=1, max=32)])
    hidden = BooleanField("Hide from new")
    archived = BooleanField("Archived")
    submit = SubmitField("Update")


class AddLocationForm(FlaskForm):
    name = StringField("Location name", validators=[Length(min=1, max=64)])
    latitude = FloatField("Latitude", validators=[DataRequired()])
    longitude = FloatField("Longitude", validators=[DataRequired()])
    submit = SubmitField("Add location")


class EditLocationForm(FlaskForm):
    name = StringField("Location name", validators=[Length(min=1, max=64)])
    latitude = FloatField("Latitude", validators=[DataRequired()])
    longitude = FloatField("Longitude", validators=[DataRequired()])
    submit = SubmitField("Update")
