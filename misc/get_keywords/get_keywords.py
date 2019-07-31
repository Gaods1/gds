import json
import requests
from datetime import datetime
from public_models.models import Systematic_info

KEYWORDS_URL = 'http://api.bosonnlp.com/keywords/analysis'


def get_token(group):
    try:
        systema = Systematic_info.objects.filter(group=group, state=1).order_by('serial').first()
        token = json.loads(systema.value).get('token', None)
        name = systema.name
        return token, name
    except Exception as e:
        return None, None


def update_systematic(name):
    Systematic_info.objects.filter(name=name).update(state=0)


def transfer_url(text):
    token, name = get_token('deep')
    if not token:
        return [], None
    params = {'top_k': 10}
    data = json.dumps(text)
    headers = {
        'X-Token': token,
        'Content-Type': 'application/json'
    }
    resp = requests.post(KEYWORDS_URL, headers=headers, params=params, data=data.encode('utf-8'))
    return resp, name


def get_keywords(text):
    resp, name = transfer_url(text)
    if resp:
        resp = resp.json()
    if not isinstance(resp, list):
        update_systematic(name)
        resp, name = transfer_url(text)
        resp = resp.json()
    keywords = [i[1] for i in resp if i[0] >= 0.5]
    if not keywords:
        keywords = [i[1] for i in resp][0:2]
    return keywords
