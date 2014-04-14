
from flask import flash, g, redirect, render_template, url_for
from flask.ext.login import login_required

from .. import app
from ..forms import Login
from ..models import Product, Property


@app.route('/products/<int:pid>/observe/')
@login_required
def observe_product(pid):
    p = Product.query.get(pid)
    g.current_user.observed.append(p)
    app.db.session.commit()
    flash('Obserwujesz '+p.name)
    return redirect(url_for('index'))


@app.route('/products/<int:pid>/unobserve/')
@login_required
def unobserve_product(pid):
    p = Product.query.get(pid)
    g.current_user.observed.remove(p)
    app.db.session.commit()
    flash('Obserwujesz '+p.name)
    return redirect(url_for('observedview'))


@app.route('/observed/')
@login_required
def observedview():
    return render_template('observed.html',
                           logform=Login(),
                           items=g.current_user.observed,
                           user=g.current_user.email,
                           categories=Property.get_categories())


__all__ = ['observe_product', 'unobserve_product', 'observedview', ]
