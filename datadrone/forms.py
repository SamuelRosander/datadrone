from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, HiddenField
from wtforms.validators import Length, Email, EqualTo, ValidationError
from wtforms.fields.html5 import DateField
from datadrone import bcrypt
from datadrone.models import User

class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[Length(min=2, max=32)])
    email = StringField("Email", validators=[Email()])
    password = PasswordField("Password", validators=[Length(min=4, max=64)])
    confirm_password = PasswordField("Confirm Password", validators=[EqualTo("password")])
    submit = SubmitField("Sign Up")

    def validate_username(self, field):
        user = User.query.filter_by(username=field.data).first()
        if user:
            raise ValidationError("Username already exists.")

    def validate_email(self, field):
        email = User.query.filter_by(email=field.data).first()
        if email:
            raise ValidationError("Email adress already exists.")

class LoginForm(FlaskForm):
    username = StringField("Username")
    password = PasswordField("Password")
    remember = BooleanField("Remember Me")
    submit = SubmitField("Log In")

class UpdateAccountForm(FlaskForm):
    username = StringField("Username", validators=[Length(min=2, max=32)])
    email = StringField("Email", validators=[Email()])
    password = PasswordField("Password")
    confirm_password = PasswordField("Confirm Password", validators=[EqualTo("password")])
    current_password = PasswordField("Current Password")
    submit = SubmitField("Update")

    def validate_username(self, field):
        if current_user.username != field.data:
            user = User.query.filter_by(username=field.data).first()
            if user:
                raise ValidationError("Username already exists.")

    def validate_email(self, field):
        if current_user.email != field.data:
            email = User.query.filter_by(email=field.data).first()
            if email:
                raise ValidationError("Email adress already exists.")

    def validate_current_password(self, field):
        user = User.query.filter_by(username=current_user.username).first()
        if not bcrypt.check_password_hash(user.password, field.data):
            raise ValidationError("Wrong password.")

class AddItemForm(FlaskForm):
    itemname = StringField("Itemname", validators=[Length(min=2, max=64)])

class AddEntryForm(FlaskForm):
    geo = BooleanField("Geo")
    latitude = HiddenField("Latitude")
    longitude = HiddenField("Longitude")

class UpdateEntryForm(FlaskForm):
    timestamp = StringField("Timestamp")
    latitude = StringField("Latitude")
    longitude = StringField("Longitude")
    comment = StringField("Comment")
    submit = SubmitField("Update")

class DetailsSearchScopeForm(FlaskForm):
    scope_from = DateField("From")
    scope_to = DateField("To")
    submit = SubmitField("->")
