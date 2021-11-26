import sqlite3

def initiate():
    con = sqlite3.connect('database.db')
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
    cur.execute("""
        CREATE TRIGGER IF NOT EXISTS changeInAvailability 
            AFTER UPDATE 
            ON availability
            WHEN NEW.availablity <> OLD.availablity
        BEGIN
            INSERT INTO availabilitychange (id, availability_old, availability_new) VALUES (NEW.id, OLD.availablity, NEW.availablity);
            UPDATE triggers SET processed = True WHERE id = NEW.id;
        END;
    """)
    cur.execute("""
        CREATE TRIGGER IF NOT EXISTS updateProcessed 
            AFTER INSERT 
            ON availabilitychange
            WHEN NEW.processed = True
        BEGIN
            UPDATE triggers SET processed = True WHERE id = NEW.id;
        END;
    """)
    print('trigger(s) made')
    con.commit()
    con.close()

def insert_addresses(id, address):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute("INSERT OR REPLACE INTO addresses VALUES (?,?)", (id, address, ))
    con.commit()
    con.close()

def insert_triggers(id, email):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute("INSERT OR REPLACE INTO triggers (id, email) VALUES (?,?)", (id, email,))
    con.commit()
    con.close()

def fetch_addresses(id=None):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    if id:
        output = cur.execute('SELECT * FROM addresses WHERE id = ?', (id,)).fetchall()
    else:
        output = cur.execute('SELECT * FROM addresses').fetchall()
    con.close()
    return output

def insert_availability(id, availability):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute("""
            INSERT INTO availability (id, availablity) VALUES (?,?)
            ON CONFLICT (id) DO UPDATE SET availablity = ?
        """, (id, availability, availability))
    con.commit()
    con.close()

def fetch_triggers(id=None,):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    if id:
        output = cur.execute("""
            SELECT id, email, inserted_at, processed FROM triggers 
            WHERE id = ? 
            AND inserted_at > datetime('now', '-4 hours')
            ORDER BY inserted_at 
            DESC LIMIT 100
        """, (id,)).fetchall()
    else:
        output = cur.execute("""
            SELECT id, email, inserted_at, processed FROM triggers 
            WHERE inserted_at > datetime('now', '-4 hours')
            ORDER BY inserted_at DESC 
            LIMIT 100
        """).fetchall()
    con.close()
    return output

def fetch_processed_triggers():
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    output = cur.execute("""
        SELECT id, email, inserted_at, processed FROM triggers 
        WHERE inserted_at > datetime('now', '-4 hours')
        AND processed = True
        ORDER BY inserted_at DESC 
        LIMIT 100
    """).fetchall()
    con.close()
    return output

def fetch_triggers_for_processing():
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    output = cur.execute("""
        SELECT t.id, a.availablity FROM triggers t
        LEFT JOIN availability a ON t.id = a.id
        WHERE t.inserted_at > datetime('now', '-4 hours')
        GROUP BY t.id, a.availablity
        ORDER BY t.inserted_at DESC 
    """).fetchall()
    con.close()
    return output

def fetch_became_available(processed=None):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    if processed == None:
        output = cur.execute("SELECT * FROM availabilitychange WHERE inserted_at > datetime('now', '-4 hours')").fetchall()
    if processed == False:
        output = cur.execute("SELECT * FROM availabilitychange WHERE inserted_at > datetime('now', '-4 hours') AND processed = False").fetchall()
    else:
        output = cur.execute("SELECT * FROM availabilitychange WHERE inserted_at > datetime('now', '-4 hours') AND processed = True").fetchall()
    con.close()
    return output

def update_availabilitychange(id):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute("UPDATE availabilitychange SET processed = True WHERE id = ?",(id,))
    con.close()

if __name__ == '__main__':
    initiate()
    