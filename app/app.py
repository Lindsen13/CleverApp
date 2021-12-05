import os
from flask import Flask, render_template, request, flash

from db import fetch_addresses, \
    insert_triggers, \
    fetch_triggers, \
    fetch_availability
from enable_scheduler import scheduler

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
        scheduler(enable=True)
        flash(f'You were successfully subscribed for charger {id}')
    triggers = fetch_triggers(id=id)
    address = fetch_addresses(id=id)
    available = fetch_availability(id)
    return render_template('triggers.html', id=id, triggers = triggers, address=address, available=available)

if __name__ == '__main__':
    #app.run(debug=True)
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))