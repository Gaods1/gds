from public_models.models import PersonalInfo, Message
import time,requests
from .models import *
import datetime


code_dict = {
    "expert": "expert_code"
}
pinfo_item = {
    "expert" : {
        "name":"expert_name",
        "id_type":"expert_id_type",
        "id":"expert_id",
        "mobile":"expert_mobile",
        "tel":"expert_tel",
        "email":"expert_email",
        "education":"education",
        "abstract":"expert_abstract",
        "account":"account_code"
    },
}

# 更新或创建个人信息
def update_or_crete_person(pcode, info):
    if pcode:
        person = PersonalInfo.objects.filter(pcode=pcode).update(**info)
    else:
        person = PersonalInfo.objects.create(**info)
        pcode = person.pcode

    return pcode


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
        message_content = "您认证的身份信息{}审核未通过。请登录平台查看。".format(name)
    else:
        msg_url = 'http://120.77.58.203:8808/sms/patclubmanage/send/auth/0/{}'.format(tel)
        message_content = "您认证的身份信息{}审核已通过。修改身份信息需重新审核，请谨慎修改。".format(name)

    mag_ret = eval(requests.post(msg_url, data=msg_data, headers=headers).text)['ret']
    if mag_ret != '1':
        raise TypeError("短信发送失败")

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
    obj.objects.filter(**{code_dict[obj]:code}).update(**data)


# 附件获取
def get_file(ecode, type):
    tcode = AttachmentFileType.objects.get(tname=type).tcode
    files = AttachmentFileinfo.objects.filter(tcode=tcode, ecode=ecode)
    if files:
        fname = files.order_by('-insert_time')[0].file_name
        url = '{}/expert/{}/{}/{}'.format(ParamInfo.objects.get(param_code=0), tcode, ecode, fname)
    else:
        url = ''
    return url