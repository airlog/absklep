
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
    from .models import Product, Property, product_property_assignment
    
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

@app.route("/auth/signin", methods=['GET', 'POST'])
def login():
    from flask import request
    from flask.ext.login import login_user
    from absklep.models import Customer

    if request.method == 'POST':
        form = absklep.forms.Login(request.form)
        if form.validate_on_submit():
            user = app.db.session.query(Customer).filter(Customer.email == form.email.data).first()
            if user is not None:
                if user.verify_password(form.pas.data) and login_user(user, remember=form.remember.data):
                    flash('Zalogowano do sklepu!')

                    # zalogowanie udane, powrót
                    return redirect(url_for('index'))
            flash('Niepoprawny login lub hasło')

        # zalogowanie nieudane
        return redirect(url_for('login'))

    return render_template('auth/signin.html',
                           logform=absklep.forms.Login())

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

@app.route('/orders/')
@login_required
def ordersview():
    from flask import g
    from .models import Order, Customer, Property
    
    if not g.current_user.is_authenticated():
        flash('Nie jestes zalogowany!')
        return redirect(url_for('index'))
    categories = Property.query.filter(Property.key=='Kategoria').order_by(Property.value).all()
    orders = g.current_user.orders
    return render_template('orders.html',
                           lorem=Markup(markdown(lorem, output='html5')),
                           random=randint(0, 0xFFFFFFFF),
                           logform=absklep.forms.Login(),
                           categories=categories,
                           orders=orders)

@app.route('/orders/show/<int:oid>/')
@login_required
def detailsview(oid):
    from flask import g
    from .models import Order, Property
    
    if not g.current_user.is_authenticated():
        flash('Nie jestes zalogowany!')
        return redirect(url_for('index'))
    
    categories = Property.query.filter(Property.key=='Kategoria').order_by(Property.value).all()
    orders = list(filter(lambda o: o.id == oid, g.current_user.orders))
#    print(orders[0].products_amount)
    return render_template('details.html',
                           lorem=Markup(markdown(lorem, output='html5')),
                           logform=absklep.forms.Login(),
                           categories=categories,
                           order=orders[0])

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
    from .models import Product, Comment, Customer, Property

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

@app.route('/panel/products/', methods=['GET', 'POST'])
def add_product_view():
	
    def get_properties_names(length):
        for i in range(length):
            yield 'propertyKey{}'.format(i), 'propertyValue{}'.format(i)

    from flask import request, g
    from .util import read_form

    if not g.current_user.is_authenticated() or g.current_user.__tablename__ != "Employees": return redirect(url_for('emplogin'))

    if request.method == 'POST':
        from .models import Product, Property

        try:
            # odczytywanie danych z formularza
            product_name = read_form('product_name')
            properties_count = read_form('properties_count', cast=int)
            category = read_form('category')
            unit_price = read_form('unit_price', cast=float)
            units_in_stock = read_form('units_in_stock', cast=int)
            description = read_form('description')
            properties = [(request.form[keyName], request.form[valueName]) for keyName, valueName in get_properties_names(properties_count)]

            # przefiltrowanie zbednych wartosci
            properties = list(
                filter(lambda t: t[0] is not None and len(t[0]) > 0 and t[1] is not None and len(t[1]) > 0,
                properties))

            # sprawdzanie czy taka kategoria juz istnieje
            # jesli nie, tworzymy nowa kategorie
            categoryObj = Property.get_object_by_tuple(Property.KEY_CATEGORY, category)
            if categoryObj is None:
                categoryObj = Property(Property.KEY_CATEGORY, category)

            # sprawdzanie czy dana para (cecha, wartosc) juz istnieje
            # jesli nie, tworzymy nowy obiekt
            propertiesObjs = []
            for key, value in properties:
                obj = Property.get_object_by_tuple(key, value)
                if obj is None:
                    obj = Property(key, value)
                propertiesObjs.append(obj)

            # tworzenie nowego produktu i dodawanie mu cech
            product = Product(product_name, unit_price, instock=units_in_stock, description=description)
            product.properties.extend(propertiesObjs)
            product.properties.append(categoryObj)

            app.db.session.add(product)
            app.db.session.commit()

            flash("Dodano produkt")
        except ValueError:
            flash('Dodanie produktu nieudane')

        return redirect(url_for('add_product_view'))

    return render_template('panel/add_product.html',
                           logform=absklep.forms.Login())

@app.route('/products/<int:pid>/observe/')
def observe_product(pid):
    
    from absklep.models import Product
    
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
	
    from absklep.models import Product
	
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
	
    from absklep.models import Property
	
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

