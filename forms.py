from wtforms import Form, TextField, PasswordField, validators, IntegerField

class RegistrationForm(Form):
    name = TextField("Jméno", [validators.Length(max=255)])
    userId = IntegerField('Číslo', [validators.NumberRange(min=1000,max=9999)])
    email = TextField('Email', [validators.Email()])

class LoginForm(Form):
    userId = IntegerField('Číslo', [validators.NumberRange(min=1000,max=9999)])
    password = PasswordField("Heslo")