
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
        from .models import Product, Property, Customer, Comment, Order
        from datetime import date
        
        a.db.session.add(Property('Kategoria','Ekrany'))
        a.db.session.add(Property('Kategoria','Myszki'))
        a.db.session.add(Property('Producent','Lenovo'))
        a.db.session.add(Property('Kategoria','Baterie'))
        a.db.session.add(Property('Producent','Asus'))
        
        a.db.session.add(Product('Samsung', 9999, 4, description='bardzo drogi komputer'))
        a.db.session.add(Product('IBM', 2999, 4, description='bardzo ładny komputer'))
        a.db.session.add(Product('Asus1', 3999, 4, description='bardzo asusowy komputer'))
        a.db.session.add(Product('Asus2', 4999, 4, description='bardzo asusowy komputer'))
       
        c1 = Property('Kategoria','Laptopy')
        c2 = Property('Kategoria','Procesory')
        p1 = Product('Lenovo', 3500, 2, description='bardzo dobry komputer')        
        p2 = Product('Asus', 2399, 0, description='bardzo szybki komputer')
        p3 = Product('Intel', 100, 2, description='bardzo tani procesor')        
        p4 = Product('AMD', 2000, 2, description='bardzo drogi procesor')
        
        p1.properties.append(c1)
        p2.properties.append(c1)
        p3.properties.append(c2)
        p4.properties.append(c2)

        a.db.session.add(p1)
        a.db.session.add(p2)
        a.db.session.add(p3)
        a.db.session.add(p4)

        a.db.session.add(Customer('plusplus@gmail.com', 'kostek'))
        a.db.session.add(Comment(1,1,3,'kiepski'))

        a.db.session.commit()

        # zamówienie dla użytkownika plusplus@gmail.com (o id = 1)
        # już skomentował
        a.db.session.add(
            Order()
            .add_product(Product.query.get(1))
            .set_customer(1)
            .set_destination_name('ABSklep')
            .set_payment_method(Order.ENUM_PAYMENT_METHODS_VALUES[0])
            .set_status(Order.ENUM_STATUS_VALUES[0])
            .set_price(10000 * 100)
            .set_address('wiocha 12')
            .set_city('wiochowisko')
            .set_postal_code('69-666')
        )

        # zamówienie dla użytkownika sample@gmail.com (o id = 2)
        # jeszcze nie skomentował
        a.db.session.add(Customer('sample@gmail.com', 'sample'))
        a.db.session.add(
            Order()
            .add_product(Product.query.get(1))
            .set_customer(2)
            .set_destination_name('ABSklep')
            .set_payment_method(Order.ENUM_PAYMENT_METHODS_VALUES[0])
            .set_status(Order.ENUM_STATUS_VALUES[0])
            .set_price(10000 * 100)
            .set_address('wiocha 12')
            .set_city('wiochowisko')
            .set_postal_code('69-666')
        )

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
