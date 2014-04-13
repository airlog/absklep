
from flask.ext.wtf import Form, RecaptchaField
from wtforms import TextField, PasswordField, BooleanField
from wtforms import validators


class Register(Form):
    email = TextField('Email ', [])
    pas = PasswordField('Haslo ', [])
    rep = PasswordField('Potwierdz haslo ', [])
    accept = BooleanField('Zgadzam się na regulamin', [])


class Login(Form):
    email = TextField('Email ', [])
    pas = PasswordField('Haslo ', [])
    remember = BooleanField('Zapamietaj mnie', [])

class Emplogin(Form):
	password = PasswordField('Hasło', [])
	fname = TextField('imie', [])
	lname = TextField('nazw', [])
