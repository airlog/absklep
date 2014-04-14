
import json

from flask import g, request
from flask.ext.login import current_user

from . import app, login_manager


@app.before_request
def inject_user():
    g.current_user = current_user

@login_manager.user_loader
def load_user(uid):
    from absklep.models import Customer, Employee

    if uid[0] == 'u': return Customer.query.get(int(uid[1:]))
    if uid[0] == 'e': return Employee.query.get(int(uid[1:]))
    return None


def load_cart_cookie(cookie_name='cart'):
    '''
    Próbuje parsować zawartość koszyka, który powinień być zakodowanym w JSON słownikiem. Kluczem
    w takim słowniku jest klucz główny (id) produktu, a wartością ilość tego produktu.
    '''
    from .models import Product

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


def delete_cart_cookie(response, cookie_name='cart'):
    response.set_cookie(cookie_name, expires=0)
    return response
