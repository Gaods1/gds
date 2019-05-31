from public_models.models import  ParamInfo
from misc.misc import gen_uuid32
import time,smtplib,requests
from email.mime.text import MIMEText
from email.utils import formataddr

"""
获取多媒体上传参数
1:upload_temp_dir        (多媒体上传临时目录绝对路径)
2:upload_dir             (多媒体上传正式目录绝对路径)
3:attachment_temp_dir    (多媒体显示临时网址)
4:attachment_dir         (多媒体显示正式网址)
"""
def get_attach_params():
    params = ParamInfo.objects.filter(param_code__in=[1,2,3,4])
    params_dict = {}
    if params:
        for obj in params:
            params_dict[int(obj.param_code)] = obj.param_value
    return params_dict


"""
获取多媒体详细信息
file_list       :上传多媒体文件列表
module_type     :模块类型 如(activity)
file_type       :文件类型 如(activity_cover[活动封面图片],editor[富文本编辑器],attach[附件])
file_dir        :文件保存最后一级目录 :各种唯一code
param_dict      :多媒体上传参数
"""
def get_attach_info(file_list,module_type,file_type,file_dir,params_dict):
    year = time.strftime('%Y', time.localtime(time.time()))
    month = time.strftime('%m', time.localtime(time.time()))
    day = time.strftime('%d', time.localtime(time.time()))
    date_dir = '{}{}{}'.format(year, month, day)
    fileinfo_dict = {}
    if file_list:
        file_normal_dir = '{}/{}/{}/{}/{}/'.format(params_dict[2].rstrip('/'), module_type, file_type, date_dir,file_dir)  # 文件保存正式绝对目录
        for file_info in file_list:
            file_dict = {}
            file_info_arr= file_info.split('/')
            file_caption = file_info_arr.pop()  #上传的原文件名
            arr_file = file_caption.split('_')
            real_file_caption = "_".join(arr_file[1:])
            # real_file_caption = file_caption[33:]
            file_arr = file_caption.split('.')
            file_ext = file_arr.pop()           #上传的文件后缀
            if file_ext.lower() in ['jpg','jpeg','png','bmp','gif']:
                file_dict['file_format'] = 1
            elif file_ext.lower() in ['docx','doc','xls','xlsx','pdf','zip']:
                file_dict['file_format'] = 0
            elif file_ext.lower() in ['mp3']:
                file_dict['file_format'] = 2
            elif file_ext.lower() in ['mp4','3gp','avi','rmvb','mkv']:
                file_dict['file_format'] = 3
            file_name = '{}.{}'.format(gen_uuid32(),file_ext)  #新的文件名保存到附件表
            file_temp_path = file_info.replace(params_dict[3],params_dict[1]) #文件保存临时绝对路径
            file_normal_path = '{}/{}'.format(file_normal_dir,file_name)     #文件保存正式绝对路径
            file_normal_url = file_normal_path.replace(params_dict[2],params_dict[4]) #文件显示正式网址
            attach_path = '{}/{}/{}/{}/'.format(module_type,file_type,date_dir,file_dir)
            file_dict['file_temp_path'] = file_temp_path
            file_dict['file_normal_path'] = file_normal_path
            file_dict['attach_path'] = attach_path
            file_dict['file_name'] = file_name
            file_dict['file_caption'] = real_file_caption
            file_dict['file_temp_url'] = file_info
            file_dict['file_normal_url'] = file_normal_url
            fileinfo_dict[file_info] = file_dict

        fileinfo_dict['file_normal_dir'] = file_normal_dir

    return fileinfo_dict




def model_get_attach(AttachmentFileType,AttachmentFileinfo,tname,activity_code):
    tcode = AttachmentFileType.objects.get(tname=tname).tcode
    attachment_dir = ParamInfo.objects.get(param_name='attachment_dir').param_value
    attachments = AttachmentFileinfo.objects.filter(
        ecode=activity_code,
        tcode=tcode,
        state=1,
    ).all()
    attachments_list = []

    if attachments:
        for attach in attachments:
            attach_info = {}
            file_arr = attach.file_caption.split('.')
            file_ext = file_arr.pop()
            attach_info['file_caption'] = attach.file_caption
            if file_ext.lower() in ['jpg','jpeg','png','bmp','gif']:
                attach_info['file_format'] = 1
                file_ext = 'image'
            elif file_ext.lower() in ['docx','doc','xls','xlsx','pdf','zip']:
                attach_info['file_format'] = 0
            elif file_ext.lower() in ['mp3']:
                attach_info['file_format'] = 2
            elif file_ext.lower() in ['mp4','3gp','avi','rmvb','mkv']:
                attach_info['file_format'] = 3
            attach_info['type'] = file_ext
            attach_info['look'] = '{}{}{}'.format(attachment_dir, attach.path, attach.file_name)
            attach_info['down'] = '{}{}{}'.format(attachment_dir, attach.path, attach.file_name)
            attach_info['name'] = attach.file_name
            attachments_list.append(attach_info)

    return attachments_list


def send_message(sms_state,mobile,activity_title):
    sms_url = '{}{}{}{}'.format("http://120.77.58.203:8808/sms/patclubmanage/send/verify/", sms_state, "/", mobile)
    sms_data = {
        'type': '活动报名',
        'name': activity_title,
    }
    # json.dumps(sms_data)
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    result_info = eval(requests.post(sms_url, data=sms_data, headers=headers).text)
    if int(result_info['ret']) == 1:
        result = {'state':1,'msg':'发送成功'}
        return result
    else:
        code_dict = {
            'syserr' : '系统异常，请尝试切换其它短信接口发送',
            'limiterr' : '业务限流，发送频率太高或次数太多，尝试重新发送或切换短信接口',
            'serverr' : '服务异常，请尝试重新发送',
            'blacklisterr' : '用户手机号在黑名单，请切换短信接口',
            'INVALID_PARAMETERS' : '短信查询接口SendDate日期格式yyyyMMdd',
            'MOBILE_NUMBER_ILLEGAL' : '请传入11位国内号段的手机号码',
            'MOBILE_COUNT_OVER_LIMIT' : '短信接收号码,支持以英文逗号分隔的形式进行批量调用',
            'PARAM_LENGTH_LIMIT' : '单个变量长度限制在20字符内',
            'PARAM_NOT_SUPPORT_URL' : '变量不支持透传url，同时检查通过变量是否透传了一些敏感信息触发关键字',
            'TEMPLATE_PARAMS_ILLEGAL' : '变量不支持透传url，同时检查通过变量是否透传了一些敏感信息触发关键字'
        }
        msg = result_info['msg']+code_dict[result_info['code']]
        result = {'state': 0, 'msg': msg}
        return result

def send_email(receiver_name,receiver_email,content):
    mail_host = "smtphz.qiye.163.com"  # 设置服务器
    mail_user = "patclub@imzgc.com"  # 用户名
    mail_pass = "1212121Pc"  # 口令
    sender = 'patclub@imzgc.com'

    try:
        msg = MIMEText(content, 'plain', 'utf-8')
        msg['From'] = formataddr(["科技成果转化平台", sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        msg['To'] = formataddr([receiver_name, receiver_email])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        msg['Subject'] = "活动报名审核通知"  # 邮件的主题，也可以说是标题

        server = smtplib.SMTP_SSL("smtphz.qiye.163.com", 465)  # 发件人邮箱中的SMTP服务器，端口是25
        server.login(mail_user, mail_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
        server.sendmail(sender, [receiver_email, ], msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.quit()  # 关闭连接
        result = True
    except Exception:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False
        result = False

    return result









