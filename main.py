import datetime
import gc
import pprint
import traceback
import random
import json

from flask import (Flask, flash, redirect, render_template, request, session,
                   url_for, abort, current_app)
from MySQLdb import escape_string as thwart
from passlib.hash import sha256_crypt
import requests_cache
from werkzeug.datastructures import MultiDict

from classes import Dummy
from dbconnect import connection, get
from events import *
from forms import *
from functions import *
from users import getUser

# from configparser import ConfigParser
# config = ConfigParser()
# config.read("config.ini")

requests_cache.install_cache(cache_name='requests_cache', backend='sqlite', expire_after=300)


app = Flask("Přihlášky")
app.secret_key = b"_randomThingo"


@app.before_request
def before():
    if not loggedIn() and request.endpoint != 'site_login':
        return redirect(url_for("site_login"))
    if request.endpoint in ["site_addOrisEvent","site_addCustomEvent"] and getUser(session.get("userId",-1)).auth > 0:
        abort(403)

@app.errorhandler(403)
def forbidden(e):
    print(e)
    return render_template("errors/403.html"), 403


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
    return render_template("index.html", user=getUser(session.get("userId",-1)), events=[Dummy(**event) for event in events])

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

            return render_template("register.jinja", form=form, user=getUser(session.get("userId",-1)))

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

            return render_template("login.jinja", form=form, user=getUser(session.get("userId",-1)))

        except Exception as e:
            return(traceback.format_exc().replace("\n","<br>"))
    else:
        return redirect(url_for("site_index"))

@app.route("/logout/")
def site_logout():
    logout()
    return redirect(url_for("site_login"))

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
    return render_template("addCustomEvent.jinja",form=form, user=getUser(session.get("userId",-1)))

