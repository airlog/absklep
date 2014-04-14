
from flask import g
from flask.ext.login import current_user

from . import app, login_manager


@app.before_request
def inject_user():
    from flask import g

    g.current_user = current_user

@login_manager.user_loader
def load_user(uid):
    from absklep.models import Customer, Employee

    if uid[0]=='u': return Customer.query.get(int(uid[1:]))
    if uid[0]=='e': return Employee.query.get(int(uid[1:]))
    return None


def delete_cart_cookie(response, cookie_name='cart'):
    response.set_cookie(cookie_name, expires=0)
    return response
