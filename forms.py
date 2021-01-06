from wtforms import Form,  validators, TextField, PasswordField, SelectField, SelectMultipleField, RadioField
from wtforms.fields.html5 import DateTimeLocalField, IntegerField, EmailField
from functions import listToLoT

class RegistrationForm(Form):
    name = TextField("Jméno", [validators.Length(max=255)])
    userId = IntegerField('Číslo', [validators.NumberRange(min=1000,max=9999)])
    email = EmailField('Email', [validators.Email()])

class LoginForm(Form):
    userId = IntegerField('Číslo', [validators.NumberRange(min=1000,max=9999)])
    password = PasswordField("Heslo")

class AddCustomEventForm(Form):
    time_signup = DateTimeLocalField("Čas uzávěrky",format='%Y-%m-%dT%H:%M')#, format="%d.%m.%Y %H:%M")
    time_presentation = DateTimeLocalField("Čas prezentace",format='%Y-%m-%dT%H:%M')#, format="%d.%m.%Y %H:%M")
    time_start = DateTimeLocalField("Čas startu",format='%Y-%m-%dT%H:%M')#), format="%d.%m.%Y %H:%M")
    place = TextField("GPS Souřadnice")

    costAdult = IntegerField("Startovné pro dospělé")
    costChild = IntegerField("Startovné pro děti")

    name = TextField("Název závodu")
    org = TextField("Organizátor")
    sport = SelectField("Sport", choices=["OB","LOB","MTBO","A"])
    typ = SelectMultipleField("Typ", choices=listToLoT(["OŽ","A","B","T"]))
    discipline = SelectField(label="Disciplína",choices=["KT","KL","SP"])
    kat = TextField("Kategorie (oddělit čárkou)")
    
class EventSignupForm(Form):
    chip = IntegerField("Chip")
    kat = SelectField("Kategorie", choices=[], validate_choice=False)
    transport = RadioField("Doprava", choices=["Samostatně","Spolujízda","Nabízím"])
    book = TextField("Poznámka do knihy")
    to_organisator = TextField("Zpráva organizátorovi")
