import MySQLdb
import gc

def connection():
    conn = MySQLdb.connect(host="localhost",
                           user = "root",
                           passwd = "TUSPoD%123",
                           db = "bsoprihlasky")
    c = conn.cursor()

    return c, conn

def get(table, what, where, value):
    c, conn = connection()
    c.execute(f"SELECT {what} FROM {table} WHERE {where} = %s", [value])
    a = c.fetchall()
    c.close()
    conn.close()
    gc.collect()
    return a

def checkForTable(table):
    c, conn = connection()

    c.execute("SHOW TABLES LIKE %s", [table])

    r = c.fetchone()

    c.close()
    conn.close()
    gc.collect()

    if r:
        return True
    else:
        return False