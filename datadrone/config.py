from os import environ

DEBUG = True
SECRET_KEY = environ.get('DD_SECRET_KEY')
SQLALCHEMY_DATABASE_URI = environ.get('DD_DATABASE_URI') # set the environment variable DD_DATABASE_URI to your SQLAlchemy connection string
SQLALCHEMY_TRACK_MODIFICATIONS = False
