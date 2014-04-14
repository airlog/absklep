
def read_form(name, allow_none=False, cast=None):
    '''
    Odczytuje dane o zadanym kluczu 'name' z otrzymanego formularza. Jesli 'allow_none' jest równe False i wartosc
    odczytana z formularza bedzie None to wyrzuci wyjatek ValueError. Argument 'cast' powinien byc funkcja przyjmujaca
    jeden argument i zwracajaca wynik. Zostanie jej podana odczytana wartość.
    '''

    from flask import request

    tmp = request.form[name]

    if tmp is None and not allow_none:
        raise ValueError('None not allowed')

    if cast is None:
        return tmp
    else:
        return cast(tmp)


def is_customer(user):
    from .models import Customer
    return user.__tablename__ == Customer.__tablename__


def is_employee(user):
    from .models import Employee
    return user.__tablename__ == Employee.__tablename__


def only_employee(login_callback=None, message=None):
    def only_employee_helper(func):
        from functools import wraps

        @wraps(func)
        def only_employee_decorated_view(*args, **kwargs):
            from flask import abort, flash, g, redirect

            # niezalogowanego trzeba przekierować do logowania
            if not g.current_user.is_authenticated() and login_callback is not None:
                if message:
                    flash(message)
                return redirect(str(login_callback))

            # zalogowany klient nie ma dostępu
            if is_customer(g.current_user):
                abort(403)

            # zalogowany pracownik ma dostęp
            if is_employee(g.current_user):
                return func(*args, **kwargs)

            # w innych wypadkach
            abort(403)
        return only_employee_decorated_view
    return only_employee_helper
