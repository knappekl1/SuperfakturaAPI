import requests
import json

parameters = {
    "lat": 50,
    "lon": 14.5
}
# response = requests.get("http://api.open-notify.org/astros.json") jiný endpoint

response = requests.get("http://api.open-notify.org/iss-pass.json", params=parameters)

# print(response.status_code)

def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, indent=4, sort_keys=True)
    print(text)
       

PassTimes=response.json()["response"]


risetimes=[]

for d in PassTimes:
    rise=d['risetime']
    risetimes.append(rise)

print(risetimes)


