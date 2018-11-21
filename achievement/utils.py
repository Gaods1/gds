import requests
import json
def massege(url,body):
    response = requests.post(url, data=json.dumps(body))
