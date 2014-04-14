
from flask import render_template, redirect, url_for, flash

from .. import app


# TODO: czy ta funkcja jest potrzebna? wydaje mi się, że edycja produktu załatwia sprawę (by Rafal)
@app.route('/panel/addparam/', methods=['GET', 'POST'])
def addparam():
    from flask import g, request
    from ..models import Property
    from ..util import read_form
    
    if not g.current_user.is_authenticated() or g.current_user.__tablename__ != "Employees":
        return redirect(url_for('emplogin'))
    
    if request.method == 'POST':
        app.db.session.add(Property(read_form('key'), read_form('val')))
        app.db.session.commit()
        flash('Dodano')
    
    return render_template('panel/addparam.html')
