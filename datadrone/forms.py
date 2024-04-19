from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, \
    HiddenField, FloatField, RadioField, DateField, TimeField
from wtforms.validators import Length, Email, EqualTo, ValidationError, \
    Optional, DataRequired
from .extensions import bcrypt
from .models import User


class RegistrationForm(FlaskForm):
    email = StringField("Email", validators=[Email(), DataRequired()])
    password = PasswordField("Password", validators=[Length(min=8)])
    confirm_password = PasswordField(
        "Confirm Password", validators=[EqualTo("password")])
    submit = SubmitField("Sign up")

    def validate_email(self, field):
        email = User.query.filter_by(email=field.data.lower()).first()
        if email:
            raise ValidationError("Email adress already exists.")


class LoginForm(FlaskForm):
    email = StringField("Email")
    password = PasswordField("Password")
    remember = BooleanField("Remember me")
    submit = SubmitField("Log in")


class RequestResetForm(FlaskForm):
    email = StringField("Email", validators=[Email()])
    submit = SubmitField("Send reset link")

    def validate_email(self, field):
        email = User.query.filter_by(email=field.data.lower()).first()
        if not email:
            raise ValidationError("Email not found in database.")


class ResetPasswordForm(FlaskForm):
    password = PasswordField("New password", validators=[
                             Length(min=8)])
    confirm_password = PasswordField(
        "Confirm password", validators=[EqualTo("password")])
    submit = SubmitField("Reset password")


class UpdateAccountForm(FlaskForm):
    email = StringField("Email")
    password = PasswordField("New password", validators=[Length(min=8)])
    confirm_password = PasswordField(
        "Confirm new password", validators=[EqualTo("password")])
    current_password = PasswordField("Current password")
    submit = SubmitField("Update")

    def validate_current_password(self, field):
        user = User.query.filter_by(email=current_user.email).first()
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
    date = DateField("Date", validators=[DataRequired()])
    time = TimeField("Time", validators=[DataRequired()])
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
    itemname = StringField("Name", validators=[
                           Length(min=1, max=64), DataRequired()])
    submit = SubmitField("Update")


class AddTagForm(FlaskForm):
    tagname = StringField("Name", validators=[
                          Length(min=1, max=32), DataRequired()])
    submit = SubmitField("Add")


class EditTagForm(FlaskForm):
    tagname = StringField("Tagname", validators=[
                          Length(min=1, max=32), DataRequired()])
    hidden = BooleanField("Hidden")
    archived = BooleanField("Archived")
    submit = SubmitField("Update")


class AddLocationForm(FlaskForm):
    name = StringField("Name", validators=[
                       Length(min=1, max=64), DataRequired()])
    latitude = FloatField("Latitude", validators=[DataRequired()])
    longitude = FloatField("Longitude", validators=[DataRequired()])
    submit = SubmitField("Add location")


class EditLocationForm(FlaskForm):
    name = StringField("Location name", validators=[
                       Length(min=1, max=64), DataRequired()])
    latitude = FloatField("Latitude", validators=[DataRequired()])
    longitude = FloatField("Longitude", validators=[DataRequired()])
    submit = SubmitField("Update")
