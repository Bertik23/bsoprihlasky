import requests
from dbconnect import connection, get, checkForTable
import gc
from MySQLdb import escape_string as thwart
from classes import Dummy
import datetime

def getEventList(**kwargs):
    params = dict(format="json", method="getEventList", **kwargs)
    r = requests.get("https://oris.orientacnisporty.cz/API/", params=params)
    #print(r.url)
    return r.json()

def getOrisEvent(id, **kwargs):
    params = dict(format="json", method="getEvent", id=id, **kwargs)
    r = requests.get("https://oris.orientacnisporty.cz/API/", params=params)
    #print(r.url)
    return r.json()

# def makeEventTable(event):
#     if not checkForTable(event):
#         c, conn = connection()
#         c.execute(f"CREATE TABLE {event} (sign_in_id int(10) PRIMARY KEY AUTO INCREMENT, id int(4), chip int(32), kat varchar(6), places int(4), goes_with int(4), book text(65535), to_org_msg mediumtext, admin_msg mediumtext, time int(32))")

#         c.close()
#         conn.close()
#         gc.collect()
#         return True
#     else:
#         return False

def addEvent(event):
    print(event)
    c, conn = connection()

    if type(event) == Dummy:
        x = c.execute("SELECT * FROM events WHERE id = %s", [thwart(str(event.id))])
    else:
        x = c.execute("SELECT * FROM events WHERE id = %s", [thwart(str(event))])

    if int(x) > 0:
        pass
    else:
        if type(event) == Dummy:
            c.execute("INSERT INTO events (id, time_signup, time_presentation, time_start, costAdult, costChild, name, org, place, type, discipline, kat, sport) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                            (thwart(event.id), thwart(str(event.time_signup)), thwart(str(event.time_presentation)), thwart(str(event.time_start)), thwart(str(event.costAdult)), event.costChild, thwart(str(event.name)), thwart(str(event.org)), thwart(str(event.place)), thwart(str(event.typ)), thwart(str(event.discipline)), thwart(str(event.kat)), thwart(event.sport)))
        else:
            c.execute("INSERT INTO events (id) VALUES (%s)", [thwart(event)])

        conn.commit()

        c.close()
        conn.close()
        gc.collect()
        
        #makeEventTable(event.id)

def getEventsFromDb(time=0):
    c, conn = connection()

    c.execute("SELECT * FROM events WHERE time_signup > %s OR time_signup IS NULL", [time])

    out = c.fetchall()

    c.execute("SHOW COLUMNS FROM events")
    labels = [i[0] for i in c.fetchall()]
    out = [dict(zip(labels, i)) for i in out]

    for event in out:
        if event["id"].startswith("ORIS"):
            orisEvent = getOrisEvent(event["id"].lstrip("ORIS"))["Data"]
            event["time_presentation"] = datetime.datetime.combine(datetime.date.fromisoformat(orisEvent["Date"]), datetime.time.fromisoformat("0"*(5-len(orisEvent["EventOfficeCloses"][-5:]))+orisEvent["EventOfficeCloses"][-5:])).timestamp() if orisEvent["Date"] != "" and orisEvent["EventOfficeCloses"] != "" else None
            event["time_start"] = datetime.datetime.combine(datetime.date.fromisoformat(orisEvent["Date"]), datetime.time.fromisoformat(orisEvent["StartTime"])).timestamp() if orisEvent["Date"] != "" and orisEvent["StartTime"] != "" else None

            event["name"] = orisEvent["Name"]
            event["type"] = orisEvent["Level"]["ShortName"]
            event["discipline"] = orisEvent["Discipline"]["ShortName"]
            event["sport"] = orisEvent["Sport"]["NameCZ"]
            #print(event)
            

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
        event = out[0]
        if event["id"].startswith("ORIS"):
            orisEvent = getOrisEvent(event["id"].lstrip("ORIS"))["Data"]
            event["time_presentation"] = datetime.datetime.combine(datetime.date.fromisoformat(orisEvent["Date"]), datetime.time.fromisoformat("0"*(5-len(orisEvent["EventOfficeCloses"][-5:]))+orisEvent["EventOfficeCloses"][-5:])).timestamp() if orisEvent["Date"] != "" and orisEvent["EventOfficeCloses"] != "" else None
            event["time_start"] = datetime.datetime.combine(datetime.date.fromisoformat(orisEvent["Date"]), datetime.time.fromisoformat(orisEvent["StartTime"])).timestamp() if orisEvent["Date"] != "" and orisEvent["StartTime"] != "" else None

            event["name"] = orisEvent["Name"]
            event["type"] = orisEvent["Level"]["ShortName"]
            event["discipline"] = orisEvent["Discipline"]["ShortName"]
            event["sport"] = orisEvent["Sport"]["NameCZ"]

            event["kat"] = ""
            if orisEvent["Classes"] != []:
                event["kat"] = []
                for class_ in orisEvent["Classes"]:
                    event["kat"].append(orisEvent["Classes"][class_]["ClassDefinition"]["Name"])
                event["kat"] = ",".join(event["kat"])

        return event
    else:
        return None