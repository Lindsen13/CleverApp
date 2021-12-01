import mysql.connector
import os
import logging

logging.basicConfig(level=logging.INFO)

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
            availability INTEGER NOT NULL,
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
    logging.info('table(s) made')
    cur.execute("""delimiter //""")
    cur.execute("""
        CREATE TRIGGER updateAvailability AFTER REPLACE ON availability
        FOR EACH ROW
        BEGIN
            IF NEW.availability > OLD.availability THEN
                INSERT INTO availabilitychange (id, availability_old, availability_new, processed) VALUES (NEW.id, OLD.availability, NEW.availability, FALSE);
            END IF;
        END
    """)
    cur.execute("""delimiter ;""")
    logging.info('trigger(s) made')
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

def fetch_availability(id):
    con = create_con()
    cur = con.cursor()
    cur.execute("""
        SELECT availability FROM availability 
        WHERE id = %s 
        ORDER BY inserted_at  DESC
        LIMIT 1
    """, (id,))
    output = cur.fetchall()
    con.close()
    if len(output) == 0:
        return None
    else:
        return output[0][0]



if __name__ == '__main__':
    initiate()
    