import requests
from .models import *
import datetime
from django.db.models import Q
import os
import shutil


# 更新或创建个人信息
def update_or_crete_person(pcode, info):

    id_person = PersonalInfo.objects.filter(pid_type=info['pid_type'], pid=info['pid'])
    account_person = PersonalInfo.objects.filter(account_code=info['account_code'])
    if account_person and account_person[0].pid_type == info['pid_type'] and account_person[0].pid != info['pid']:
        raise ValueError('此账号已经绑定证件号码，证件号码不允许更改')

    if id_person and id_person[0].account_code and id_person[0].account_code != info['account_code']:
            raise ValueError('此证件号码已经被其他账号注册')

    if id_person and not id_person[0].account_code:
        id_person.update(**info)
        return id_person[0].pcode

    code_person = PersonalInfo.objects.filter(pcode=pcode, account_code=info['account_code'])
    if code_person and pcode:
        code_person.update(**info)
        return pcode

    if account_person:
        account_person.update(**info)
        return account_person[0].pcode

    person_info = PersonalInfo.objects.create(**info)
    return person_info.pcode


# 创建企业信息（如果只有企业名的话）
def create_enterprise(ecode):
    if ecode:
        try:
            e_code = EnterpriseBaseinfo.objects.values_list('ecode', flat=True).get(Q(ecode=ecode) | Q(ename=ecode))
        except Exception as e:
            e_code = EnterpriseBaseinfo.objects.create(ename=ecode).ecode
        return e_code
    return None


#   更新或创建企业信息
def update_or_crete_enterprise(ecode, info):
    license_enterprise = EnterpriseBaseinfo.objects.filter(business_license=info['business_license'])
    account_enterprise = EnterpriseBaseinfo.objects.filter(account_code=info['account_code'])

    if account_enterprise and account_enterprise[0].business_license != info['business_license']:
        raise ValueError('此账号已经绑定统一社会信用码，统一社会信用码不允许更改')

    if license_enterprise and license_enterprise[0].account_code and \
            license_enterprise[0].account_code != info['account_code']:
        raise ValueError('此统一社会信用码已经被其他账号注册')

    if license_enterprise and not license_enterprise[0].account_code:
        license_enterprise.update(**info)
        return license_enterprise[0].ecode

    code_enterprise = EnterpriseBaseinfo.objects.filter(ecode=ecode, account_code=info['account_code'])
    if ecode and code_enterprise:
        code_enterprise.update(**info)
        return ecode

    if account_enterprise:
        account_enterprise.update(**info)
        return account_enterprise[0].ecode

    enterprise = EnterpriseBaseinfo.objects.create(**info)
    return enterprise.ecode


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
    if int(mag_ret) == 1:
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


# 获取领域code
def get_major_code(user_type, user_code):
    mcode = MajorUserinfo.objects.values_list('mcode', flat=True).filter(
        mtype=2, user_type=user_type, user_code=user_code)
    return mcode


# 获取领域
def get_major(mcode):
    mname = MajorInfo.objects.values_list('mname', flat=True).filter(mcode__in=mcode, state=1)
    return mname


# 验证前端账号是否具有当前信息
def check_identity(account_code, identity, info):
    try:
        IdentityAuthorizationInfo.objects.get(account_code=account_code, identity_code=identity)
        raise ValueError('所选账号已经认证当前身份')
    except IdentityAuthorizationInfo.DoesNotExist:
        IdentityAuthorizationInfo.objects.create(**info)


# 验证前端账号是否具有当前信息
def check_identity2(account_code, identity, info):
    identity = IdentityAuthorizationInfo.objects.filter(account_code=account_code, identity_code=identity)
    if identity:
        identity.update(**info)
    else:
        IdentityAuthorizationInfo.objects.create(**info)


# 验证证件号码是否已注册
def check_id(account_code, id_type, pid):
    p = PersonalInfo.objects.filter(pid_type=id_type, pid=pid)
    if p and p[0].account_code != account_code:
        raise ValueError('此证件号码已被他人使用')


# 根据account_code 来更新或者创建person_info
def create_or_update_person(account_code, info):
    check_id(account_code, info['pid_type'], info['pid'])
    person = PersonalInfo.objects.filter(account_code=account_code)
    if person:
        person.update(**info)
        return person[0].pcode
    else:
        p = PersonalInfo.objects.create(**info)
        return p.pcode


# 根据 account_code 来更新或者创建e_info
def create_or_update_enterprise(account_code, info):
    e = EnterpriseBaseinfo.objects.filter(business_license=info['business_license'])
    if e and e[0].account_code != account_code:
        raise ValueError('此统一社会信用代码已被他人使用')
    einfo = EnterpriseBaseinfo.objects.filter(account_code=account_code)
    if einfo:
        einfo.update(**info)
        return einfo[0].ecode
    else:
        ee = EnterpriseBaseinfo.objects.create(**info)
        return ee.ecode



# 插入领域与身份相关表
def crete_major(mtype, user_type, user_code, majors):
    MajorUserinfo.objects.filter(user_code=user_code, user_type=user_type, mtype=mtype).delete()
    if majors:
        major_user_info = {
            'mtype': mtype,
            'user_type': user_type,
            'user_code': user_code
        }
        major_user_info_list = []
        for m in majors:
            major_user_info['mcode'] = m
            major_user_info_list.append(MajorUserinfo(**major_user_info))
        MajorUserinfo.objects.bulk_create(major_user_info_list)


# 图片url转路径
def url_to_path(url):
    # 默认替换临时， 当type为True为替换正式
    path = None
    if url:
        formal_path = ParamInfo.objects.get(param_name='upload_dir').param_value  # 多媒体文件正式路径
        formal_url = ParamInfo.objects.get(param_name='attachment_dir').param_value    # 读取多媒体文件的正式路径
        temp_path = ParamInfo.objects.get(param_name='upload_temp_dir').param_value  # 多媒体文件临时路径
        temp_url = ParamInfo.objects.get(param_name='attachment_temp_dir').param_value  # 读取多媒体文件的正式路径
        if temp_url in url:
            path = url.replace(temp_url, temp_path)
        # elif formal_url in url:
        #     path = url.replace(formal_url, formal_path)
    return path


# 复制图片到正式路径
def copy_img(url, identity, img_type, ecode, creater):
    try:
        upload_temp_dir = ParamInfo.objects.get(param_name='upload_temp_dir').param_value
        if url and upload_temp_dir in url and os.path.isfile(url):
            file_name = url.split('/')[-1]
            formal_path = ParamInfo.objects.get(param_name='upload_dir').param_value
            tcode = AttachmentFileType.objects.get(tname=img_type).tcode
            file_formal_path = os.path.join(formal_path, identity, tcode, ecode)
            file_path = os.path.join(file_formal_path, file_name)
            if not os.path.exists(file_formal_path):
                os.makedirs(file_formal_path)
            formal_file = shutil.copyfile(url, file_path)
            path = os.path.join(identity, tcode, ecode) + '/'
            if not img_type != 'consultEditor':
                AttachmentFileinfo.objects.filter(ecode=ecode, tcode=tcode, file_name=file_name).delete()
                AttachmentFileinfo.objects.create(ecode=ecode, tcode=tcode, file_format=1, file_name=file_name,
                                                  state=1, publish=1, file_order=0, operation_state=3,
                                                  creater=creater, path=path, file_caption=file_name)
            return formal_file
        return None
    except Exception as e:
        raise ValueError(e)


# 删除附件
def remove_img(url):
    if url and os.path.isfile(url):
        os.remove(url)
