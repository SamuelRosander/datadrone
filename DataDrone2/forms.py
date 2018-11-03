from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import Length, Email, EqualTo, ValidationError
from DataDrone2.models import Users

class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[Length(min=2, max=32)])
    email = StringField("Email", validators=[Email()])
    password = PasswordField("Password", validators=[Length(min=4, max=64)])
    confirm_password = PasswordField("Confirm Password", validators=[EqualTo("password")])
    submit = SubmitField("Sign Up")

    def validate_username(self, field):
        user = Users.query.filter_by(username=field.data).first()
        if user:
            raise ValidationError("Username already exists.")

    def validate_email(self, field):
        email = Users.query.filter_by(email=field.data).first()
        if email:
            raise ValidationError("Email adress already exists.")

class LoginForm(FlaskForm):
    username = StringField("Username")
    password = PasswordField("Password")
    remember = BooleanField("Remember Me")
    submit = SubmitField("Log In")
