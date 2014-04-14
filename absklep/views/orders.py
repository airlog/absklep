
from flask import flash, g, redirect, render_template, request, url_for
from flask.ext.login import login_required

from .. import app
from ..forms import Login
from ..models import Property, Order
from ..util import read_form


@app.route('/orders/')
@login_required
def ordersview():
    orders = g.current_user.orders
    return render_template('orders.html',
                           logform=Login(),
                           categories=Property.get_categories(),
                           orders=orders)


@app.route('/orders/show/<int:oid>/')
@login_required
def detailsview(oid):
    orders = list(filter(lambda o: o.id == oid, g.current_user.orders))
    return render_template('details.html',
                           logform=Login(),
                           categories=Property.get_categories(),
                           order=orders[0])


@app.route('/orders/make')
def makeorderview():
    return render_template('address.html',
                           logform=Login())


@app.route('/panel/orders/')
@login_required
def panel_ordersview():
    # TODO: zmienić na @login_required i inny sposób na pozwalanie tylko pracownikom
    if not g.current_user.is_authenticated() or not g.current_user.__tablename__ == "Employees":
        flash('Musisz się zalogować, żeby zobaczyć zamówienia')
        return redirect(url_for('index'))

    orders = g.current_user.orders
    return render_template('panel/orders.html',
                           logform=Login(),
                           orders=orders)


@app.route('/panel/orders/show/<int:oid>/', methods=['GET', 'POST'])
@login_required
def panel_detailsview(oid):
    # TODO: zmienić na @login_required i inny sposób na pozwalanie tylko pracownikom
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
                           logform=Login(),
                           order=orders[0])


@app.route('/panel/orders/unassigned/')
@login_required
def panel_unassigned_orders_view():
    # TODO: zmienić na @login_required i inny sposób na pozwalanie tylko pracownikom
    if not g.current_user.is_authenticated() or not g.current_user.__tablename__ == "Employees":
        flash('Musisz się zalogować, żeby zobaczyć zamówienia')
        return redirect(url_for('index'))

    orders = list(filter(lambda o: o.employee_id == None, Order.query.all()))

    return render_template('panel/unassigned.html',
                           logform=Login(),
                           orders=orders)


@app.route('/panel/orders/unassigned/show/<int:oid>/')
@login_required
def panel_unassigned_details_view(oid):
    # TODO: zmienić na @login_required i inny sposób na pozwalanie tylko pracownikom
    if not g.current_user.is_authenticated() or not g.current_user.__tablename__ == "Employees":
        flash('Musisz się zalogować, żeby zobaczyć zamówienia')
        return redirect(url_for('index'))

    orders = list(filter(lambda o: o.id == oid and o.employee_id is None, Order.query.all()))
    if orders == []:
        flash('Zamówienie o podanym id nie istnieje')
        return redirect(url_for('panel_unassigned_sview'))

    return render_template('panel/unassigned_details.html',
                           logform=Login(),
                           order=orders[0])


@app.route('/panel/orders/unassigned/show/<int:oid>/assign', methods=['POST'])
@login_required
def assign(oid):
    # TODO: zmienić na @login_required i inny sposób na pozwalanie tylko pracownikom
    if not g.current_user.is_authenticated() or not g.current_user.__tablename__ == "Employees":
        flash('Musisz się zalogować')
        return redirect(url_for('index'))

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
