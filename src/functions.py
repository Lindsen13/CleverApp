from db import insert_availability, insert_addresses
import requests
from geopy.geocoders import Nominatim
import time

def location_processor(full=False):
    geolocator = Nominatim(user_agent="CleverConverter")

    url = 'https://clever-app-prod.firebaseio.com/chargers/v3/locations.json'
    output = requests.get(url)
    if output.status_code != 200:
        raise ValueError(f'Error in fetching data: {output.status_code}')
    if full:
        charger_to_parse = list(output.json().keys())
    else:
        charger_to_parse = list(output.json().keys())[:3]
    for id in charger_to_parse:
        address = str(output.json().get(id).get('address').get('line1')) + ', ' + str(output.json().get(id).get('address').get('line2'))
        geo_loc = geolocator.geocode(address)
        if geo_loc:
            lat, lon = geo_loc.latitude, geo_loc.longitude
        else:
            lat, lon = None, None
        insert_addresses(
            id = id,
            address = address,
            lat = lat,
            lon = lon
        )
        print(f'Inserted id {id}. {address=}, {lat=}, {lon=}')
        time.sleep(0.5)

def process_triggers(id):
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
            #available = 1
            insert_availability(id = id, availability = available)

if __name__ == '__main__':
    location_processor(full=False)