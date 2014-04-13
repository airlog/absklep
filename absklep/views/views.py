
from random import randint

from flask import render_template, redirect, url_for, flash
from flask.ext.login import current_user, login_required
from jinja2 import Markup
from markdown import markdown

from .. import app
import absklep.forms

#some communicates for now
success = "Zostałeś zarejestrowany!"
fail = "Podany email już istnieje."


@app.route('/panel/products/', methods=['GET', 'POST'])
def add_product_view():
	
    def get_properties_names(length):
        for i in range(length):
            yield 'propertyKey{}'.format(i), 'propertyValue{}'.format(i)

    from flask import request, g
    from ..util import read_form

    if not g.current_user.is_authenticated() or g.current_user.__tablename__ != "Employees": return redirect(url_for('emplogin'))

    if request.method == 'POST':
        from ..models import Product, Property

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


@app.route('/panel/', methods=['GET', 'POST'])
def emplogin():
    
    from flask import g, request
    from ..models import Employee
    
    # pracownik jest juz zalogowany
    if g.current_user.is_authenticated() and g.current_user.__tablename__ == "Employees": return render_template('/panel/panel.html', logform=absklep.forms.Login())
    
    from ..util import read_form
    from ..forms import Emplogin
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

    from ..models import Product, Property, product_property_assignment
    from ..util import read_form
    
    if not g.current_user.is_authenticated() or g.current_user.__tablename__ != "Employees": return redirect(url_for('emplogin'))
    
    if request.method == 'POST':
        try: 
            pid = int(read_form('pid'))
            product = Product.query.get(pid)
            if product is not None: return redirect(url_for('modify_product_detail', pid=pid))
            flash('Produkt o podanym id nie istnieje')
            return render_template('panel/modify.html', logform=absklep.forms.Login())
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


@app.route('/panel/modify/<int:pid>/', methods=['GET', 'POST'])
def modify_product_detail(pid):
    from flask import g, request

    from ..models import Product, Property
    from ..util import read_form
    
    if not g.current_user.is_authenticated() or g.current_user.__tablename__ != "Employees": return redirect(url_for('emplogin'))
    
    product = Product.query.get(pid)
    
    if request.method == 'POST':
        if read_form('attr') == 'n': product.name = read_form('nval')
        elif read_form('attr') == 'p': product.unit_price = read_form('nval')
        elif read_form('attr') == 'a': product.units_in_stock = read_form('nval')
        elif read_form('attr') == 'd': product.description = read_form('nval')
        elif read_form('attr') == 'r':
            key, val = read_form('key'), read_form('nval')
            
            if read_form('mode')=='rm':
                product.properties = [ x for x in product.properties if x.key != key ]
            else:
                p = Property.query.filter(Property.key==key, Property.value==val).first()
                if p is None:
                    flash('Taki parametr nie istnieje, najpierw musisz go dodać z głównego menu')
                    render_template('panel/modify_details.html', product=product)
                product.properties = [ x for x in product.properties if x.key != key ]
                product.properties.append(p)
        elif read_form('attr') == 'ap':
            key, val = read_form('key'), read_form('nval')
            
            p = Property.query.filter(Property.key==key, Property.value==val).first()
            if p is None:
                flash('Taki parametr nie istnieje, najpierw musisz go dodać z głównego menu')
                render_template('panel/modify_details.html', product=product)
            product.properties.append(p)
        flash('Produkt został zmieniony')
        product = Product.query.get(pid)
    
    return render_template('panel/modify_details.html', product=product)

@app.route('/panel/modify/<int:pid>/remove/')
def remove_product(pid):
    from flask import g
    from ..models import Product
    
    if not g.current_user.is_authenticated() or g.current_user.__tablename__ != "Employees": return redirect(url_for('emplogin'))
    
    #return Product.query.get(pid).name
    app.db.session.delete(Product.query.get(pid))
    app.db.session.commit()
    flash('Produkt został usunięty')
    return redirect(url_for('modify_product'))
    
    
