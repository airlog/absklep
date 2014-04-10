
from flask import g
from flask.ext.login import current_user

from . import app, login_manager


@app.before_request
def inject_user():
    from flask import g

    g.current_user = current_user

@login_manager.user_loader
def load_user(uid):
    from absklep.models import Customer

    return Customer.query.get(uid)

