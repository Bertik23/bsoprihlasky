from flask import Flask, render_template, flash, request, url_for, redirect, session
from passlib.hash import sha256_crypt
from MySQLdb import escape_string as thwart
import gc
import traceback
from forms import *
from functions import *

# from configparser import ConfigParser
# config = ConfigParser()
# config.read("config.ini")

from dbconnect import connection, get

class Dummy:
    def __init__(self, **kwargs):
        for i in kwargs:
            setattr(self, i, kwargs[i])

app = Flask("Přihlášky")
app.secret_key = b"_randomThingo"

@app.before_request
def before():
    print(request.endpoint)
    if not loggedIn() and request.endpoint != 'site_login':
        return redirect(url_for("site_login"))

@app.route("/")
def site_index():
    return render_template("index.html", user=Dummy(name=get("users","name","uid",session["userId"])[0][0]))

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
                        return redirect(url_for("site_index"))
                    else:
                        flash("Špatné heslo", "error")

                elif x == 0:
                    flash("Uživatel neexistuje", "error")


            return render_template("login.jinja", form=form)

        except Exception as e:
            return(traceback.format_exc().replace("\n","<br>"))
    else:
        return redirect(url_for("site_index"))


app.run()