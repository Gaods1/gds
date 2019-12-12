import json
import requests
from datetime import datetime
from public_models.models import Systematic_info

import json

from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.nlp.v20190408 import nlp_client, models


KEYWORDS_URL = 'http://api.bosonnlp.com/keywords/analysis'


def get_token(group):
    try:
        systema = Systematic_info.objects.filter(group=group, state=1).order_by('serial').first()
        secretid = json.loads(systema.value).get('secretid', None)
        secretkey = json.loads(systema.value).get('secretkey', None)
        name = systema.name
        return secretid, secretkey
    except Exception as e:
        return None, None


def transfer_url(params):
    secretid, secretkey = get_token('deep')
    if not secretid:
        return None
    httpProfile = HttpProfile()
    httpProfile.endpoint = "nlp.tencentcloudapi.com"

    clientProfile = ClientProfile()
    clientProfile.httpProfile = httpProfile

    req = models.KeywordsExtractionRequest()

    cred = credential.Credential(secretid, secretkey)
    client = nlp_client.NlpClient(cred, "ap-guangzhou", clientProfile)
    req.from_json_string(params)
    resp = client.KeywordsExtraction(req)
    return resp.to_json_string()


def get_keywords(text):
    params = {}
    params['Text'] = text
    params = json.dumps(params)
    resp= transfer_url(params)
    if resp:
        resp = json.loads(resp).get("Keywords")
    keywords = [i['Word'] for i in resp if i["Score"] >= 0.8]
    if not keywords:
        keywords = [i['Word'] for i in resp][0:2]
    return keywords
