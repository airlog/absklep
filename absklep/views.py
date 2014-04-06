
from random import randint

from flask import render_template
from jinja2 import Markup
from markdown import markdown

from . import app, lorem


@app.route('/')
@app.route('/products/')
def index():
    return render_template('index.html',
                           lorem=Markup(markdown(lorem, output='html5')),
                           random=randint(0, 0xFFFFFFFF))

@app.route('/products/<int:pid>/')
def productview(pid):
    return render_template('product.html',
                           lorem=Markup(markdown(lorem, output='html5')),
                           random=randint(0, 0xFFFFFFFF))

@app.route('/products/category/<int:cid>/')
def categoryview(cid):
    return render_template('category.html',
                           random=randint(0, 0xFFFFFFFF))

@app.route('/auth/signup')
def register():
    return render_template('auth/signup.html',
                           lorem=Markup(markdown(lorem, output='html5')))

@app.route('/orders/make')
def makeorderview():
    return render_template('address.html')

@app.route('/cart/')
def cartview():
    return render_template('cart.html',
                           lorem=Markup(markdown(lorem, output='html5')),
                           random=randint(0, 0xFFFFFFFF))

@app.route('/orders/')
def ordersview():
    return render_template('orders.html',
                           lorem=Markup(markdown(lorem, output='html5')),
                           random=randint(0, 0xFFFFFFFF))

@app.route('/observed/')
def observedview():
    return render_template('observed.html',
                           lorem=Markup(markdown(lorem, output='html5')))

@app.route('/orders/show/<int:oid>/')
def detailsview(oid):
    return render_template('details.html',
                           lorem=Markup(markdown(lorem, output='html5')))

