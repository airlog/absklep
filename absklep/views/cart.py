
from random import randint

from flask import render_template
from jinja2 import Markup
from markdown import markdown

from .. import app, lorem
import absklep.forms


@app.route('/cart/')
def cartview():
    def load_cart_cookie(cookie_name='cart'):
        '''
        Próbuje parsować zawartość koszyka, który powinień być zakodowanym w JSON słownikiem. Kluczem
        w takim słowniku jest klucz główny (id) produktu, a wartością ilość tego produktu.
        '''
        import json
        from flask import request
        from ..models import Product

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

    from ..models import Property

    cart = load_cart_cookie()
    categories = Property.query.filter(Property.key=='Kategoria').order_by(Property.value)

    return render_template('cart.html',
                           lorem=Markup(markdown(lorem, output='html5')),
                           random=randint(0, 0xFFFFFFFF),
                           logform=absklep.forms.Login(),
                           cart=cart,
                           categories=categories)


__all__ = ['cartview', ]
