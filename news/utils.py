from public_models.models import  ParamInfo
from misc.misc import gen_uuid32
import time

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
module_type     :模块类型 如(news,policy)
file_type       :文件类型 如(logo[logo图片],guide[导引图片],editor[富文本图片],attach[附件])
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
            # 文件后缀判断20190701添加
            if file_ext.lower() in ['jpg', 'jpeg', 'png', 'bmp', 'gif']:
                file_dict['file_format'] = 1
            elif file_ext.lower() in ['docx', 'doc', 'xls', 'xlsx', 'pdf']:
                file_dict['file_format'] = 0
            elif file_ext.lower() in ['ppt', 'pptx']:
                file_dict['file_format'] = 2
            elif file_ext.lower() in ['zip', 'rar', 'gzip', 'tar', 'bzip']:
                file_dict['file_format'] = 3
            elif file_ext.lower() in ['mp3',]:
                file_dict['file_format'] = 4
            elif file_ext.lower() in ['mp4', '3gp', 'avi', 'rmvb', 'mkv']:
                file_dict['file_format'] = 5

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




def model_get_attach(AttachmentFileType,AttachmentFileinfo,add_id,news_code):
    tcode = AttachmentFileType.objects.get(tname='attachment').tcode
    attachment_dir = ParamInfo.objects.get(param_name='attachment_dir').param_value
    attachments = AttachmentFileinfo.objects.filter(
        ecode=news_code,
        add_id=add_id,
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
            attach_info['type'] = file_ext
            attach_info['look'] = '{}{}{}'.format(attachment_dir, attach.path, attach.file_name)
            attach_info['down'] = '{}{}{}'.format(attachment_dir, attach.path, attach.file_name)
            attach_info['name'] = attach.file_name
            attachments_list.append(attach_info)

    return attachments_list









