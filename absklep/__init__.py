
from flask import Flask, request, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, login_user, current_user


__version__ = "0.1.0"

app = Flask(__name__)
app.db = SQLAlchemy(app)

import absklep.controllers
from absklep.models import *
import absklep.forms

absklep.controllers.load_config(app, package=__name__)
absklep.controllers.load_database(app)


login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)



# dummy function to see if everything set up correctly
@app.route("/")
def hello_world():
	s=''
	if current_user is not None: s=current_user.email
	return ("\n"
            "<div style=\"text-align: center;\">\n"
            "   <h1>Hello, %s</h1>\n"
            "   <span style=\"font-size: 24px;\">get ready for <b>%s</b>!</span>\n"
            " </div>\n" % (str(current_user.email), __name__)
            )



#some communicates for now
success = "Zostałeś zarejestrowany!"
fail = "Podany email już istnieje."

@app.route("/register/", methods=['GET', 'POST'])
def register():
	form = absklep.forms.Register(request.form)
	if form.validate_on_submit():
		
		if app.db.session.query(Customer).filter(Customer.email==form.email.data).scalar() is None:
			customer = Customer(str(form.email.data), str(form.pas.data))
			app.db.session.add(customer)
			app.db.session.commit()
			
			return success
		
		return render_template('register.html', form=form, message=fail)
	return render_template('register.html', form=form, message='')


@app.route("/login/", methods=['GET', 'POST'])
def login():
	form = absklep.forms.Login(request.form)
	if form.validate_on_submit():
		user = app.db.session.query(Customer).filter(Customer.email==form.email.data).first()
		if user is not None:
			#TODO: check if password correct
			if login_user(user, remember=form.remember.data):
				return 'Witaj, '+str(current_user.email)
	return render_template('login.html', form=form, message='')
		


@login_manager.user_loader
def load_user(uid):
	return Customer.query.get(uid)