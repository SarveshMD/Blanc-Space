from secret import CLIENT_ID, CLIENT_SECRET
import requests
import json
from datetime import datetime

token_endpoint_uri = "https://accounts.spotify.com/api/token/"
headers = {"Content-Type": "application/x-www-form-urlencoded"}
data = {
    "grant_type": "client_credentials",
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET
}

response = requests.post(token_endpoint_uri, data=data, headers=headers)
content = json.loads(response.text)
content["load_time"] = str(datetime.now())
content = json.dumps(content, indent=2)
with open("token.json", "w") as file:
    file.write(content)
print(content)
print("Written to token.json successfully...")
