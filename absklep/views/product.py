
from flask import abort, flash, g, render_template, request, redirect, url_for
from flask.ext.login import login_required

from .. import app
from ..forms import Login
from ..models import Comment, Customer, Product, Property
from ..util import read_form, only_employee


def is_allowed_to_comment(user, product):
    # niezalogowany nie może komentować
    if not user.is_authenticated():
        return False

    product_ordered = product.id in (p.product.id for order in user.orders for p in order.products_amount)
    already_commented = product.id in (c.product_id for c in user.comments)

    return product_ordered and not already_commented


@app.route('/products/<int:pid>/')
def productview(pid):
    args = {
        "logform": Login(),
    }

    product = Product.query.get(pid)
    if product is None:
        abort(500)

    comments = list(Comment.query.filter_by(product_id=pid))
    for c in comments:
        c.customer_id = Customer\
            .query\
            .get(c.customer_id)\
            .email

    properties = list(filter(lambda prop: prop.key != Property.KEY_CATEGORY, product.properties))
    properties.sort(key=lambda prop: prop.key)
    
    args['allow_comment'] = is_allowed_to_comment(g.current_user, product)
    args['product'] = product
    args['comments'] = comments
    args['properties'] = properties
    args['rate'] = sum([c.rate for c in comments ])//len(comments) if len(comments) > 0 else 0

    return render_template('product.html',
                           categories=Property.KEY_CATEGORY,
                           **args)


@app.route('/panel/products/', methods=['GET', 'POST'])
@only_employee('/panel/')
def add_product_view():
    def get_properties_names(length):
        for i in range(length):
            yield 'propertyKey{}'.format(i), 'propertyValue{}'.format(i)

    if request.method == 'POST':
        try:
            # odczytywanie danych z formularza
            product_name = read_form('product_name')
            properties_count = read_form('properties_count', cast=int)
            category = read_form('category')
            unit_price = int(read_form('unit_price').replace('.',""))
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
                           logform=Login())


@app.route('/panel/modify/', methods=['GET', 'POST'])
@only_employee('/panel/')
def modify_product():
    if request.method == 'POST':
        try:
            pid = int(read_form('pid'))
            product = Product.query.get(pid)
            if product is not None:
                return redirect(url_for('modify_product_detail', pid=pid))
            flash('Produkt o podanym id nie istnieje')
            return redirect(url_for('modify_product'))
        except:
            pass

        try:
            cnt = int(read_form('count'))
        except:
            return render_template('panel/modify.html', logform=Login())

        name = read_form('name')
        products = Product\
            .query\
            .filter(Product.name.like("%"+name+"%"))\
            .all()

        for i in range(1, cnt+1):
            k, v = read_form('param%d' % i), read_form('val%d' % i)
            if k != '' and v != '':
                products = products.filter(Product.properties.any(key=k, value=v))

        return render_template('panel/choosemodify.html',
                               logform=Login(),
                               products=products)

    return render_template('panel/modify.html',
                           logform=Login())


@app.route('/panel/modify/<int:pid>/', methods=['GET', 'POST'])
@only_employee('/panel/')
def modify_product_detail(pid):
    product = Product.query.get(pid)

    if request.method == 'POST':
        
        #co pracownik chce zmienic w produkcie
        to_change = read_form('attr')
        
        #zmiana wartosci parametru, ktory juz byl prypisany do produktu
        if to_change == 'property':
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
        #dodanie nowej pary klucz, wartosc
        elif to_change == 'add_property':
            key, val = read_form('key'), read_form('nval')

            p = Property.query.filter(Property.key==key, Property.value==val).first()
            if p is None:
                flash('Taki parametr nie istnieje, najpierw musisz go dodać z głównego menu')
                render_template('panel/modify_details.html', product=product)
            product.properties.append(p)
        #reszta
        else:
            if to_change == 'unit_price':
                setattr(product, to_change, int(read_form('nval').replace('.',"")))                
            else:
                setattr(product, to_change, read_form('nval'))

        app.db.session.commit()
        flash('Produkt został zmieniony')
        product = Product.query.get(pid)

    return render_template('panel/modify_details.html',
                           product=product)


@app.route('/panel/modify/<int:pid>/remove/')
@only_employee('/panel/')
def remove_product(pid):
    app.db.session.delete(Product.query.get(pid))
    app.db.session.commit()

    flash('Produkt został usunięty')
    return redirect(url_for('modify_product'))


__all__ = ['productview', 'add_product_view', 'modify_product', 'modify_product_detail', 'remove_product', ]
