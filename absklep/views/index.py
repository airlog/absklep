
from flask import abort, flash, g, redirect, render_template, url_for
from flask.ext.login import login_required

from .. import app
from ..forms import Login
from ..models import Product, Property, Comment
from ..util import read_form


@app.route('/')
@app.route('/products/')
def index():
    def product_rate(product):
        rates = [c.rate for c in product.comments]
        return sum(rates)/len(rates) if len(rates) > 0 else 0

    products_best = Product\
        .query\
        .all()
    products_best.sort(key=lambda p: product_rate(p), reverse=True)
    products_last = Product\
        .query\
        .order_by(Product.date_added.desc())\
        .all()

    return render_template('index.html',
                           logform=Login(),
                           categories=Property.get_categories(),
                           products_best=products_best[0:4],
                           products_last=products_last[0:4])


@app.route('/products/category/<int:cid>/')
def categoryview(cid):
    from ..models import Product, Property, product_property_assignment

    products = Product\
        .query\
        .join(product_property_assignment, Product.id == product_property_assignment.columns.product_id)\
        .filter(product_property_assignment.columns.property_id == cid)\
        .all()

    category = Property\
        .query\
        .filter(Property.id == cid)\
        .first()

    return render_template('category.html',
                           logform=Login(),
                           categories=Property.get_categories(),
                           products=products,
                           category=category)


@app.route('/products/<int:pid>/comments/new', methods=['POST'])
@login_required
def new_comment_product(pid):
    user = g.current_user
    product = Product.query.get(pid)

    # to raczej nigdy nie powinno się stać, ale warto o to zadbać
    if product is None:
        return abort(500)

    try:
        comment_text = read_form('comment')
        rate = read_form('rate', cast=int)

        if rate not in Comment.RATE_ALLOWED_VALUES:
            raise ValueError()
        if comment_text == '' or len(comment_text) <= 0:
            raise ValueError()

        comment = Comment(product.id, user.id, rate, comment_text)
        app.db.session.add(comment)
        app.db.session.commit()

        flash('Dodano komentarz')
    except ValueError:
        flash('Dodawanie komentarza nieudane!')

    return redirect(url_for('productview', **{'pid': pid}))


__all__ = ['index', 'categoryview', 'new_comment_product', ]
