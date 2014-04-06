
from flask.ext.wtf import Form, RecaptchaField
from wtforms import TextField, PasswordField, BooleanField
from wtforms import validators


class Register(Form):
    email = TextField('Email ', [validators.Required(), validators.Email()])
    pas = PasswordField('Haslo ', [validators.Required(),
                                   validators.Length(min=6, max=20, message='hasło musi mieć od 8 do 20 znaków')])
    accept = BooleanField('Zgadzam się na regulamin', [validators.Required(message='musisz zaakceptować regulamin')])


class Login(Form):
    email = TextField('Email ', [validators.Required(), validators.Email()])
    pas = PasswordField('Haslo ', [validators.Required(),
                                   validators.Length(min=6, max=20, message='hasło musi mieć od 8 do 20 znaków')])
    remember = BooleanField('Zapamietaj mnie', [])
