import os
import pytz
import requests
from flask import Flask
from datetime import datetime, timezone

app = Flask(__name__)


client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
map_server = os.getenv('MAP_SERVER_URL')
token_auth_url = "https://sso.smartabyarsmartvillage.org/auth/realms/SMARTVILLAGE/protocol/openid-connect/token"

if client_id is None or client_secret is None:
    print("No CLIENT_ID or CLIENT_SECRET environment variable or defined...Exiting")
    exit(1)
    

token_auth_payload =  {
    'grant_type': 'client_credentials',
    'client_id': client_id,
    'client_secret': client_secret,
}
response = requests.post(token_auth_url, token_auth_payload)


access_token = ""
if response.status_code == 200:
    access_token = response.json().get('access_token')
    print(f"Token: {access_token}")
else:
    print(f"Status: {response.status_code}")

    
api_uri = "https://www.smartabyarsmartvillage.org"
map_data_api = "/api/map-result"
smart_traffic_light_api= "/api/smart-traffic-light-import"


def get_map_data():
    utc_time = datetime.utcnow()
    my_timezone_name = 'America/New_York'
    my_timezone = pytz.timezone(my_timezone_name)
    current_my_time = utc_time.replace(tzinfo=timezone.utc).astimezone(my_timezone)
    formatted_time = current_my_time.strftime("%Y-%m-%dT%H:%M:%S.000") + ("[%s]" % my_timezone_name)
    print(formatted_time)

    headers = {
     'Authorization': f'Bearer {access_token}',
    }
    params = {"rows": "100","fq": f"dateTime:{formatted_time}"}


    map_result = requests.get(url=api_uri+map_data_api, params=params, headers=headers)


    if map_result.status_code == 200:
        map_data = map_result.json()
        print(f"GET Request Successful. Data: {map_data}")
    else:
        print(f"GET Status code: {map_result.status_code}")

    print(f"My map data is:")
    return map_data
    



def update_data(map_data):
    headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json',
    }


    all_coordinates = []
    for item in map_data['list']:
        if 'location' in item and 'coordinates' in item['location']:
            coordinates = item['location']['coordinates']
            all_coordinates.append(coordinates)
        

    light_data = {
        "pk": "veberod-intersection-1",
        "saves": ["entityId", "smartTrafficLightName", "location", "areaServed"],
        "entityId": "urn:ngsi-ld:SmartTrafficLight:SmartTrafficLight-veberod-intersection-1",
        "smartTrafficLightName": "Veberöd intersection 1",
        "areaServed": [
        ]
    }


    light_data['areaServed'] = [{"type": "Point", "coordinates": coordinates} for coordinates in all_coordinates[1:]]




    if map_server is not None:
        put_response = requests.put(url=map_server+smart_traffic_light_api, json={"list":[light_data]}, headers=headers)
        if put_response.status_code == 200:
            put_data = put_response.json()
            print(f"Successful PUT, Updated: {put_data}")
        else:
            print(f"PUT Failed: {put_response.status_code}, {put_response.text}")
    else:
        print("No MAP_SERVER_URL environment variable defined, printing payload to terminal:")
        print(f"My light_data is: {light_data}")
    
@app.route('/health')
def check_data():
    map_data = get_map_data()
    update_data(map_data)
    return "App is running"

if __name__ == '__main__':
         app.run(host='0.0.0.0', port=8081, debug=False)