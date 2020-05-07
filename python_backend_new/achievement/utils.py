import requests
import json
def massege(url,body,headers):
    response = requests.post(url, data=body,headers=headers)

def diedai(raw_list):
    for x in raw_list:
        yield x


