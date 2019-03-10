from django.db import models
from misc.misc import gen_uuid32
from public_models.models import AttachmentFileinfo,AttachmentFileType,ParamInfo
from public_models.models import SystemDistrict

# Create your models here.


# 新闻栏目信息 *
class NewsGroupInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    group_code = models.CharField(unique=True, max_length=64, default=gen_uuid32)
    group_name = models.CharField(unique=True, verbose_name='新闻栏目名称',max_length=64)
    group_memo = models.CharField(verbose_name='新闻栏目描述',max_length=255, blank=True, null=True)
    logo = models.CharField(verbose_name='新闻栏目logo',max_length=255, blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)

    @property
    def logo_path(self):
        logo_path = ''
        tcode = AttachmentFileType.objects.get(tname='logoPhoto').tcode
        attach_fileinfo = AttachmentFileinfo.objects.filter(ecode=self.group_code, tcode=tcode, file_name=self.logo)
        if attach_fileinfo:
            attach_path = attach_fileinfo[0].path
            attachment_dir = ParamInfo.objects.get(param_name='attachment_dir').param_value
            logo_path = '{}{}'.format(attachment_dir, attach_path)
        return logo_path

    class Meta:
        managed = False
        db_table = 'news_group_info'


# 新闻信息表 *
class NewsInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    group_code = models.CharField(max_length=64)
    news_code = models.CharField(unique=True,max_length=64, default=gen_uuid32)
    caption = models.CharField(verbose_name='新闻主标题',max_length=64)
    caption_ext = models.CharField(verbose_name='新闻副标题',max_length=64, blank=True, null=True)
    author = models.CharField(verbose_name='作者名称',max_length=32, blank=True, null=True)
    publisher = models.CharField(verbose_name='发行单位',max_length=32, blank=True, null=True)
    release_date = models.DateTimeField(verbose_name='发布时间',blank=True, null=True)
    up_time = models.DateTimeField(verbose_name='上架时间', blank=True, null=True)
    down_time = models.DateTimeField(verbose_name='下架时间', blank=True, null=True)
    top_tag = models.IntegerField(verbose_name='是否置顶',blank=True, null=True)
    top_time = models.DateTimeField(verbose_name='置顶时间',blank=True, null=True)
    face_pic = models.CharField(verbose_name='新闻导引图片',max_length=64, blank=True, null=True)
    news_body = models.TextField(verbose_name='新闻详情',blank=True, null=True)
    state = models.IntegerField(verbose_name='新闻状态')
    creater = models.CharField(verbose_name='新闻创建者',max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(verbose_name='新闻创建时间',auto_now_add=True)
    district_id = models.IntegerField(verbose_name='新闻所属地区')
    source = models.IntegerField(verbose_name='新闻来源',blank=True, null=True,default=1)
    account_code = models.CharField(verbose_name='审核人',max_length=32, blank=True, null=True)
    check_time = models.DateTimeField(verbose_name='审核时间',blank=True, null=True)
    check_state = models.IntegerField(verbose_name='审核状态',blank=True, null=True)
    count = models.IntegerField(verbose_name='点击量',blank=True, null=True)

    @property
    def face_pic_path(self):
        face_pic_path = ''
        tcode = AttachmentFileType.objects.get(tname='guidePhoto').tcode
        attach_fileinfo = AttachmentFileinfo.objects.filter(ecode=self.news_code, tcode=tcode,file_name=self.face_pic)
        if attach_fileinfo:
            attach_path = attach_fileinfo[0].path
            attachment_dir = ParamInfo.objects.get(param_name='attachment_dir').param_value
            face_pic_path = '{}{}'.format(attachment_dir, attach_path)
        return face_pic_path

    @property
    def group_name(self):
        return NewsGroupInfo.objects.get(group_code=self.group_code).group_name

    @property
    def district_name(self):
        return SystemDistrict.objects.get(district_id=self.district_id).district_name

    @property
    def attachments(self):
        tcode = AttachmentFileType.objects.get(tname='attachment').tcode
        attachment_dir = ParamInfo.objects.get(param_name='attachment_dir').param_value
        attachments = AttachmentFileinfo.objects.filter(
            ecode=self.news_code,
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
                attach_info['file_path'] = '{}{}{}'.format(attachment_dir, attach.path, attach.file_name)
                attachments_list.append(attach_info)

        return attachments_list

    class Meta:
        managed = False
        db_table = 'news_info'


# 政策栏目信息表 *
class PolicyGroupInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    group_code = models.CharField(unique=True, max_length=64, default=gen_uuid32())
    group_name = models.CharField(unique=True,verbose_name='政策法规栏目名称',max_length=64)
    group_memo = models.CharField(verbose_name='政策法规栏目描述',max_length=255, blank=True, null=True)
    logo = models.CharField(verbose_name='政策法规栏目logo',max_length=255, blank=True, null=True)
    state = models.IntegerField(default=1)

    @property
    def logo_path(self):
        logo_path = ''
        tcode = AttachmentFileType.objects.get(tname='logoPhoto').tcode
        attach_fileinfo = AttachmentFileinfo.objects.filter(ecode=self.group_code,tcode=tcode,file_name=self.logo)
        if attach_fileinfo:
            attach_path = attach_fileinfo[0].path
            attachment_dir = ParamInfo.objects.get(param_name='attachment_dir').param_value
            logo_path = '{}{}'.format(attachment_dir,attach_path)
        return logo_path

    class Meta:
        managed = False
        db_table = 'policy_group_info'


# 政策信息表 *
class PolicyInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    group_code = models.CharField(max_length=64)
    policy_code = models.CharField(max_length=64, default=gen_uuid32)
    caption = models.CharField(verbose_name='政策法规主标题',max_length=64)
    caption_ext = models.CharField(verbose_name='政策法规副标题',max_length=64, blank=True, null=True)
    author = models.CharField(verbose_name='作者名称',max_length=64, blank=True, null=True)
    publisher = models.CharField(verbose_name='发行单位',max_length=64, blank=True, null=True)
    release_date = models.DateTimeField(verbose_name='发布时间',blank=True, null=True)
    top_tag = models.IntegerField(verbose_name='是否置顶',blank=True, null=True)
    face_pic = models.CharField(verbose_name='政策法规导引图片',max_length=64, blank=True, null=True)
    news_body = models.TextField(verbose_name='政策法规详情',blank=True, null=True)
    state = models.IntegerField(verbose_name='政策法规状态')
    creater = models.CharField(verbose_name='政策法规创建者',max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(verbose_name='政策法规创建时间',auto_now_add=True)
    district_id = models.IntegerField(verbose_name='政策法规所属地区')
    source = models.CharField(verbose_name='政策法规来源',max_length=255, blank=True, null=True)

    @property
    def face_pic_path(self):
        face_pic_path = ''
        tcode = AttachmentFileType.objects.get(tname='guidePhoto').tcode
        attach_fileinfo = AttachmentFileinfo.objects.filter(ecode=self.policy_code, tcode=tcode, file_name=self.face_pic)
        if attach_fileinfo:
            attach_path = attach_fileinfo[0].path
            attachment_dir = ParamInfo.objects.get(param_name='attachment_dir').param_value
            face_pic_path = '{}{}'.format(attachment_dir, attach_path)
        return face_pic_path

    @property
    def group_name(self):
        return PolicyGroupInfo.objects.get(group_code=self.group_code).group_name

    @property
    def district_name(self):
        return SystemDistrict.objects.get(district_id=self.district_id).district_name

    @property
    def attachments(self):
        tcode = AttachmentFileType.objects.get(tname='attachment').tcode
        attachment_dir = ParamInfo.objects.get(param_name='attachment_dir').param_value
        attachments = AttachmentFileinfo.objects.filter(
            ecode= self.policy_code,
            tcode = tcode,
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
                attach_info['file_path'] = '{}{}{}'.format(attachment_dir,attach.path,attach.file_name)
                attachments_list.append(attach_info)

        return attachments_list

    class Meta:
        managed = False
        db_table = 'policy_info'



