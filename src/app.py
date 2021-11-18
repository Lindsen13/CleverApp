from flask import Flask, render_template, request, flash
from db import fetch_addresses, \
    insert_triggers, \
    fetch_triggers, \
    fetch_triggers_for_processing, \
    fetch_became_available
    
from functions import process_triggers

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
        process_triggers(trigger[0])
    triggers = fetch_triggers_for_processing()
    became_available = fetch_became_available()
    return render_template('test_triggers.html', triggers = triggers, became_available = became_available)