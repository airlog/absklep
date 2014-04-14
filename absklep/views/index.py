
from flask import abort, flash, g, redirect, render_template, url_for
from flask.ext.login import login_required

from .. import app
from ..forms import Login
from ..models import Product, Property, Comment
from ..util import read_form

MAX_ON_PAGE = 10

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
@app.route('/products/category/<int:cid>/sort/<sort>/')
@app.route('/products/category/<int:cid>/page/<int:page>/')
@app.route('/products/category/<int:cid>/page/<int:page>/sort/<sort>/')
def categoryview(cid, page=1, sort='name_up'):
    from ..models import Product, Property, product_property_assignment

    if page <= 0:
        page = 1
    
    products = Product\
        .query\
        .join(product_property_assignment, Product.id == product_property_assignment.columns.product_id)\
        .filter(product_property_assignment.columns.property_id == cid)\
        .all()

    category = Property\
        .query\
        .filter(Property.id == cid)\
        .first()

    if sort == 'price_up':
        products.sort(key=lambda p: p.unit_price)
    elif sort == 'price_down':
        products.sort(key=lambda p: p.unit_price, reverse=True)
    elif sort == 'name_down':
        products.sort(key=lambda p: p.name, reverse=True)
    else:
        products.sort(key=lambda p: p.name)
        
    return render_template('category.html',
                           logform=Login(),
                           categories=Property.get_categories(),
                           products=products[(page-1)*MAX_ON_PAGE:page*MAX_ON_PAGE],
                           category=category,
                           page=page,
                           max=len(products)/MAX_ON_PAGE,
                           sort=sort)


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