@app.route('/cart/')
def cartview():
    def load_cart_cookie(cookie_name='cart'):
        '''
        Próbuje parsować zawartość koszyka, który powinień być zakodowanym w JSON słownikiem. Kluczem
        w takim słowniku jest klucz główny (id) produktu, a wartością ilość tego produktu.
        '''
        import json
        from flask import request
        from .models import Product

        jsonCart = request.cookies.get(cookie_name)
        if jsonCart is None or jsonCart == '':
            return {}

        obj = json.loads(jsonCart)
        if not isinstance(obj, dict):
            return {}

        cart = {}
        for key, value in obj.items():
            try:
                product = Product.query.get(int(key))
            except ValueError:
                continue

            if product is None:
                continue

            cart[product] = value

        return cart
    
    from .models import Property

    cart = load_cart_cookie()
    categories = Property.query.filter(Property.key=='Kategoria').order_by(Property.value)

    return render_template('cart.html',
                           lorem=Markup(markdown(lorem, output='html5')),
                           random=randint(0, 0xFFFFFFFF),
                           logform=absklep.forms.Login(),
                           cart=cart,
                           categories=categories)

@app.route('/products/<int:pid>/comments/new', methods=['POST'])
@login_required
def new_comment_product(pid):
    from flask import g, abort

    from .models import Comment, Product
    from .util import read_form
    
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


@app.route('/panel/', methods=['GET', 'POST'])
def emplogin():
    
    from flask import g, request
    from .models import Employee
    
    # pracownik jest juz zalogowany
    if g.current_user.is_authenticated() and g.current_user.__tablename__ == "Employees": return render_template('/panel/panel.html', logform=absklep.forms.Login())
    
    from .util import read_form
    from .forms import Emplogin
    from flask.ext.login import login_user
    
    emplogin = Emplogin(request.form)
    
    if emplogin.validate_on_submit():
        emp = app.db.session.query(Employee).filter(Employee.firstname == emplogin.fname.data, Employee.surname == emplogin.lname.data).first()
        if emp is not None:
            if emp.verify_password(emplogin.password.data) and login_user(emp):
                flash('Zalogowano do sklepu!')
                
                # zalogowanie udane, powrót
                return render_template('/panel/panel.html', logform=absklep.forms.Login())
        flash('Niepoprawne dane lub hasło')

    # zalogowanie nieudane, powrót
        
    
    return render_template('panel/login.html',
                            emplogin=emplogin)

@app.route('/panel/modify/', methods=['GET', 'POST'])
def modify_product():
    from flask import g, abort, request

    from .models import Product, Property, product_property_assignment
    from .util import read_form
    
    if not g.current_user.is_authenticated() or g.current_user.__tablename__ != "Employees": return redirect(url_for('emplogin'))
    
    if request.method == 'POST':
        try: 
            pid = int(read_form('pid'))
            product = Product.query.get(pid)
            return 'pid'
        except: pass
        
        try: cnt = int(read_form('count'))
        except: return render_template('panel/modify.html', logform=absklep.forms.Login())
        
        name = read_form('name')
        products = Product.query.filter(Product.name.like("%"+name+"%"))
        
        for i in range(1, cnt+1):
            k, v = read_form('param%d'% i ), read_form('val%d'% i )
            if k != '' and v != '':
                products = products.filter(Product.properties.any(key=k, value=v))
            
        return render_template('panel/choosemodify.html', logform=absklep.forms.Login(), products=products.all())
        		
    return render_template('panel/modify.html', logform=absklep.forms.Login())

@app.route('/panel/modify/<int:pid>/')
def modify_product_detail(pid):
    return str(pid)

@app.route('/panel/orders/')
@login_required
def panel_ordersview():

    from flask import g, request
    from .models import Employee
   		
    if not g.current_user.is_authenticated() or not g.current_user.__tablename__ == "Employees": 
        flash('Musisz się zalogować, żeby zobaczyć zamówienia')
        return redirect(url_for('index'))
   
    orders = g.current_user.orders
    return render_template('panel/orders.html',
                           lorem=Markup(markdown(lorem, output='html5')),
                           logform=absklep.forms.Login(),
                           orders = orders
                           )

@app.route('/panel/orders/show/<int:oid>/', methods=['GET', 'POST'])
@login_required
def panel_detailsview(oid):
    from flask import request, g
    from .util import read_form
    
    from .models import Order, Property
    
    if not g.current_user.is_authenticated() or not g.current_user.__tablename__ == "Employees": 
        flash('Musisz się zalogować')
        return redirect(url_for('index'))

    orders = list(filter(lambda o: o.id == oid, g.current_user.orders))
    if orders == []:
        flash('Zamówienie o podanym id nie istnieje')
        return redirect(url_for('panel_ordersview'))
    
    if request.method == 'POST':
        try:
            status = read_form('status')
            
            orders[0].set_status(status)
            app.db.session.commit()

            flash("Zmieniono status")
        except ValueError:
            flash('Wystąpił błąd podczas zmiany statusu')

        return redirect(url_for('panel_detailsview', **{'oid': oid}))

    return render_template('panel/details.html',
                           lorem=Markup(markdown(lorem, output='html5')),
                           logform=absklep.forms.Login(),
                           order=orders[0])

