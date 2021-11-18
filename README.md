# CleverApp

A Flask app to subscribe to a Clever Charging Station in Denmark. If a spot comes available, a notification is given.

## TODO

* Complete user experience when subscribing
* Create option to send out emails when a charger becomes available
* Complete the UI

## Setup:

```sh
cd CleverApp

python3 -m venv env
source env/bin/activate

EXPORT FLASK_APP=app.py

python3 db.py
python3 functions.py

flask run
```