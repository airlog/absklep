
from flask import render_template, flash

from .. import app
from ..util import only_employee


# TODO: czy ta funkcja jest potrzebna? wydaje mi się, że edycja produktu załatwia sprawę (by Rafal)
@app.route('/panel/addparam/', methods=['GET', 'POST'])
@only_employee('/panel/')
def addparam():
    from flask import g, request
    from ..models import Property
    from ..util import read_form

    if request.method == 'POST':
        app.db.session.add(Property(read_form('key'), read_form('val')))
        app.db.session.commit()
        flash('Dodano')
    
    return render_template('panel/addparam.html')
