from public_models.models import PersonalInfo, Message, EnterpriseBaseinfo
import time,requests
from .models import *
import datetime


# 更新或创建个人信息
def update_or_crete_person(pcode, info):
    ap = PersonalInfo.objects.filter(account_code=info['account_code'])
    pp = PersonalInfo.objects.filter(pcode=pcode)
    if pcode and pp:
        pp.update(**info)
    elif info['account_code'] and ap:
        ap.update(**info)
        pcode = ap[0].pcode
    else:
        person = PersonalInfo.objects.create(**info)
        pcode = person.pcode

    return pcode


#   更新或创建企业信息
def update_or_crete_enterprise(ecode, info):
    ap = EnterpriseBaseinfo.objects.filter(account_code=info['account_code'])
    pp = EnterpriseBaseinfo.objects.filter(ecode=ecode)
    if ecode and pp:
        pp.update(**info)
    elif info['account_code'] and ap:
        ap.update(**info)
        ecode = ap[0].ecode
    else:
        e = EnterpriseBaseinfo.objects.create(**info)
        ecode = e.ecode

    return ecode


# 发送信息
def send_msg(tel, name, state, account_code, sender):
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    msg_data = {
        "name": name
    }
    if state == 2:
        msg_url = 'http://120.77.58.203:8808/sms/patclubmanage/send/auth/1/{}'.format(tel)
        message_content = "您认证的身份信息{}审核已通过。修改身份信息需重新审核，请谨慎修改。".format(name)

    else:
        msg_url = 'http://120.77.58.203:8808/sms/patclubmanage/send/auth/0/{}'.format(tel)
        message_content = "您认证的身份信息{}审核未通过。请登录平台查看。".format(name)

    mag_ret = eval(requests.post(msg_url, data=msg_data, headers=headers).text)['ret']
    if mag_ret == '1':
        Message.objects.create(
            message_title='{}认证信息审核结果通知'.format(name),
            message_content=message_content,
            account_code=account_code,
            send_time=datetime.datetime.now(),
            sender=sender,
            sms=1,
            sms_state=1,
            sms_phone=tel,
            email=0,
            email_state=0
        )
    return True


# 更新基本信息表
def update_baseinfo(obj, code, data):
    obj.objects.filter(**code).update(**data)


# 获取领域
def get_major(user_type, user_code):
    mcode = [i['mcode'] for i in
             MajorUserinfo.objects.values('mcode').filter(mtype=2, user_type=user_type, user_code=user_code)]
    mname = [i['mname'] for i in MajorInfo.objects.values('mname').filter(mcode__in=mcode, state=1)]
    return mname