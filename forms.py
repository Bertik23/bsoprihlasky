from wtforms import Form, validators, TextField, PasswordField, SelectField, SelectMultipleField, RadioField
from wtforms.fields.core import BooleanField, FieldList
from wtforms.fields.html5 import DateTimeLocalField, IntegerField, EmailField
from wtforms.widgets import CheckboxInput, ListWidget, TableWidget, html_params
from functions import listToLoT
import datetime

def select_multi_checkbox(field, ul_class='', **kwargs):
    kwargs.setdefault('type', 'checkbox')
    field_id = kwargs.pop('id', field.id)
    html = [u'<ul %s>' % html_params(id=field_id, class_=ul_class)]
    for value, label, checked in field.iter_choices():
        choice_id = u'%s-%s' % (field_id, value)
        options = dict(kwargs, name=field.name, value=value, id=choice_id)
        if checked:
            options['checked'] = 'checked'
        html.append(u'<li><input %s /> ' % html_params(**options))
        html.append(u'<label for="%s">%s</label></li>' % (field_id, label))
    html.append(u'</ul>')
    return u''.join(html)

def table(field, class_='', **kwargs):
    kwargs.setdefault('type', 'checkbox')
    field_id = kwargs.pop("id", field.id)
    html = []
    for value, label, checked in field.iter_choices():
        choice_id = u'%s-%s' % (field_id, value)
        options = dict(kwargs, name=field.name, value=value, id=choice_id)
        if checked:
            options['checked'] = 'checked'
        html.append(u'<tr><td><input %s /></td>' % html_params(**options))
        html.append(u"<td>%s</td></tr>" % label)
    return u''.join(html)

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

class AddOrisEventForm(Form):
    events = SelectMultipleField(label="Strany:", validators=[validators.Optional()], choices = [], option_widget=CheckboxInput(), widget=table)#prefix_label=False))
    
class EventSignupForm(Form):
    chip = IntegerField("Chip")
    kat = SelectField("Kategorie", choices=[], validate_choice=False)
    transport = SelectField("Doprava", choices=["Samostatně","Spolujízda","Nabízím"], render_kw={'onchange': "myFunction()"})
    transport_with = SelectField("Spolujízda s", choices=[], validators=[validators.Optional()])
    transport_offer = IntegerField("Nabízím", validators=[validators.Optional()])
    book = TextField("Poznámka do knihy")
    to_organisator = TextField("Zpráva organizátorovi")
