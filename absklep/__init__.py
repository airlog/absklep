
from flask import Flask
from flask.ext.login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy

__version__ = "0.1.0"
__envvar__ = "ABSKLEP_SETTINGS"

app = Flask(__name__)
app.db = SQLAlchemy(app)


import absklep.models


def load_config(a, package=None):
    """
    Loading application configuration from environment variable or, if not set, from config file
    distributed with this module.

    :param a:   flask's application object
    """
    if package is None:
        package = __name__
    a.config.from_object("{}.config".format(package))     # default settings
    try:
        a.config.from_envvar(__envvar__)                 # override defaults
    except RuntimeError:
        pass


def load_database(a):
    def some_data_for_tests():
        from .models import Product, Property, Customer, Comment, Order, Employee, ProductAmount, Archival
        from datetime import date, datetime
        
        e1 = Employee('Marek','Marek','marek@buziaczek.pl','123','12345678901')
        e2 = Employee('Jarek','Jarek','jarek@buziaczek.pl','123','12345678902')

        a.db.session.add(e1)
        a.db.session.add(e2)
        a.db.session.commit()
        
    a.db.drop_all()
    a.db.create_all()
    some_data_for_tests()

from os.path import abspath
app.get_upload_folder = '{}/{}'.format(abspath('.'),'absklep/static/images/photos')

load_config(app, package=__name__)
load_database(app)

login_manager = LoginManager()
login_manager.init_app(app)

import absklep.controllers
import absklep.views
import absklep.forms

from absklep.views import login

login_manager.login_view = 'login'

