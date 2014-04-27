
from flask import abort, flash, g, make_response, redirect, render_template, request, url_for
from flask.ext.login import login_required

from .. import app
from ..controllers import load_cart_cookie, delete_cart_cookie
from ..forms import Login
from ..models import Property, ProductAmount, Order
from ..util import read_form, only_employee


MAX_ON_PAGE = 10

@app.route('/orders/')
@app.route('/orders/page/<int:page>/')
@app.route('/orders/sort/<sort>/')
@app.route('/orders/page/<int:page>/sort/<sort>/')
@login_required
def ordersview(page=1, sort='date_down'):
    if page <= 0:
        page = 1
    orders = g.current_user.orders
    archivals = g.current_user.archivals
    
    all_orders = [('archival', a) for a in archivals] + [('order', o) for o in orders]

    if sort == 'date_up':
        all_orders.sort(key=lambda o: o[1].date_ordered)
    else:
        all_orders.sort(key=lambda o: o[1].date_ordered, reverse=True)
    
    return render_template('orders.html',
                           logform=Login(),
                           categories=Property.get_categories(),
                           orders=all_orders[(page-1)*MAX_ON_PAGE:page*MAX_ON_PAGE],
                           page=page,
                           max=len(all_orders)/MAX_ON_PAGE,
                           sort=sort)


@app.route('/orders/show/<int:oid>/')
@login_required
def detailsview(oid):
    orders = list(filter(lambda o: o.id == oid, g.current_user.orders))
    return render_template('details.html',
                           logform=Login(),
                           categories=Property.get_categories(),
                           order=orders[0])

@app.route('/orders/show/<int:oid>/archival/')
@login_required
def archival_details_view(oid):
    archivals = list(filter(lambda o: o.id == oid, g.current_user.archivals))
    return render_template('archival_details.html',
                           logform=Login(),
                           categories=Property.get_categories(),
                           order=archivals[0])


@app.route('/orders/new', methods=['GET', 'POST'])
@login_required
def makeorderview():
    def get():
        return render_template('address.html',
                               logform=Login(),
                               cart=load_cart_cookie(),
                               payment_methods=Order.ENUM_PAYMENT_METHODS_VALUES[:])

    def post():
        def cast_payment_method(txt):
            if txt not in Order.ENUM_PAYMENT_METHODS_VALUES:
                 raise ValueError()
            return txt

        def cast_nonempty_str(txt):
            if txt is not None and len(txt) > 0:
                return txt
            return None

        failureMethod, successMethod = 'makeorderview', 'ordersview'
        cart = load_cart_cookie()

        # koszyk jest pusty
        if len(cart) <= 0:
            flash('Żeby złożyć zamówienie najpierw wypełnij koszyk!')
            return redirect(url_for(failureMethod))

        try:
            name, surname = read_form('name'), read_form('surname')
            house, apartment = read_form('housenum'), read_form('apartmentnum', allow_none=True, cast=cast_nonempty_str)
            street, postal, city = read_form('street'), read_form('postalcode'), read_form('city')
            payment = read_form('payment', cast=cast_payment_method)
            address = '{}/{}'.format(house, apartment) if apartment is not None else house
        except ValueError:
            flash('Wystąpił błąd podczas przetwarzania żądania!')
            return redirect(url_for(failureMethod))

        # tworzenie obiektów do bazy danych
        price = sum((product.unit_price * int(amount) for product, amount in cart.items()))
        paIter = (ProductAmount(amount).set_product(product) for product, amount in cart.items())

        order = Order()\
            .set_price(price)\
            .set_customer(g.current_user.id)\
            .set_firstname(name)\
            .set_surname(surname)\
            .set_address(address)\
            .set_city(city)\
            .set_postal_code(postal)\
            .set_payment_method(payment)\
            .done()
        for pa in paIter:
            order.add_product_amount(pa)

        # zapisanie zmian w bazie danych
        try:
            app.db.session.add(order)
            app.db.session.commit()
        except:  # TODO: bardziej szczegółowo łapać
            abort(500)

        flash('Zamówienie złożone')
        return delete_cart_cookie(make_response(redirect(url_for(successMethod))))

    try:
        return {'GET': get, 'POST': post, }[request.method.upper()]()
    except KeyError:
        abort(405)


