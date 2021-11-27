import datetime
import requests
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

def fetch_triggers_for_processing():
    con = create_con()
    cur = con.cursor()
    cur.execute("""
        SELECT id FROM triggers
        WHERE inserted_at > NOW() - INTERVAL 4 HOUR
        AND processed IS False
        GROUP BY id
    """)
    output = cur.fetchall()
    logging.info(f"Fetched {len(output)} triggers to process")
    con.close()
    return output

def process_current_availability(id):
    logging.info(f"Processing {id=}")
    url = f'https://clever-app-prod.firebaseio.com/chargers/v2/availability/{id}.json'
    output = requests.get(url)
    if output.status_code == 200:
        available = 0
        if output.json() == None:
            print(f'cant find {id=}')
            available = 0
        else:
            print(output.json()['available'])
            for type in output.json()['available'].keys():
                for speed in ['regular','fast','ultra']:
                    if output.json()['available'].get(type).get(speed):
                        available += output.json()['available'].get(type).get(speed)
            logging.info(f"Inserting {available=} for {id=}")
            insert_availability(id = id, availability = available)

def insert_availability(id, availability):
    con = create_con()
    cur = con.cursor()
    logging.info(f"Inserting {availability=} for {id=}")
    cur.execute("""
            INSERT INTO availability (id, availability) VALUES (%s,%s)
            ON DUPLICATE KEY UPDATE availability = %s
        """, (id, availability, availability, ))
    con.commit()
    con.close()

def update_users():
    con = create_con()
    cur = con.cursor()
    cur.execute("""
        SELECT id, availability_old, availability_new FROM availabilitychange WHERE processed IS False;
    """)
    output = cur.fetchall()
    logging.info(f"Found {len(output)} changes to notify people on")
    emails_list = []
    for entry in output:
        cur.execute("""
            SELECT t.email, a.address, t.id FROM triggers t
            LEFT JOIN addresses a ON t.id = a.id
            WHERE t.processed IS False 
            AND t.inserted_at > NOW() - INTERVAL 4 HOUR
            AND t.id = %s;
        """, (entry[0],))
        emails = cur.fetchall()
        logging.info(f"Reaching out to {len(emails)} people")
        for email in emails:
            logging.info(f'Sending email to {email[0]} about address {email[1]} (id={email[2]})')
            logging.info("Updated triggers and availabilityChange")
            cur.execute("UPDATE triggers set processed = True WHERE id = %s", (email[2],))
            cur.execute("UPDATE availabilitychange set processed = True WHERE id = %s", (email[2],))
            con.commit()
            emails_list.append(email)
    con.close()
    return emails_list

def main(request):
    start = datetime.datetime.now()
    logging.info(f"Getting started at {start}")
    logging.info("Getting all triggers...")
    triggers = fetch_triggers_for_processing()
    ids = []
    for trigger in triggers:
        logging.info(f"Process availability for trigger {trigger[0]}")
        process_current_availability(trigger[0])
        ids.append(trigger[0])
    logging.info("Updating users...")
    emails = update_users()
    end = datetime.datetime.now()
    logging.info(f"Finished at {end}")
    logging.info(f"Execution took {(end-start).total_seconds()}")
    logging.info("---Done Processing!---")
    return {"Status":"completed","updated:":[ids],"notified:":len([emails])}

if __name__ == "__main__":
    main(request=False)