
from random import randint

from flask import render_template
from jinja2 import Markup
from markdown import markdown

from .. import app, lorem
import absklep.forms


#define error!!!
@app.route('/products/<int:pid>/')
def productview(pid):
    def is_allowed_to_comment(user, product):
        # niezalogowany nie może komentować
        if not user.is_authenticated():
            return False

        product_ordered = product.id in (p.product.id for order in user.orders for p in order.products_amount)
        already_commented = product.id in (c.product_id for c in user.comments)

        return product_ordered and not already_commented

    from flask import abort, g
    from ..models import Product, Comment, Customer, Property

    args = {
        "lorem": Markup(markdown(lorem, output='html5')),
        "random": randint(0, 0xFFFFFFFF),
        "logform": absklep.forms.Login(),
    }

    product = Product.query.get(pid)
    if product is None:
        abort(500)

    comments = list(Comment.query.filter_by(product_id=pid))
    for c in comments: c.customer_id = Customer.query.get(c.customer_id).email

    categories = Property.query.filter(Property.key=='Kategoria').order_by(Property.value).all()
    properties = list(filter(lambda prop: prop.key !='Kategoria', product.properties))
    properties.sort(key=lambda prop: prop.key)
    
    args['allow_comment'] = is_allowed_to_comment(g.current_user, product)
    args['product'] = product
    args['comments'] = comments
    args['properties'] = properties
    args['rate'] = sum([ c.rate for c in comments ])//len(comments) if len(comments) > 0 else 0
    return render_template('product.html', categories=categories, **args)


__all__ = ['productview', ]