@app.route('/panel/orders/')
@app.route('/panel/orders/page/<int:page>/')
@app.route('/panel/orders/sort/<sort>/')
@app.route('/panel/orders/page/<int:page>/sort/<sort>/')
@only_employee('/panel/', message='Musisz sie zalogować żeby zobaczyć zamówienia!')
def panel_ordersview(page=1, sort='date_down'):

    if page <= 0:
        page = 1
        
    orders = g.current_user.orders

    if sort == 'date_up':
        orders.sort(key=lambda o: o.date_ordered)
    elif sort == 'number_up':
        orders.sort(key=lambda o: o.id)
    elif sort == 'number_down':
        orders.sort(key=lambda o: o.id, reverse=True)
    else:
        orders.sort(key=lambda o: o.date_ordered, reverse=True)

    return render_template('panel/orders.html',
                           logform=Login(),
                           orders=orders[(page-1)*MAX_ON_PAGE:page*MAX_ON_PAGE],
                           page=page,
                           max=len(orders)/MAX_ON_PAGE,
                           sort=sort)


@app.route('/panel/orders/show/<int:oid>/', methods=['GET', 'POST'])
@only_employee('/panel/', message='Musisz sie zalogować!')
def panel_detailsview(oid):
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
                           logform=Login(),
                           order=orders[0])


@app.route('/panel/orders/unassigned/')
@app.route('/panel/orders/unassigned/page/<int:page>/')
@app.route('/panel/orders/unassigned/sort/<sort>/')
@app.route('/panel/orders/unassigned/page/<int:page>/sort/<sort>/')
@only_employee('/panel/', message='Musisz sie zalogować żeby zobaczyć zamówienia!')
def panel_unassigned_orders_view(page=1, sort='date_down'):

    if page <= 0:
        page = 1
        
    orders = list(filter(lambda o: o.employee_id == None, Order.query.all()))

    if sort == 'date_up':
        orders.sort(key=lambda o: o.date_ordered)
    elif sort == 'number_up':
        orders.sort(key=lambda o: o.id)
    elif sort == 'number_down':
        orders.sort(key=lambda o: o.id, reverse=True)
    else:
        orders.sort(key=lambda o: o.date_ordered, reverse=True)

    return render_template('panel/unassigned.html',
                           logform=Login(),
                           orders=orders[(page-1)*MAX_ON_PAGE:page*MAX_ON_PAGE],
                           page=page,
                           max=len(orders)/MAX_ON_PAGE,
                           sort=sort)


@app.route('/panel/orders/unassigned/show/<int:oid>/')
@only_employee('/panel/', message='Musisz sie zalogować żeby zobaczyć zamówienia!')
def panel_unassigned_details_view(oid):
    orders = list(filter(lambda o: o.id == oid and o.employee_id is None, Order.query.all()))
    if orders == []:
        flash('Zamówienie o podanym id nie istnieje')
        return redirect(url_for('panel_unassigned_sview'))

    return render_template('panel/unassigned_details.html',
                           logform=Login(),
                           order=orders[0])


@app.route('/panel/orders/unassigned/show/<int:oid>/assign', methods=['POST'])
@only_employee('/panel/', message='Musisz sie zalogować żeby zobaczyć zamówienia!')
def assign(oid):
    orders = list(filter( lambda o: o.id == oid and o.employee_id is None, Order.query.all()))
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


__all__ = ['ordersview', 'detailsview', 'makeorderview',
           'panel_ordersview', 'panel_detailsview', 'panel_unassigned_orders_view', 'panel_unassigned_details_view',
           'assign', ]
