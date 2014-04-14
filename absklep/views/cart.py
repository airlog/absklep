
import json

from flask import render_template, request

from .. import app
from ..forms import Login
from ..models import Product, Property


def load_cart_cookie(cookie_name='cart'):
    '''
    Próbuje parsować zawartość koszyka, który powinień być zakodowanym w JSON słownikiem. Kluczem
    w takim słowniku jest klucz główny (id) produktu, a wartością ilość tego produktu.
    '''
    jsonCart = request.cookies.get(cookie_name)
    if jsonCart is None or jsonCart == '':
        return {}

    obj = json.loads(jsonCart)
    if not isinstance(obj, dict):
        return {}

    cart = {}
    for key, value in obj.items():
        try:
            product = Product.query.get(int(key))
        except ValueError:
            continue

        if product is None:
            continue

        cart[product] = value

    return cart


@app.route('/cart/')
def cartview():
    cart = load_cart_cookie()

    return render_template('cart.html',
                           logform=Login(),
                           cart=cart,
                           categories=Property.get_categories())


__all__ = ['cartview', ]
