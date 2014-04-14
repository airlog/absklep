
from flask import flash, g, redirect, render_template, request, url_for
from flask.ext.login import login_required, login_user, logout_user

from .. import app
from ..forms import Login, Register, Emplogin
from ..models import Customer, Employee


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


@app.route('/panel/', methods=['GET', 'POST'])
def emplogin():
    # pracownik jest juz zalogowany
    # TODO: zmienić na @login_required i inny sposób na pozwalanie tylko pracownikom
    if g.current_user.is_authenticated() and g.current_user.__tablename__ == "Employees":
        return render_template('/panel/panel.html', logform=Login())

    if request.method == 'POST':
        emplogin = Emplogin(request.form)
        if emplogin.validate_on_submit():
            emp = app.db.session.query(Employee).filter(Employee.firstname == emplogin.fname.data, Employee.surname == emplogin.lname.data).first()
            if emp is not None:
                if emp.verify_password(emplogin.password.data) and login_user(emp):
                    # zalogowanie udane, powrót
                    flash('Zalogowano do sklepu!')
                    return redirect(url_for('emplogin'))

            # zalogowanie nieudane, powrót
            flash('Niepoprawne dane lub hasło')
            return redirect(url_for('emplogin'))

    # wchodzi niezalogowany pracownik albo użytkownik
    return render_template('panel/login.html',
                            emplogin=Emplogin())


__all__ = ['register', 'login', 'logout', 'emplogin', ]
