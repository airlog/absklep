
from flask import abort, g, render_template

from .. import app
from ..forms import Login
from ..models import Product, Comment, Customer, Property


def is_allowed_to_comment(user, product):
    # niezalogowany nie może komentować
    if not user.is_authenticated():
        return False

    product_ordered = product.id in (p.product.id for order in user.orders for p in order.products_amount)
    already_commented = product.id in (c.product_id for c in user.comments)

    return product_ordered and not already_commented


@app.route('/products/<int:pid>/')
def productview(pid):
    args = {
        "logform": Login(),
    }

    product = Product.query.get(pid)
    if product is None:
        abort(500)

    comments = list(Comment.query.filter_by(product_id=pid))
    for c in comments:
        c.customer_id = Customer\
            .query\
            .get(c.customer_id)\
            .email

    properties = list(filter(lambda prop: prop.key != Property.KEY_CATEGORY, product.properties))
    properties.sort(key=lambda prop: prop.key)
    
    args['allow_comment'] = is_allowed_to_comment(g.current_user, product)
    args['product'] = product
    args['comments'] = comments
    args['properties'] = properties
    args['rate'] = sum([c.rate for c in comments ])//len(comments) if len(comments) > 0 else 0

    return render_template('product.html',
                           categories=Property.KEY_CATEGORY,
                           **args)


__all__ = ['productview', ]
