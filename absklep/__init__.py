
from flask import Flask, request, render_template, flash, url_for, redirect
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, login_user, current_user, logout_user, login_required

from jinja2 import Markup
from markdown import markdown

from random import randint

__version__ = "0.1.0"

app = Flask(__name__)
app.db = SQLAlchemy(app)

lorem = 'dummy'
with open('lorem.txt') as file: lorem = file.read()

import absklep.controllers
import absklep.models
import absklep.views
import absklep.forms

absklep.controllers.load_config(app, package=__name__)
#absklep.controllers.load_database(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

#some communicates for now
success = "Zostałeś zarejestrowany!"
fail = "Podany email już istnieje."

@app.route('/')
@app.route('/products/')
def index():
    from jinja2 import Markup
    from markdown import markdown
    if current_user.is_authenticated():
        return render_template('index.html',
                           lorem=Markup(markdown(lorem, output='html5')),
                           random=randint(0, 0xFFFFFFFF),
                           logform=absklep.forms.Login(),
                           user = current_user.email)
    return render_template('index.html',
                           lorem=Markup(markdown(lorem, output='html5')),
                           random=randint(0, 0xFFFFFFFF),
                           logform=absklep.forms.Login())


@app.route("/auth/signup", methods=['GET', 'POST'])
def register():
    from absklep.models import Customer
    
    form = absklep.forms.Register(request.form)
    
    if form.validate_on_submit():
        if app.db.session.query(Customer).filter(Customer.email == form.email.data).scalar() is None:
            customer = Customer(str(form.email.data), str(form.pas.data))
            app.db.session.add(customer)
            app.db.session.commit()
            #flash('Zostałeś zarejestrowany!')
            return redirect(url_for('login'))
        flash('Podany email już istnieje.')
        return render_template('auth/signup.html', form=form, logform=absklep.forms.Login(), message='')
    return render_template('auth/signup.html', form=form, logform=absklep.forms.Login(), message='')


@app.route("/auth/signin", methods=['GET', 'POST'])
def login():
    from absklep.models import Customer

    form = absklep.forms.Login(request.form)
    
    if form.validate_on_submit():
        	
        user = app.db.session.query(Customer).filter(Customer.email == form.email.data).first()
        if user is not None:
            if not user.verify_password(form.pas.data):
                flash('Niepoprawny login lub hasło')
                return render_template('index.html', form=form, message='haslo nieprawidlowe', logform=form)
            if login_user(user, remember=form.remember.data):
                return render_template('index.html', user=current_user.email, logform=form, mmessage='')
        return fail
    return render_template('index.html', logform=form, message='')

@app.route("/auth/signout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

#define error!!!
@app.route('/products/<int:pid>/')
def productview(pid):
    from absklep.models import Product, Comment, Customer, Property
	
    args = {"lorem": Markup(markdown(lorem, output='html5')), "random": randint(0, 0xFFFFFFFF),"logform": absklep.forms.Login()}
    
    if current_user.is_authenticated(): args['user'] = current_user.email
    
    product = Product.query.get(pid)
    if product is None: return 'error'
    
    comments = list(Comment.query.filter_by(product_id=pid))
    for c in comments: c.customer_id = Customer.query.get(c.customer_id).email
    
    properties = Property.query.filter(Product.properties.any(id=pid)).all()
    
    args['product'] = product
    args['comments'] = comments
    args['properties'] = properties
    args['rate'] = sum([ c.rate for c in comments ])//len(comments)
    return render_template('product.html',
                           **args)
                           

@login_manager.user_loader
def load_user(uid):
    from absklep.models import Customer

    return Customer.query.get(uid)
