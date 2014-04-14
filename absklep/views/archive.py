
from flask import flash, g, redirect, render_template, request, url_for
from flask.ext.login import login_required

from .. import app
from ..forms import Login
from ..models import Archival, ProductArchivalAmount


@app.route('/panel/archivals/')
@login_required
def panel_archivalsview():
    # TODO: zmienić na @login_required i inny sposób na pozwalanie tylko pracownikom
    if not g.current_user.is_authenticated() or not g.current_user.__tablename__ == "Employees":
        flash('Musisz się zalogować, żeby zobaczyć zamówienia')
        return redirect(url_for('index'))

    archivals = g.current_user.archivals
    return render_template('panel/archivals.html',
                           logform=Login(),
                           archivals=archivals)


@app.route('/panel/archivals/show/<int:aid>/')
@login_required
def panel_archival_detailsview(aid):
    # TODO: zmienić na @login_required i inny sposób na pozwalanie tylko pracownikom
    if not g.current_user.is_authenticated() or not g.current_user.__tablename__ == "Employees":
        flash('Musisz się zalogować, żeby zobaczyć zamówienia')
        return redirect(url_for('index'))

    archivals = list(filter(lambda o: o.id == aid, g.current_user.archivals))
    if archivals == []:
        flash('Zamówienie o podanym id nie istnieje')
        return redirect(url_for('panel_archivalsview'))

    return render_template('panel/archival_details.html',
                           logform=Login(),
                           order=archivals[0])


@app.route('/panel/orders/show/<int:oid>/move_to_archivals', methods=['POST'])
@login_required
def move_to_archivals(oid):
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


__all__ = ['panel_archivalsview', 'panel_archival_detailsview', 'move_to_archivals', ]
