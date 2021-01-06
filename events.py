import requests
from dbconnect import connection, get, checkForTable
import gc
from MySQLdb import escape_string as thwart
from classes import Dummy

def getEventList(**kwargs):
    params = dict(format="json", method="getEventList", **kwargs)
    return requests.get("https://oris.orientacnisporty.cz/API/", params=params).json()

def makeEventTable(event):
    if not checkForTable(event):
        c, conn = connection()
        c.execute(f"CREATE TABLE {event} (id int(4) PRIMARY KEY, kat varchar(6), places int(4), goes_with int(4), book text(65535), to_org_msg mediumtext, admin_msg mediumtext, time int(32))")

        c.close()
        conn.close()
        gc.collect()
        return True
    else:
        return False

def addEvent(event):
    c, conn = connection()

    x = c.execute("SELECT * FROM events WHERE id = %s", [thwart(str(event))])

    if int(x) > 0:
        pass
    else:
        c.execute("INSERT INTO events (id, time_signup, time_presentation, time_start, costAdult, costChild, name, org, place, type, discipline, kat, sport) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                            (thwart(event.id), thwart(str(event.time_signup)), thwart(str(event.time_presentation)), thwart(str(event.time_start)), thwart(str(event.costAdult)), event.costChild, thwart(str(event.name)), thwart(str(event.org)), thwart(str(event.place)), thwart(str(event.typ)), thwart(str(event.discipline)), thwart(str(event.kat)), thwart(event.sport)))

        conn.commit()

        c.close()
        conn.close()
        gc.collect()
        
        makeEventTable(event.id)

def getEventsFromDb(time=0):
    c, conn = connection()

    c.execute("SELECT * FROM events WHERE time_signup > %s", [time])

    out = c.fetchall()

    c.execute("SHOW COLUMNS FROM events")
    labels = [i[0] for i in c.fetchall()]
    out = [dict(zip(labels, i)) for i in out]

    c.close()
    conn.close()
    gc.collect()
    return out

def getEvent(id):
    c, conn = connection()

    x = c.execute("SELECT * FROM events WHERE id = %s", [id])
    if x == 1:
        out = c.fetchall()

        c.execute("SHOW COLUMNS FROM events")
        labels = [i[0] for i in c.fetchall()]
        out = [dict(zip(labels, i)) for i in out]

        c.close()
        conn.close()
        gc.collect()
        return out[0]
    else:
        return None