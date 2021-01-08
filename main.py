import re
import MySQLdb
from flask import Flask, render_template, flash, request, url_for, redirect, session
from passlib.hash import sha256_crypt
from MySQLdb import escape_string as thwart
import gc
import traceback
from forms import *
from functions import *
from events import *
from classes import Dummy
import datetime
import pprint
from wtforms import BooleanField

# from configparser import ConfigParser
# config = ConfigParser()
# config.read("config.ini")

from dbconnect import connection, get

app = Flask("Přihlášky")
app.secret_key = b"_randomThingo"

@app.before_request
def before():
    if not loggedIn() and request.endpoint != 'site_login':
        return redirect(url_for("site_login"))

@app.route("/")
def site_index():
    events = getEventsFromDb(0)#datetime.datetime.now().timestamp())
    for event in events:
        for i in event:
            if i.startswith("time_"):
                if event[i] == None:
                    event[i] = "TBA"
                else:
                    event[i] = datetime.datetime.fromtimestamp(event[i]).strftime("%H:%M %d.%m.%Y")
    return render_template("index.html", user=Dummy(name=get("users","name","uid",session["userId"])[0][0]), events=[Dummy(**event) for event in events])

@app.route("/register/", methods=["GET","POST"])
def site_register():
    a = notLoggedInRedir()
    if a == True:
        try:
            form = RegistrationForm(request.form)

            if request.method == "POST" and form.validate():
                userId  = form.userId.data
                email = form.email.data
                password = sha256_crypt.hash("1111")
                name = form.name.data
                c, conn = connection()

                x = c.execute("SELECT * FROM users WHERE uid = %s", [thwart(str(userId))])

                if int(x) > 0:
                    flash("Číslo už zabrané, použij jiné", category="error")
                    return render_template('register.jinja', form=form)

                else:
                    c.execute("INSERT INTO users (uid, password, email, name) VALUES (%s, %s, %s, %s)",
                            (thwart(str(userId)), thwart(password), thwart(email), thwart(name)))
                    
                    conn.commit()
                    #flash("Thanks for registering!")
                    c.close()
                    conn.close()
                    gc.collect()

                return redirect(url_for('site_index'))

            return render_template("register.jinja", form=form)

        except Exception as e:
            return(traceback.format_exc().replace("\n","<br>"))
    return a

@app.route("/login/", methods=["GET","POST"])
def site_login():
    if not loggedIn():
        try:
            form = LoginForm(request.form)

            if request.method == "POST" and form.validate():
                userId  = form.userId.data
                c, conn = connection()

                x = c.execute("SELECT * FROM users WHERE uid = %s", [thwart(str(userId))])


                if int(x) == 1:
                    if  sha256_crypt.verify(form.password.data,c.fetchone()[1]):
                        session["loggedIn"] = True
                        session["userId"] = form.userId.data
                        c.close()
                        conn.close()
                        gc.collect()
                        return redirect(url_for("site_index"))
                    else:
                        flash("Špatné heslo", "error")

                elif x == 0:
                    flash("Uživatel neexistuje", "error")

                c.close()
                conn.close()
                gc.collect()

            return render_template("login.jinja", form=form)

        except Exception as e:
            return(traceback.format_exc().replace("\n","<br>"))
    else:
        return redirect(url_for("site_index"))

@app.route("/addCustomEvent/", methods=["GET","POST"])
def site_addCustomEvent():
    form = AddCustomEventForm(request.form)
    if request.method == "POST" and form.validate():
        c, conn = connection()

        x = c.execute("SELECT * FROM events WHERE id LIKE 'CUST%'")

        id = "CUST" + addZerosTo(4, max([int(i[0][4:]) for i in c.fetchall()])+1)

        formData = form.data
        formData["time_signup"] = formData["time_signup"].timestamp()
        formData["time_presentation"] = formData["time_presentation"].timestamp()
        formData["time_start"] = formData["time_start"].timestamp()
        formData["typ"] = ",".join(formData["typ"])

        print(formData)

        addEvent(Dummy(id=id, **formData))
        c.close()
        conn.close()
        gc.collect()
    return render_template("addCustomEvent.jinja",form=form)

@app.route("/addOrisEvent/", methods=["GET","POST"])
def site_addOrisEvent():
    form = AddOrisEventForm(request.form)
    if request.method == "POST":
        for id in form.events.data:
            addEvent(f"ORIS{id}")
    c, conn = connection()
    c.execute("SELECT id FROM events")
    alreadyAdded = [i[0] for i in c.fetchall()]
    c.close()
    conn.close()
    gc.collect()
    events = getEventList(datefrom=datetime.datetime.now().date())['Data']
    events = [events[i] for i in sorted(events, key=lambda x: datetime.date.fromisoformat(events[x]['Date'])) if f'ORIS{events[i]["ID"]}' not in alreadyAdded]
    
    form.events.choices = [(event["ID"], f'{datetime.date.fromisoformat(event["Date"]).strftime("%d.%m.%Y")}</td><td>{event["Name"]}') for event in events]
    
    return render_template("addOrisEvent.html",form=form)


@app.route("/event/", methods=["GET","POST"])
def site_event():
    id = request.args.get('id', None)
    if id != None:
        event = getEvent(id)
        if event != None:
            for i in event:
                if i.startswith("time_"):
                    if event[i] == None:
                        event[i] = "TBA"
                    else:
                        event[i] = datetime.datetime.fromtimestamp(event[i]).strftime("%H:%M %d.%m.%Y")
            try:
                form = EventSignupForm(request.form)
            except:
                form = EventSignupForm()
            c, conn = connection()

            if request.method == "POST" and form.validate():
                x = c.execute("SELECT * FROM signups WHERE id = %s AND event_id = %s", [session["userId"], event["id"]])
                if x == 0:
                    c.execute(f"INSERT INTO signups (id, chip, kat, places, goes_with, book, to_org_msg, time, event_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                                [session["userId"], form.chip.data, thwart(form.kat.data), form.transport_offer.data if form.transport.data == "Nabízím" else -1 if form.transport.data == "Spolujízda" else 0, None, thwart(form.book.data), thwart(form.to_organisator.data), datetime.datetime.now().timestamp(), event["id"]])
                    conn.commit()
                else:
                    flash("Už jsi přihlášen")

            c.execute(f"SELECT signups.id, signups.kat, signups.goes_with, signups.places, signups.book, signups.to_org_msg, signups.admin_msg, signups.time, users.name FROM signups INNER JOIN users ON signups.id = users.uid")
            signedup = c.fetchall()

            labels = ["Id","Kat","S","Místa","Kniha","Organizátorovi","Od správce","Čas","Jméno"]
            signedup = [dict(zip(labels, i)) for i in signedup]
            
            c.close()
            conn.close()
            gc.collect()
            form.kat.choices = event["kat"].split(",")
            return render_template("event.html", event=Dummy(**event), form=form, signedup=signedup)
    return redirect(url_for("site_index"))

app.run()