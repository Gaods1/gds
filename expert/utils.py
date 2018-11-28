from public_models.models import PersonalInfo, Message
import time,requests
from .models import *
import datetime
import shutil, os


# 更新或创建个人信息
def update_or_crete_person(pcode, info):
    p = PersonalInfo.objects.filter(account_code=info['account_code'])
    if pcode:
        person = PersonalInfo.objects.filter(pcode=pcode).update(**info)
    elif p:
        p.update(**info)
        pcode = p[0].pcode
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
        message_content = "您认证的身份信息{}审核已通过。修改身份信息需重新审核，请谨慎修改。".format(name)

    else:
        msg_url = 'http://120.77.58.203:8808/sms/patclubmanage/send/auth/0/{}'.format(tel)
        message_content = "您认证的身份信息{}审核未通过。请登录平台查看。".format(name)

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
    obj.objects.filter(**code).update(**data)


# 附件获取
def get_file(ecode, type):
    tcode = AttachmentFileType.objects.get(tname=type).tcode
    files = AttachmentFileinfo.objects.filter(tcode=tcode, ecode=ecode, state=1)
    if files:
        fname = files.order_by('-insert_time')[0].file_name
        url = '{}/expert/{}/{}/{}'.format(ParamInfo.objects.get(param_code=1), tcode, ecode, fname)
    else:
        url = ''
    return url


# 移动附件
def mv_file(file_list):
    for file in file_list:
        if not file:
            continue
        new_path = file.replace(ParamInfo.objects.get(param_code=1).param_value,
                                  ParamInfo.objects.get(param_code=2).param_value)
        new_dir = '/'.join(new_path.split('/')[0:-1]) + '/'
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)
        shutil.move(file, new_dir)
    return True