@app.route('/panel/archivals/')
@login_required
def panel_archivalsview():

    from flask import g, request
    from .models import Employee
   		
    if not g.current_user.is_authenticated() or not g.current_user.__tablename__ == "Employees": 
        flash('Musisz się zalogować, żeby zobaczyć zamówienia')
        return redirect(url_for('index'))
   
    archivals = g.current_user.archivals
    return render_template('panel/archivals.html',
                           lorem=Markup(markdown(lorem, output='html5')),
                           logform=absklep.forms.Login(),
                           archivals = archivals
                           )

@app.route('/panel/archivals/show/<int:aid>/')
@login_required
def panel_archival_detailsview(aid):

    from flask import g, request
    from .models import Employee
   		
    if not g.current_user.is_authenticated() or not g.current_user.__tablename__ == "Employees": 
        flash('Musisz się zalogować, żeby zobaczyć zamówienia')
        return redirect(url_for('index'))
   
    archivals = list(filter(lambda o: o.id == aid, g.current_user.archivals))
    if archivals == []:
        flash('Zamówienie o podanym id nie istnieje')
        return redirect(url_for('panel_archivalsview'))
        
    return render_template('panel/archival_details.html',
                           lorem=Markup(markdown(lorem, output='html5')),
                           logform=absklep.forms.Login(),
                           order=archivals[0])

@app.route('/panel/orders/show/<int:oid>/move_to_archivals', methods=['POST'])
@login_required
def move_to_archivals(oid):
    from flask import request, g
    
    from .models import Order, Archival, ProductAmount, ProductArchivalAmount 
    
    if not g.current_user.is_authenticated() or not g.current_user.__tablename__ == "Employees": 
        flash('Musisz się zalogować')
        return redirect(url_for('index'))

    orders = list(filter(lambda o: o.id == oid, g.current_user.orders))
    if orders == []:
        flash('Zamówienie o podanym id nie istnieje')
        return redirect(url_for('panel_ordersview'))
    
    if request.method == 'POST':
        try:            
            o = orders[0]
            archival = Archival().set_order_id(o.id).set_customer(o.customer_id).set_employee(o.employee_id)
            archival.set_price(o.price).set_date_ordered(o.date_ordered).set_status(o.status)
            archival.set_payment_method(o.payment_method).set_firstname(o.firstname).set_surname(o.surname)
            archival.set_address(o.address).set_city(o.city).set_postal_code(o.postal_code)
            
            for pa in o.products_amount:
                archival.products_amount.append(ProductArchivalAmount().set_amount(pa.amount).set_product(pa.product_id))
                app.db.session.delete(pa)
                
            app.db.session.delete(o)
            app.db.session.add(archival)
            app.db.session.commit()
            
            flash("Zarchiwizowano zamówienie o id: {}".format(o.id))
        except ValueError:
            flash('Wystąpił błąd podczas archiwizacji')

    return redirect(url_for('panel_ordersview'))

@app.route('/panel/orders/unassigned/')
@login_required
def panel_unassigned_orders_view():
    from flask import g, request
    from .models import Order
   		
    if not g.current_user.is_authenticated() or not g.current_user.__tablename__ == "Employees": 
        flash('Musisz się zalogować, żeby zobaczyć zamówienia')
        return redirect(url_for('index'))
   
    orders = list(filter( lambda o: o.employee_id == None, Order.query.all()))
    
    return render_template('panel/unassigned.html',
                           lorem=Markup(markdown(lorem, output='html5')),
                           logform=absklep.forms.Login(),
                           orders = orders
                           )
    
@app.route('/panel/orders/unassigned/show/<int:oid>/')
@login_required
def panel_unassigned_details_view(oid):
    from flask import g, request
    from .models import Order
   		
    if not g.current_user.is_authenticated() or not g.current_user.__tablename__ == "Employees": 
        flash('Musisz się zalogować, żeby zobaczyć zamówienia')
        return redirect(url_for('index'))
   
    orders = list(filter( lambda o: o.id == oid and o.employee_id == None, Order.query.all()))
    if orders == []:
        flash('Zamówienie o podanym id nie istnieje')
        return redirect(url_for('panel_unassigned_sview'))

    return render_template('panel/unassigned_details.html',
                           lorem=Markup(markdown(lorem, output='html5')),
                           logform=absklep.forms.Login(),
                           order = orders[0]
                           )

@app.route('/panel/orders/unassigned/show/<int:oid>/assign', methods=['POST'])
@login_required
def assign(oid):
    from flask import request, g
    
    from .models import Order, Employee
     
    if not g.current_user.is_authenticated() or not g.current_user.__tablename__ == "Employees": 
        flash('Musisz się zalogować')
        return redirect(url_for('index'))

    orders = list(filter( lambda o: o.id == oid and o.employee_id == None, Order.query.all()))
    if orders == []:
        flash('Zamówienie o podanym id nie istnieje')
        return redirect(url_for('panel_unassigned_sview'))
    
    if request.method == 'POST':
        try:            
            o = orders[0]
            o.set_employee(g.current_user.id)
            
            app.db.session.commit()
            
            flash("Zamówienie o id: {} zostało przydzielone.".format(o.id))
        except ValueError:
            flash('Wystąpił błąd')

    return redirect(url_for('panel_ordersview'))

