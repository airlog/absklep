
from flask import render_template, request

from .. import app
from ..controllers import load_cart_cookie
from ..forms import Login
from ..models import Product, Property
from ..util import only_customer


@app.route('/cart/')
@only_customer()
def cartview():
    cart = load_cart_cookie()

    return render_template('cart.html',
                           logform=Login(),
                           cart=cart,
                           categories=Property.get_categories())


__all__ = ['cartview', ]
