from flask import session, url_for, redirect

def loggedIn():
    return session.get("loggedIn", False)

def notLoggedInRedir():
    if not loggedIn():
        print("notLoggedIn")
        return redirect(url_for("site_login"))
    else:
        print("loggedIn")
        return True


def login(userId):
    session["loggedIn"] = True
    session["userId"] = userId