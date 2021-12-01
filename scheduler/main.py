import smtplib
import datetime
import requests
import mysql.connector 
import os
import logging
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials

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
            logging.info(f'cant find {id=}')
            available = 0
        else:
            logging.info(output.json()['available'])
            for type in output.json()['available'].keys():
                for speed in ['regular','fast','ultra']:
                    if output.json()['available'].get(type).get(speed):
                        available += output.json()['available'].get(type).get(speed)
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

def send_email(to="ivo.lindsen@hotmail.com",subject="This is a test - subject", body="This is a test - body"):
    user = os.environ['GMAIL_MAIL']
    password = os.environ['GMAIL_PASSWORD']

    chars = [
        {'æ':'ae'},
        {'Æ':'AE'},
        {'å':'a'},
        {'Å':'A'},
        {'œ':'oe'},
        {'Œ':'Oe'},
        {'ø':'o'},
        {'Ø':'O'},
    ]
    for char in chars:
        subject = subject.replace(list(char.keys())[0],list(char.values())[0])
        body = body.replace(list(char.keys())[0],list(char.values())[0])
        
    email_text = f"From: {user}\nTo: {to}\nSubject: {subject}\n\n{body}"
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    server.login(user, password)
    server.sendmail(user, to, email_text)
    server.close()
        
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
            send_email(
                to=email[0],
                subject=f"Clever charging spot {email[1]} came available!",
                body=f"Clever charging spot {email[1]} came available! Thanks for using my tool :-)"
            )
            logging.info("Updated triggers and availabilityChange")
            cur.execute("UPDATE triggers set processed = True WHERE id = %s", (email[2],))
            cur.execute("UPDATE availabilitychange set processed = True WHERE id = %s", (email[2],))
            con.commit()
            emails_list.append(email)
    con.close()
    return emails_list

def scheduler(enable=True):
    credentials = GoogleCredentials.get_application_default()

    service = discovery.build('cloudscheduler', 'v1', credentials=credentials)
    project = os.environ['GCP_PROJECT_ID']
    location = os.environ['GCP_LOCATION']
    scheduler = os.environ['GCP_CLOUD_SCHEDULER']
    name = f"projects/{project}/locations/{location}/jobs/{scheduler}"

    request = service.projects().locations().jobs().get(name=name)
    response = request.execute()
    if enable == True:
        if response['state'] == 'ENABLED':
            logging.info(f"State is {response['state']}. Not doing anything")
        else:
            logging.info("Resuming...")
            request = service.projects().locations().jobs().resume(name=name)
            response = request.execute()
    elif enable == False:
        if response['state'] == 'PAUSED.':
            logging.info(f"State is {response['state']}. Not doing anything")
        else:
            logging.info("Pausing...")
            request = service.projects().locations().jobs().pause(name=name)
            response = request.execute()

def main(request):
    start = datetime.datetime.now()
    logging.info(f"Getting started at {start}")
    logging.info("Getting all triggers...")
    triggers = fetch_triggers_for_processing()
    if len(triggers) == 0:
        scheduler(enable=False)
        return {"Status":"completed","updated:":[],"notified:":0,"enabled":"Changed To Disable"}
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
    return {"Status":"completed","updated:":[ids],"notified:":len([emails]),"enabled":"Still enabled"}


if __name__ == "__main__":
    main(request=False)