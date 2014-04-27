
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
            
    a.db.create_all()

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

