import enum
from flask import session, url_for, redirect
import re
import datetime

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

def logout():
    session["loggedIn"] = False
    session.pop("userId")

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

regex = r'^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$'
match_iso8601 = re.compile(regex).match
def validate_iso8601(str_val):
    try:            
        if match_iso8601( str_val ) is not None:
            return True
    except:
        pass
    return False

def datetime_val(string):
    try:
        datetime.datetime.fromisoformat(string)
        return True
    except:
        return False

def removeAtIndexes(l, index):
    out = []
    for i2, l2 in enumerate(l):
        out.append([])
        for i, item in enumerate(l2):
            if i != index:
                out[i2].append(item)

    return out