import mysql.connector
import os

def create_con():
    return mysql.connector.connect(
        user=os.environ['SQL_USER'], 
        password=os.environ['SQL_PASSWORD'], 
        host=os.environ['SQL_HOST'], 
        database=os.environ['SQL_DATABASE'])
    
def initiate():
    con = create_con()
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS addresses (
            id INTEGER PRIMARY KEY, 
            address TEXT NOT NULL)
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS triggers (
            id INTEGER NOT NULL, 
            email TEXT NOT NULL, 
            processed BOOLEAN DEFAULT FALSE,
            inserted_at timestamp DEFAULT CURRENT_TIMESTAMP)
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS availability (
            id INTEGER PRIMARY KEY NOT NULL, 
            availablity INTEGER NOT NULL,
            inserted_at timestamp DEFAULT CURRENT_TIMESTAMP)
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS availabilitychange (
            id INTEGER NOT NULL, 
            availability_old INTEGER NOT NULL,
            availability_new INTEGER NOT NULL,
            processed BOOLEAN DEFAULT FALSE,
            inserted_at timestamp DEFAULT CURRENT_TIMESTAMP)
    """)
    print('table(s) made')
    con.commit()
    con.close()

def insert_addresses(id, address):
    con = create_con()
    cur = con.cursor()
    cur.execute("REPLACE INTO addresses VALUES (%s,%s)", (id, address, ))
    con.commit()
    con.close()

def insert_triggers(id, email):
    con = create_con()
    cur = con.cursor()
    cur.execute("REPLACE INTO triggers (id, email) VALUES (%s,%s)", (id, email,))
    con.commit()
    con.close()

def fetch_addresses(id=None):
    con = create_con()
    cur = con.cursor()
    if id:
        cur.execute('SELECT * FROM addresses WHERE id = %s', (id,))
        output = cur.fetchall()
    else:
        cur.execute('SELECT * FROM addresses;')
        output = cur.fetchall()
    con.close()
    return output

def insert_availability(id, availability):
    con = create_con()
    cur = con.cursor()
    cur.execute("""
            INSERT INTO availability (id, availablity) VALUES (%s,%s)
            ON CONFLICT (id) DO UPDATE SET availablity = %s
        """, (id, availability, availability))
    con.commit()
    con.close()

def fetch_triggers(id=None,):
    con = create_con()
    cur = con.cursor()
    if id:
        cur.execute("""
            SELECT id, email, inserted_at, processed FROM triggers 
            WHERE id = %s 
            AND inserted_at > NOW() - INTERVAL 4 HOUR
            ORDER BY inserted_at 
            DESC LIMIT 100
        """, (id,))
        output = cur.fetchall()
    else:
        cur.execute("""
            SELECT id, email, inserted_at, processed FROM triggers 
            WHERE inserted_at > NOW() - INTERVAL 4 HOUR
            ORDER BY inserted_at DESC 
            LIMIT 100
        """)
        output = cur.fetchall()
    con.close()
    return output

if __name__ == '__main__':
    initiate()
    