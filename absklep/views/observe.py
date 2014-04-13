
from flask import flash, redirect, render_template, url_for
from flask.ext.login import current_user
from markdown import markdown
from jinja2 import Markup

from .. import app, lorem
import absklep.forms

@app.route('/products/<int:pid>/observe/')
def observe_product(pid):

    from ..models import Product

    if current_user.is_anonymous():
        flash('Musisz się zalogować, żeby obserwować produkty')
        return redirect(url_for('productview', pid=pid))

    p = Product.query.get(pid)
    current_user.observed.append(p)
    app.db.session.commit()
    flash('Obserwujesz '+p.name)
    return redirect(url_for('index'))

@app.route('/products/<int:pid>/unobserve/')
def unobserve_product(pid):

    from ..models import Product

    if current_user.is_anonymous():
        flash('Musisz się zalogować, żeby obserwować produkty')
        return redirect(url_for('productview', pid=pid))

    p = Product.query.get(pid)
    current_user.observed.remove(p)
    app.db.session.commit()
    flash('Obserwujesz '+p.name)
    return redirect(url_for('observedview'))

@app.route('/observed/')
def observedview():

    from ..models import Property

    categories = Property.query.filter(Property.key=='Kategoria').order_by(Property.value)

    if current_user.is_anonymous():
        flash('Musisz się zalogować, żeby obserwować produkty')
        return redirect(url_for('index'))

    return render_template('observed.html',
                           lorem=Markup(markdown(lorem, output='html5')),
                           logform=absklep.forms.Login(),
                           items=current_user.observed,
                           user=current_user.email,
                           categories=categories)


__all__ = ['observe_product', 'unobserve_product', 'observedview', ]
