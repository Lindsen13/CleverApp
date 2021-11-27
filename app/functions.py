from db import insert_addresses
import requests
import logging

logging.basicConfig(level=logging.INFO)

def location_processor(full=False):
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
        insert_addresses(
            id = id,
            address = address
        )
        logging.info(f'Inserted id {id}. {address=}')

if __name__ == '__main__':
    location_processor(full=True)