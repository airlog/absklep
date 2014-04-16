
from flask import flash, g, redirect, render_template, request, url_for
from flask.ext.login import login_required

from .. import app
from ..forms import Login
from ..models import Archival, ProductArchivalAmount
from ..util import only_employee

MAX_ON_PAGE = 20

@app.route('/panel/archivals/')
@app.route('/panel/archivals/page/<int:page>/')
@app.route('/panel/archivals/sort/<sort>/')
@app.route('/panel/archivals/page/<int:page>/sort/<sort>/')
@only_employee('/panel/', message='Musisz sie zalogować żeby zobaczyć zamówienia!')
def panel_archivalsview(page=1, sort='date_ordered'):
    if page <= 0:
        page = 1
    
    archivals = g.current_user.archivals
    
    if sort == 'date_up':
        archivals.sort(key=lambda a: a.date_ordered)
    elif sort == 'number_up':
        archivals.sort(key=lambda a: a.order_id)
    elif sort == 'number_down':
        archivals.sort(key=lambda a: a.order_id, reverse=True)
    else:
        archivals.sort(key=lambda a: a.date_ordered, reverse=True)

    return render_template('panel/archivals.html',
                           logform=Login(),
                           archivals=archivals[(page-1)*MAX_ON_PAGE:page*MAX_ON_PAGE],
                           page=page,
                           max=len(archivals)/MAX_ON_PAGE,
                           sort=sort
                           )


@app.route('/panel/archivals/show/<int:aid>/')
@only_employee('/panel/', message='Musisz sie zalogować żeby zobaczyć zamówienia!')
def panel_archival_detailsview(aid):
    archivals = list(filter(lambda o: o.id == aid, g.current_user.archivals))
    if archivals == []:
        flash('Zamówienie o podanym id nie istnieje')
        return redirect(url_for('panel_archivalsview'))

    return render_template('panel/archival_details.html',
                           logform=Login(),
                           order=archivals[0])


@app.route('/panel/orders/show/<int:oid>/move_to_archivals', methods=['POST'])
@only_employee('/panel/', message='Musisz sie zalogować!')
def move_to_archivals(oid):
    orders = list(filter(lambda o: o.id == oid, g.current_user.orders))
    if orders == []:
        flash('Zamówienie o podanym id nie istnieje')
        return redirect(url_for('panel_ordersview'))
    if (orders[0].status != orders[0].ENUM_STATUS_VALUES[2] and orders[0].status != orders[0].ENUM_STATUS_VALUES[3]):
        flash('Zamówienia z obecnym statusem nie można zarchiwizować.')
        return redirect(url_for('panel_detailsview', **{'oid': oid}))
    
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
