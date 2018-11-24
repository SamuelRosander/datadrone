<<<<<<< HEAD
from os import environ

DEBUG = True
SECRET_KEY = environ.get('DD_SECRET_KEY')
SQLALCHEMY_DATABASE_URI = environ.get('DD_DATABASE_URI') # set the environment variable DD_DATABASE_URI to your SQLAlchemy connection string
=======
DEBUG = True
SECRET_KEY = "001e218a814e52e63f40bd4917a223a8"
SQLALCHEMY_DATABASE_URI = "mysql://root:@localhost/datadrone"
>>>>>>> 47854163768c02bd18b18ada00e19a1c7e4ed735
SQLALCHEMY_TRACK_MODIFICATIONS = False
