from dbconnect import connection
from classes import *
import gc

def getUser(id):
    c, conn = connection()

    x = c.execute("SELECT * FROM users WHERE uid = %s", [id])

    if x == 0:
        return None
    else:
        user = c.fetchone()
        c.execute("SHOW COLUMNS FROM users")
        labels = [i[0] for i in c.fetchall()]
        user = dict(zip(labels, user))
        user.pop("password")
        return Dummy(**user)