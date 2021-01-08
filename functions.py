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

def listToLoT(l):
    out = [(i,i) for i in l]
    return out

def addZerosTo(n, num):
    return "0"*(n-len(str(num)))+str(num)

def oneLineTable(*args):
    out = "<table><tr>"
    for i in args:
        out += f"<td>{i}</td>"
    out += "</tr></table>"
    return out