
from flask import Flask, request, render_template, flash, url_for, redirect
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, login_user, current_user, logout_user, login_required

from jinja2 import Markup
from markdown import markdown

from random import randint

__version__ = "0.1.0"
__envvar__ = "ABSKLEP_SETTINGS"

app = Flask(__name__)
app.db = SQLAlchemy(app)

lorem = 'dummy'
with open('lorem.txt') as file: lorem = file.read()

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
        from .models import Product, Property
        a.db.session.add(Property('Kategoria','Ekrany'))
        a.db.session.add(Property('Kategoria','Myszki'))
        a.db.session.add(Property('Producent','Lenovo'))
        a.db.session.add(Property('Kategoria','Procesory'))
        a.db.session.add(Property('Kategoria','Baterie'))
        a.db.session.add(Property('Producent','Asus'))
        a.db.session.add(Product('Lenovo', 3500, 2, description='bardzo dobry komputer'))
        a.db.session.add(Product('Samsung', 9999, 4, description='bardzo drogi komputer'))
        a.db.session.add(Product('IBM', 2999, 4, description='bardzo ładny komputer'))
        a.db.session.add(Product('Asus1', 3999, 4, description='bardzo asusowy komputer'))
        a.db.session.add(Product('Asus2', 4999, 4, description='bardzo asusowy komputer'))
        a.db.session.commit()
    
    a.db.drop_all()
    a.db.create_all()
    some_data_for_tests()

load_config(app, package=__name__)
load_database(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

import absklep.controllers
import absklep.views
import absklep.forms
