from flask import Flask, render_template, request, flash
from db import fetch_addresses, \
    insert_triggers, \
    fetch_triggers, \
    fetch_triggers_for_processing, \
    insert_availability, \
    fetch_became_available
import requests

app = Flask(__name__)
app.secret_key = b'MyAmazingSecretForCookies'

@app.route('/')
def index():
    addresses = fetch_addresses()
    return render_template('index.html', addresses = addresses)

@app.route('/<int:id>', methods=['GET', 'POST'])
def insights_page(id):
    if request.method == 'POST':
        email = request.form['email']
        insert_triggers(id=id, email=email)
        flash(f'You were successfully subscribed for charger {id}')
    triggers = fetch_triggers(id=id)
    return render_template('triggers.html', id=id, triggers = triggers)

@app.route('/check_triggers')
def test():
    triggers = fetch_triggers_for_processing()
    for trigger in triggers:
        id = trigger[0]
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
                            available = 1
                            insert_availability(id = id, availability = available)
            print(available)
    triggers = fetch_triggers_for_processing()
    became_available = fetch_became_available()
    return render_template('test_triggers.html', triggers = triggers, became_available = became_available)