
from random import randint

from flask import flash, redirect, render_template, url_for

from .. import app
import absklep.forms

@app.route('/')
@app.route('/products/')
def index():
    from jinja2 import Markup
    from markdown import markdown
    from sqlalchemy import func
    from ..models import Product, Property

    def product_rate(product):
    	rates = [c.rate for c in product.comments]
    	return sum(rates)/len(rates) if len(rates) > 0 else 0

    categories = Property.query.filter(Property.key=='Kategoria').order_by(Property.value).all()
    products_best = Product.query.all()
    products_best.sort(key=lambda p: product_rate(p), reverse=True)
    products_last = Product.query.order_by(Product.date_added.desc())

    return render_template('index.html',
                           lorem=Markup(markdown(lorem, output='html5')),
                           random=randint(0, 0xFFFFFFFF),
                           logform=absklep.forms.Login(),
                           categories=categories,
                           products_best=products_best[0:4],
                           products_last=products_last[0:4])


@app.route('/products/category/<int:cid>/')
def categoryview(cid):
    from ..models import Product, Property, product_property_assignment

    products = Product.query\
        .join(product_property_assignment, Product.id == product_property_assignment.columns.product_id)\
        .filter(product_property_assignment.columns.property_id == cid)\
        .all()

    categories = Property.query.filter(Property.key=='Kategoria').order_by(Property.value).all()
    category = Property.query.filter(Property.id == cid).first()

    return render_template('category.html',
                           random=randint(0, 0xFFFFFFFF),
                           logform=absklep.forms.Login(),
                           categories=categories,
                           products=products,
                           category=category)


@app.route('/products/<int:pid>/comments/new', methods=['POST'])
@login_required
def new_comment_product(pid):
    from flask import g, abort

    from ..models import Comment, Product
    from ..util import read_form

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
