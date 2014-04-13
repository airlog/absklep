
from random import randint

from flask import flash, redirect, render_template, url_for
from flask.ext.login import login_required
from jinja2 import Markup
from markdown import markdown

from .. import app, lorem
import absklep.forms


@app.route('/orders/')
@login_required
def ordersview():
    from flask import g
    from ..models import Order, Customer, Property

    if not g.current_user.is_authenticated():
        flash('Nie jestes zalogowany!')
        return redirect(url_for('index'))
    categories = Property.query.filter(Property.key=='Kategoria').order_by(Property.value).all()
    orders = g.current_user.orders
    return render_template('orders.html',
                           lorem=Markup(markdown(lorem, output='html5')),
                           random=randint(0, 0xFFFFFFFF),
                           logform=absklep.forms.Login(),
                           categories=categories,
                           orders=orders)

@app.route('/orders/show/<int:oid>/')
@login_required
def detailsview(oid):
    from flask import g
    from ..models import Order, Property

    if not g.current_user.is_authenticated():
        flash('Nie jestes zalogowany!')
        return redirect(url_for('index'))

    categories = Property.query.filter(Property.key=='Kategoria').order_by(Property.value).all()
    orders = list(filter(lambda o: o.id == oid, g.current_user.orders))
#    print(orders[0].products_amount)
    return render_template('details.html',
                           lorem=Markup(markdown(lorem, output='html5')),
                           logform=absklep.forms.Login(),
                           categories=categories,
                           order=orders[0])


@app.route('/orders/make')
def makeorderview():
    return render_template('address.html',
    	logform=absklep.forms.Login())


__all__ = ['ordersview', 'detailsview', 'makeorderview', ]
