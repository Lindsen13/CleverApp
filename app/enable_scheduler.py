from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
import os
import logging

logging.basicConfig(level=logging.INFO)

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

if __name__ == "__main__":
    scheduler(enable=False)