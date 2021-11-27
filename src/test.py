from googleapiclient import discovery
from oauth2client.client import GoogleCredentials

def scheduler(enable=True):
    credentials = GoogleCredentials.get_application_default()

    service = discovery.build('cloudscheduler', 'v1', credentials=credentials)

    name = 'projects/clever-project-333313/locations/us-central1/jobs/runCleverSchedulers'

    request = service.projects().locations().jobs().get(name=name)
    response = request.execute()
    if enable == True:
        if response['state'] == 'ENABLED':
            print(f"State is {response['state']}. Not doing anything")
        else:
            print("Resuming...")
            request = service.projects().locations().jobs().resume(name=name)
            response = request.execute()
    elif enable == False:
        if response['state'] == 'PAUSED.':
            print(f"State is {response['state']}. Not doing anything")
        else:
            print("Pausing...")
            request = service.projects().locations().jobs().pause(name=name)
            response = request.execute()

if __name__ == "__main__":
    scheduler(enable=True)