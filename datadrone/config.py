from os import environ

SECRET_KEY = environ.get('DD_SECRET_KEY')  # secret key and db string and saved in environment variables
SQLALCHEMY_DATABASE_URI = environ.get('DD_DATABASE_URI')
SQLALCHEMY_TRACK_MODIFICATIONS = False
MAIL_SERVER = "smtp.googlemail.com"
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = environ.get('DD_MAIL_USERNAME')
MAIL_PASSWORD = environ.get('DD_MAIL_PASSWORD')
