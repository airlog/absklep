
from flask import flash, g, redirect, render_template, url_for
from flask.ext.login import login_required

from .. import app
from ..forms import Login
from ..models import Product, Property
from ..util import only_customer

MAX_ON_PAGE = 20

@app.route('/products/<int:pid>/observe/')
@login_required
@only_customer()
def observe_product(pid):
    p = Product.query.get(pid)
    g.current_user.observed.append(p)
    app.db.session.commit()
    flash('Obserwujesz '+p.name)
    return redirect(url_for('observedview'))


@app.route('/products/<int:pid>/unobserve/')
@login_required
@only_customer()
def unobserve_product(pid):
    p = Product.query.get(pid)
    g.current_user.observed.remove(p)
    app.db.session.commit()
    flash('Nie obserwujesz już '+p.name)
    return redirect(url_for('observedview'))


@app.route('/observed/')
@app.route('/observed/sort/<sort>/')
@app.route('/observed/page/<page>/')
@app.route('/observed/page/<page>/sort/<sort>/')
@login_required
@only_customer()
def observedview(page=1, sort='name_up'):
    if page <= 0:
        page = 1
    items = g.current_user.observed
    if sort == 'price_up':
        items.sort(key=lambda p: p.unit_price)
    elif sort == 'price_down':
        items.sort(key=lambda p: p.unit_price, reverse=True)
    elif sort == 'name_down':
        items.sort(key=lambda p: p.name, reverse=True)
    else:
        items.sort(key=lambda p: p.name)
    
    return render_template('observed.html',
                           logform=Login(),
                           items=items[(page-1)*MAX_ON_PAGE : page*MAX_ON_PAGE],
                           user=g.current_user.email,
                           categories=Property.get_categories(),
                           page=page,
                           max=len(g.current_user.observed)/MAX_ON_PAGE,
                           sort=sort)


__all__ = ['observe_product', 'unobserve_product', 'observedview', ]
