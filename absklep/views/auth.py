
from flask import flash, redirect, render_template, request, url_for
from flask.ext.login import login_required, login_user, logout_user

from .. import app
from ..forms import Login, Register
from ..models import Customer


@app.route("/auth/signup", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        form = Register(request.form)
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

    return render_template('auth/signup.html',
                           form=Register(),
                           logform=Login())


@app.route("/auth/signin", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        form = Login(request.form)
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
                           logform=Login())


@app.route("/auth/signout/")
@login_required
def logout():
    logout_user()
    flash('Wylogowano z systemu!')
    return redirect(url_for('index'))


__all__ = ['register', 'login', 'logout', ]
