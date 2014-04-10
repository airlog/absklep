
from random import randint

from flask import render_template, redirect, url_for, flash
from flask.ext.login import current_user, login_required
from jinja2 import Markup
from markdown import markdown

from . import app, lorem
import absklep.forms

#some communicates for now
success = "Zostałeś zarejestrowany!"
fail = "Podany email już istnieje."

@app.route('/')
@app.route('/products/')
def index():
    from jinja2 import Markup
    from markdown import markdown
    from sqlalchemy import func    
    from .models import Product, Property
    
    def product_rate(product):
    	rates = [c.rate for c in product.comments]
    	return sum(rates)/len(rates) if len(rates) > 0 else 0
    
    categories = Property.query.filter(Property.key=='Kategoria').order_by(Property.value)
    products_best = sorted(Product.query.all(), key=product_rate)[:4]
    products_last = Product.query.order_by(Product.date_added.desc())[:4]

    return render_template('index.html',
                           lorem=Markup(markdown(lorem, output='html5')),
                           random=randint(0, 0xFFFFFFFF),
                           logform=absklep.forms.Login(),
                           categories=categories,
                           products_best=products_best,
                           products_last=products_last)

@app.route('/products/category/<int:cid>/')
def categoryview(cid):
    return render_template('category.html',
                           random=randint(0, 0xFFFFFFFF),
                           logform=absklep.forms.Login())

@app.route("/auth/signup", methods=['GET', 'POST'])
def register():
    from flask import request
    from absklep.models import Customer

    form = absklep.forms.Register(request.form)

    if request.method == 'POST':
        if form.validate_on_submit():
            if app.db.session.query(Customer).filter(Customer.email == form.email.data).scalar() is None:
                customer = Customer(str(form.email.data), str(form.pas.data))
                app.db.session.add(customer)
                app.db.session.commit()

                # rejestracja udana
                flash('Zostałeś zarejestrowany!')
                return redirect(url_for('index'))

            # blad rejestracji
            flash('Podany email już istnieje.')
            return redirect(url_for('register'))

    return render_template('auth/signup.html', form=form, logform=absklep.forms.Login(), message='')

@app.route("/auth/signin", methods=['POST'])
def login():
    from flask import request
    from flask.ext.login import login_user
    from absklep.models import Customer

    form = absklep.forms.Login(request.form)
    if form.validate_on_submit():
        user = app.db.session.query(Customer).filter(Customer.email == form.email.data).first()
        if user is not None:
            if user.verify_password(form.pas.data) and login_user(user, remember=form.remember.data):
                flash('Zalogowano do sklepu!')

                # zalogowanie udane, powrót
                return redirect(url_for('index'))
        flash('Niepoprawny login lub hasło')

    # zalogowanie nieudane, powrót
    return redirect(url_for('index'))

@app.route("/auth/signout/")
@login_required
def logout():
    from flask.ext.login import logout_user

    logout_user()
    flash('Wylogowano z systemu!')
    return redirect(url_for('index'))


@app.route('/orders/make')
def makeorderview():
    return render_template('address.html',
    	logform=absklep.forms.Login())

@app.route('/cart/')
def cartview():
    return render_template('cart.html',
                           lorem=Markup(markdown(lorem, output='html5')),
                           random=randint(0, 0xFFFFFFFF),
                           logform=absklep.forms.Login())

@app.route('/orders/')
def ordersview():
    return render_template('orders.html',
                           lorem=Markup(markdown(lorem, output='html5')),
                           random=randint(0, 0xFFFFFFFF),
                           logform=absklep.forms.Login())

@app.route('/observed/')
def observedview():
    return render_template('observed.html',
                           lorem=Markup(markdown(lorem, output='html5')))

@app.route('/orders/show/<int:oid>/')
def detailsview(oid):
    return render_template('details.html',
                           lorem=Markup(markdown(lorem, output='html5')))

#define error!!!
@app.route('/products/<int:pid>/')
def productview(pid):
    from absklep.models import Product, Comment, Customer, Property

    args = {"lorem": Markup(markdown(lorem, output='html5')), "random": randint(0, 0xFFFFFFFF),"logform": absklep.forms.Login()}

    product = Product.query.get(pid)
    if product is None: return 'error'

    comments = list(Comment.query.filter_by(product_id=pid))
    for c in comments: c.customer_id = Customer.query.get(c.customer_id).email

    properties = Property.query.filter(Product.properties.any(id=pid)).all()

    args['product'] = product
    args['comments'] = comments
    args['properties'] = properties
    args['rate'] = sum([ c.rate for c in comments ])//len(comments) if len(comments) > 0 else 0
    return render_template('product.html', **args)
