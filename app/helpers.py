import urllib.request
import json


# Extract picture - Dog
def getPicture():
    picture = "https://bit.ly/3gDmzHO"
    req = urllib.request.Request('https://dog.ceo/api/breeds/image/random')
    with urllib.request.urlopen(req) as resp:
        if resp.status == 200:
            json_data = json.loads(resp.read().decode('utf-8'))
            picture = json_data['message']
    return picture
