
from flask import g, render_template
from flask.ext.login import login_required

from .. import app
from ..forms import Login
from ..models import Property


@app.route('/orders/')
@login_required
def ordersview():
    orders = g.current_user.orders
    return render_template('orders.html',
                           logform=Login(),
                           categories=Property.get_categories(),
                           orders=orders)


@app.route('/orders/show/<int:oid>/')
@login_required
def detailsview(oid):
    orders = list(filter(lambda o: o.id == oid, g.current_user.orders))
    return render_template('details.html',
                           logform=Login(),
                           categories=Property.get_categories(),
                           order=orders[0])


@app.route('/orders/make')
def makeorderview():
    return render_template('address.html',
                           logform=Login())


__all__ = ['ordersview', 'detailsview', 'makeorderview', ]
