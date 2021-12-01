# CleverApp

A Flask app to subscribe to a Clever Charging Station in Denmark. If a spot comes available, a notification is given.

This application is based on:

- Google Cloud function to scrape Clever to figure out if there's charging station that became available
- Flask app for the UI
- MySQL database for storing data and handling trigger(s)
- Gmail for sending out email

## TODO

* Update emails send to a proper service like Mailgun
* Improve UI to make it more pleasent to look at

## Setup:

To setup this repository:

```sh
git clone https://github.com/Lindsen13/CleverApp.git
cd CleverApp

#Initate virtual environment
python3 -m venv env
source env/bin/activate
python3 -m pip --upgrade pip
python3 -m pip install -r requirements.txt

#Set environmental variables for MySQL database:
export SQL_USER="username"
export SQL_PASSWORD="password"
export SQL_HOST="host"
export SQL_DATABASE="database"

#Set environmental variables for Google Cloud project
export GOOGLE_APPLICATION_CREDENTIALS="JSON_FILE"
export GCP_PROJECT_ID="PROJECT_ID"
export GCP_LOCATION="LOCATION"
export GCP_CLOUD_SCHEDULER="GCP_FUNCTION_NAME"

#Set environmental variables for gmail (to be able to send out emails)
export GMAIL_PASSWORD="GMAIL_PASSWORD"
export GMAIL_MAIL="GMAIL_MAIL"

#Export flask app so we can run "flask run" to start the application
export FLASK_APP=app.py

#Lets populate the database with tables and all locations from Clever:
python3 db.py
python3 functions.py

#Deploy GCP function
#--currently done with github workflow when pushed to 'main' branch

#Run the flask app
flask run
```