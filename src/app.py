from flask import Flask, render_template, request, flash
from flask_apscheduler import APScheduler

from db import fetch_addresses, \
    insert_triggers, \
    fetch_triggers, \
    fetch_triggers_for_processing, \
    fetch_became_available, \
    update_availabilitychange, \
    fetch_processed_triggers
    
from functions import process_triggers

app = Flask(__name__)
app.secret_key = b'MyAmazingSecretForCookies'

# initialize scheduler
scheduler = APScheduler()
scheduler.api_enabled = True
scheduler.init_app(app)
scheduler.start()

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
    address = fetch_addresses(id=id)
    return render_template('triggers.html', id=id, triggers = triggers, address=address)

@app.route('/check_triggers')
def check_triggers():
    process_all_triggers()
    triggers = fetch_triggers_for_processing()
    became_available = fetch_became_available(processed=False)
    processed_triggers = fetch_processed_triggers()
    return render_template('test_triggers.html', triggers = triggers, became_available = became_available, processed_triggers=processed_triggers)

@scheduler.task('cron', id='processs_all_triggers_with_cron', minute='*', timezone="Europe/Berlin")
def process_all_triggers():
    triggers = fetch_triggers_for_processing()
    for trigger in triggers:
        process_triggers(trigger[0])
    became_available = fetch_became_available(processed=False)
    print(became_available)
    for available in became_available:
        update_availabilitychange(available[0])
    

def send_email(id, email):
    print(f'hello world: {id}, {email}')

if __name__ == '__main__':
    app.run(debug=True)