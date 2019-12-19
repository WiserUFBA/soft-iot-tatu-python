import json
import requests




with open('settings.json') as f:
	settings = json.load(f)

API_KEY = settings["api_key"]

data = {
	'considerIp': True,
	'wifiAccessPoints':[]
}

headers = {"Content-Type": "application/json"}
url = "https://www.googleapis.com/geolocation/v1/geolocate?key=" + settings["api_key"]
#url = "https://location.services.mozilla.com/v1/geolocate?key=" + settings["api_key"]
response = requests.post(url, headers=headers, data=json.dumps(data))
googleLocation = json.loads(response.content) 

with open('location.json') as f:
	location = json.load(f)

location["location"]["lat"] = googleLocation["location"]["lat"]
location["location"]["lng"] = googleLocation["location"]["lng"]
location["accuracy"] = googleLocation["accuracy"]

with open('location.json', 'w') as output:
	json.dump(location, output, indent=4)

