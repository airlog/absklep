
"""
This is application's default configuration.
"""

DEBUG = True
SECRET_KEY = "totally random bytes"  # TODO: generate random bytes

#SQLALCHEMY_DATABASE_URI = "sqlite:///../test.db"
SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://marta:fiflak@localhost/absklep"