@app.route("/addOrisEvent/", methods=["GET","POST"])
def site_addOrisEvent():
    form = AddOrisEventForm(request.form)
    if request.method == "POST":
        for id in form.events.data:
            print(request.form.to_dict()[f"time_{id}"])
            if datetime_val(request.form.to_dict()[f"time_{id}"]):
                kwargs = {}
                event = getOrisEvent(id)["Data"]
                if int(event["Stages"]) > 0:
                    kwargs["stages"] = {"n": event["Stages"], "ids": [event[f"Stage{i}"] for i in range(1,8) if event[f"Stage{i}"] != '0']}
                addEvent(dict(id=f"ORIS{id}", time_signup=datetime.datetime.fromisoformat(request.form.to_dict()[f"time_{id}"]).timestamp(), **kwargs))
                flash(f"Event {id} addded.","success")
    c, conn = connection()
    c.execute("SELECT id FROM events")
    alreadyAdded = [i[0] for i in c.fetchall()]
    c.close()
    conn.close()
    gc.collect()
    events = getEventList(datefrom=datetime.datetime.now().date())
    events = [events[i] for i in sorted(events, key=lambda x: datetime.date.fromisoformat(events[x]['Date'])) if f'ORIS{events[i]["ID"]}' not in alreadyAdded]
    
    form.events.choices = [(event["ID"], f'{datetime.date.fromisoformat(event["Date"]).strftime("%d.%m.%Y")}</td><td>{event["Name"]}') for event in events]

    
    return render_template("addOrisEvent.html", form=form, user=getUser(session.get("userId",-1)))


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
                if i in ["stages"]:
                    try:
                        print(event[i])
                        event[i] = json.loads(event[i].replace("\'","\""))
                    except Exception as e:
                        print(e)
                        event[i] = {"n": 0}

            c, conn = connection()

            c.execute("SELECT id FROM signups WHERE id = %s AND event_id = %s", [session.get("userId",-1), event["id"]])
            if c.fetchall() == ():
                user_signedup = False
            else:
                user_signedup = True

            if request.method == "POST":
                form = EventSignupForm(request.form)
                if form.validate():
                    if not user_signedup:
                        c.execute("INSERT INTO signups (id, chip, kat, places, goes_with, book, to_org_msg, time, event_id, stages) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                                    [session["userId"], form.chip.data, thwart(form.kat.data), form.transport_offer.data if form.transport.data == "Nabízím" else -1 if form.transport.data == "Spolujízda" else 0, None, thwart(form.book.data), thwart(form.to_organisator.data), datetime.datetime.now().timestamp(), event["id"], form.stages.data])
                        conn.commit()
                    else:
                        c.execute("UPDATE signups SET chip = %s, kat = %s, places = %s, goes_with = %s, book = %s, to_org_msg = %s, time = %s, stages = %s WHERE id = %s AND event_id = %s",
                                [form.chip.data, thwart(form.kat.data), form.transport_offer.data if form.transport.data == "Nabízím" else -1 if form.transport.data == "Spolujízda" else 0, None, thwart(form.book.data), thwart(form.to_organisator.data), datetime.datetime.now().timestamp(), thwart(",".join(form.stages.data)), session["userId"], event["id"]])
                        conn.commit()
            else:
                c.execute("SELECT chip, kat, book, to_org_msg, goes_with, places FROM signups WHERE event_id = %s and id = %s", [event["id"], session["userId"]])
                f = c.fetchone()
                if f != None:
                    l = ["chip","kat","book","to_organisator","transport_with","transport_offer"]
                    f = dict(zip(l, f))
                    if f["transport_with"] == None:
                        if f["transport_offer"] == 0:
                            f["transport"] = "Samostatně"
                        else:
                            f["transport"] = "Nabízím"
                    else:
                        f["transport"] = "Spolujízda"
                    print(f)
                    f = MultiDict([(key, f[key]) for key in f])
                    form = EventSignupForm(f)
                else:
                    form = EventSignupForm()

            c.execute("SELECT signups.id, signups.chip, signups.kat, signups.stages, signups.goes_with, signups.places, signups.book, signups.to_org_msg, signups.admin_msg, signups.time, users.name FROM signups INNER JOIN users ON signups.id = users.uid AND signups.event_id = %s", [event["id"]])
            signedup = c.fetchall()

            labels = ["Id", "Chip", "Kat", "S", "Místa", "Kniha", "Organizátorovi", "Od správce", "Čas", "Jméno"]
            if int(event["stages"]["n"]) > 0:
                labels.insert(3, "Etapy")
            else:
                signedup = removeAtIndexes(signedup, 3)
            signedup = [dict(zip(labels, i)) for i in signedup]

            for i in signedup:
                i["Čas"] = datetime.datetime.fromtimestamp(i["Čas"]).strftime("%H:%M %d.%m.%Y")


            c.execute("SELECT signups.id, users.name, signups.places FROM signups INNER JOIN users ON signups.id = users.uid AND signups.places > 0 AND signups.event_id = %s", [event["id"]])

            places = c.fetchall()
            
            c.close()
            conn.close()
            gc.collect()
            form.kat.choices = event["kat"].split(",")
            form.transport_with.choices = [("","")]+[(p[0], f"{p[1]} ({p[2]})") for p in places]
            if int(event["stages"]["n"]) > 0:
                form.stages.choices = [(str(i),f"E{i}") for i in range(1, int(event["stages"]["n"])+1)]
            return render_template("event.html", event=Dummy(**event), form=form, signedup=signedup, user=getUser(session.get("userId",-1)), user_signedup = user_signedup)
    return redirect(url_for("site_index"))

@app.route("/user-settings/", methods=["GET","POST"])
def site_settings():
    if request.method == "POST":
        form = UserSettingsForm(request.form)
        if form.validate():
            c, conn = connection()
            
            f = request.form.to_dict()
            email = f.pop("email")
            c.execute("UPDATE users SET settings = %s WHERE uid = %s", [json.dumps(f), session.get("userId",-1)])
            c.execute("UPDATE users SET email = %s WHERE uid = %s", [email, session["userId"]])
            conn.commit()

            c.close()
            conn.close()
            gc.collect()
            flash("Změny uloženy", "success")
    else:
        userSettings = getUser(session.get("userId",-1)).settings
        if userSettings != None:
            userSettings = json.loads(userSettings)
            userSettings["email"] = getUser(session.get("userId",-1)).email
            userSettings = MultiDict([(key, userSettings[key]) for key in userSettings])
            form = UserSettingsForm(userSettings)
        else:
            userSettings = {}
            userSettings["email"] = getUser(session.get("userId",-1)).email
            userSettings = MultiDict([(key, userSettings[key]) for key in userSettings])
            form = UserSettingsForm(userSettings)
    #form = UserSettingsForm(request.form)
    return render_template("user_settings.html", form = form, user = getUser(session.get("userId",-1)))

@app.route("/test/")
def site_test():
    flash("Test", random.choice(["success","error",""]))
    return render_template("header.html", user=getUser(session.get("userId",-1)))

app.run()
