import json
import requests
from  datetime import datetime

KEYWORDS_URL = 'http://api.bosonnlp.com/keywords/analysis'


tokens = ['nO2BUMFs.33400.hZdTIvBQ7gv7', 'ZBM23Hlx.33575.NctEtWEHBEzu', 'bklnK5Yi.33576.m7aaOckOs-yg',
          'OhxuqeTi.33577.uJ5fhPhY8xnj', 'N9FKM0N4.33579.u6FfYP_Wouwe', '9E9945Zy.33580.Ooef_MEFSuip',
          'cyNNmX-T.33606.jeFRqAg7XkRq', '7jLjc4bI.33611.LjDEFnOUKzx3', 'oa-X3KgA.33612.pu2WnZQoOIoP']


def get_keywords(text):
    params = {'top_k': 10}
    data = json.dumps(text)
    headers = {
        'X-Token': 'nO2BUMFs.33400.hZdTIvBQ7gv7',
        'Content-Type': 'application/json'
    }
    resp = requests.post(KEYWORDS_URL, headers=headers, params=params, data=data.encode('utf-8')).json()
    keywords = [i[1] for i in resp if i[0] >= 0.5]
    if not keywords:
        keywords = [i[1] for i in resp][0:2]
    return keywords