@app.route('/panel/addparam/', methods=['GET', 'POST'])
def addparam():
    from flask import g, request
    from ..models import Property
    from ..util import read_form
    
    if not g.current_user.is_authenticated() or g.current_user.__tablename__ != "Employees": return redirect(url_for('emplogin'))
    
    if request.method == 'POST':
        app.db.session.add(Property(read_form('key'), read_form('val')))
        app.db.session.commit()
        flash('Dodano')
    
    return render_template('panel/addparam.html')



@app.route('/panel/orders/')
@login_required
def panel_ordersview():

    from flask import g, request
    from ..models import Employee
   		
    if not g.current_user.is_authenticated() or not g.current_user.__tablename__ == "Employees": 
        flash('Musisz się zalogować, żeby zobaczyć zamówienia')
        return redirect(url_for('index'))
   
    orders = g.current_user.orders
    return render_template('panel/orders.html',
                           logform=absklep.forms.Login(),
                           orders = orders
                           )


@app.route('/panel/orders/show/<int:oid>/', methods=['GET', 'POST'])
@login_required
def panel_detailsview(oid):
    from flask import request, g
    from ..util import read_form
    
    from ..models import Order, Property
    
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
                           logform=absklep.forms.Login(),
                           order=orders[0])


@app.route('/panel/archivals/')
@login_required
def panel_archivalsview():

    from flask import g, request
    from ..models import Employee
   		
    if not g.current_user.is_authenticated() or not g.current_user.__tablename__ == "Employees": 
        flash('Musisz się zalogować, żeby zobaczyć zamówienia')
        return redirect(url_for('index'))
   
    archivals = g.current_user.archivals
    return render_template('panel/archivals.html',
                           logform=absklep.forms.Login(),
                           archivals = archivals
                           )


@app.route('/panel/archivals/show/<int:aid>/')
@login_required
def panel_archival_detailsview(aid):

    from flask import g, request
    from ..models import Employee
   		
    if not g.current_user.is_authenticated() or not g.current_user.__tablename__ == "Employees": 
        flash('Musisz się zalogować, żeby zobaczyć zamówienia')
        return redirect(url_for('index'))
   
    archivals = list(filter(lambda o: o.id == aid, g.current_user.archivals))
    if archivals == []:
        flash('Zamówienie o podanym id nie istnieje')
        return redirect(url_for('panel_archivalsview'))
        
    return render_template('panel/archival_details.html',
                           logform=absklep.forms.Login(),
                           order=archivals[0])


@app.route('/panel/orders/show/<int:oid>/move_to_archivals', methods=['POST'])
@login_required
def move_to_archivals(oid):
    from flask import request, g
    
    from ..models import Order, Archival, ProductAmount, ProductArchivalAmount
    
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
    from ..models import Order
   		
    if not g.current_user.is_authenticated() or not g.current_user.__tablename__ == "Employees": 
        flash('Musisz się zalogować, żeby zobaczyć zamówienia')
        return redirect(url_for('index'))
   
    orders = list(filter( lambda o: o.employee_id == None, Order.query.all()))
    
    return render_template('panel/unassigned.html',
                           logform=absklep.forms.Login(),
                           orders = orders
                           )


@app.route('/panel/orders/unassigned/show/<int:oid>/')
@login_required
def panel_unassigned_details_view(oid):
    from flask import g, request
    from ..models import Order
   		
    if not g.current_user.is_authenticated() or not g.current_user.__tablename__ == "Employees": 
        flash('Musisz się zalogować, żeby zobaczyć zamówienia')
        return redirect(url_for('index'))
   
    orders = list(filter( lambda o: o.id == oid and o.employee_id == None, Order.query.all()))
    if orders == []:
        flash('Zamówienie o podanym id nie istnieje')
        return redirect(url_for('panel_unassigned_sview'))

    return render_template('panel/unassigned_details.html',
                           logform=absklep.forms.Login(),
                           order = orders[0]
                           )


@app.route('/panel/orders/unassigned/show/<int:oid>/assign', methods=['POST'])
@login_required
def assign(oid):
    from flask import request, g
    
    from ..models import Order, Employee
     
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

