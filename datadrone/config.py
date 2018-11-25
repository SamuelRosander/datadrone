from os import environ

SECRET_KEY = environ.get('DD_SECRET_KEY') # secret key and db string and saved in environment variables
SQLALCHEMY_DATABASE_URI = environ.get('DD_DATABASE_URI')
SQLALCHEMY_TRACK_MODIFICATIONS = False
