import re
from rest_framework.serializers import ValidationError


# 验证手机号
def validate_mobile(value):
    if not re.match(r'^1[3-9]\d{9}$', value):
        raise ValidationError('手机号格式错误')


# 验证邮箱
def validate_email(value):
    if not re.match(r'^\w+@[a-zA-Z0-9]{2,10}(?:\.[a-z]{2,4}){1,3}$', value):
        raise ValidationError('邮箱格式错误')


# 验证账号
def validate_account(value):
    if not re.match(r'^[a-zA-z]\w{5,32}$', value):
        raise ValidationError('账号格式有误，字母开头，字母和数字下划线组合的6-32位字符串')


# 验证电话
def validate_tel(value):
    if not re.match(r'^\d{3,4}-\d{7,8}$', value):
        raise ValidationError('电话号码格式错误')

# 验证企业电话
def validate_mobile_tel(value):
    if not re.match(r'(^1[3-9]\d{9}$)|(^\d{3,4}-\d{7,8}$)', value):
        raise ValidationError('企业电话格式错误')


# 验证身份证
def validate_id(value):
    # (^\d{15}$)|(^\d{18}}$)|(^\d{17}(\d|X|x)$) 15位18位身份证号码
    if not re.match(r'^\d{6}(18|19|20)?\d{2}(0[1-9]|1[012])(0[1-9]|[12]\d|3[01])\d{3}(\d|X)$', value):
        raise ValidationError('身份证号码格式错误')


# 验证护照
def validate_passport(value):
    # 规则： 14/15开头 + 7位数字, G + 8位数字, P + 7位数字, S/D + 7或8位数字,等
    # 样本： 141234567, G12345678, P1234567
    r = r'^1[45][0-9]{7}$|([P|p|S|s]\d{7}$)|([S|s|G|g]\d{8}$)|' \
        r'([Gg|Tt|Ss|Ll|Qq|Dd|Aa|Ff]\d{8}$)|([H|h|M|m]\d{8,10})$'
    if not re.match(r, value):
        raise ValidationError('护照格式错误')


# 验证驾照
def validate_driver_license(value):
    if not re.match(r'^\d{6}(18|19|20)?\d{2}(0[1-9]|1[012])(0[1-9]|[12]\d|3[01])\d{3}(\d|X)$', value):
        raise ValidationError('驾驶证号码格式错误')


# 验证军官证
def validate_military_officer_card(value):
    # 规则： 军 / 兵 / 士 / 文 / 职 / 广 /（其他中文） + "字第" + 4到8位字母或数字 + "号"
    # 样本： 军字第2001988号, 士字第P011816X号
    if not re.match(r'^[\u4E00-\u9FA5](字第)([0-9a-zA-Z]{4,8})(号?)$', value):
        raise ValidationError('军官证号码格式错误')


# 验证台胞证
def validate_tw_card(value):
    # 规则： 新版8位或18位数字， 旧版10位数字 + 英文字母
    # 样本： 12345678 或 1234567890B
    if not re.match(r'^\d{8}|^\d{10}[a-zA-Z]{1}|^\d{18}$', value):
        raise ValidationError('台湾居民来往大陆通行证号码格式错误')


# 验证港澳通行证
def validate_hm_card(value):
    # 规则： H/M + 10位或6位数字
    # 样本： H1234567890
    if not re.match(r'^([H|M]\d{6,10}(\(\w{1}\))?)$', value):
        raise ValidationError('港澳居民来往内地通行证号码格式错误')


# 户口本正则表达式
def validate_account_book(value):
    # 规则： 15位数字, 18位数字, 17位数字 + X
    # 样本： 441421999707223115
    if not re.match(r'(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)', value):
        raise ValidationError('港澳居民来往内地通行证号码格式错误')

# 验证身份证
def validate_id1(value):
    # (^\d{15}$)|(^\d{18}}$)|(^\d{17}(\d|X|x)$) 15位18位身份证号码
    if not re.match(r'^\d{6}(18|19|20)?\d{2}(0[1-9]|1[012])(0[1-9]|[12]\d|3[01])\d{3}(\d|X)$', value):
        raise ValueError('身份证号码格式错误')


# 验证护照
def validate_passport1(value):
    # 规则： 14/15开头 + 7位数字, G + 8位数字, P + 7位数字, S/D + 7或8位数字,等
    # 样本： 141234567, G12345678, P1234567
    r = r'^1[45][0-9]{7}$|([P|p|S|s]\d{7}$)|([S|s|G|g]\d{8}$)|' \
        r'([Gg|Tt|Ss|Ll|Qq|Dd|Aa|Ff]\d{8}$)|([H|h|M|m]\d{8,10})$'
    if not re.match(r, value):
        raise ValueError('护照格式错误')


# 验证驾照
def validate_driver_license1(value):
    if not re.match(r'^\d{6}(18|19|20)?\d{2}(0[1-9]|1[012])(0[1-9]|[12]\d|3[01])\d{3}(\d|X)$', value):
        raise ValueError('驾驶证号码格式错误')


# 验证军官证
def validate_military_officer_card1(value):
    # 规则： 军 / 兵 / 士 / 文 / 职 / 广 /（其他中文） + "字第" + 4到8位字母或数字 + "号"
    # 样本： 军字第2001988号, 士字第P011816X号
    if not re.match(r'^[\u4E00-\u9FA5](字第)([0-9a-zA-Z]{4,8})(号?)$', value):
        raise ValueError('军官证号码格式错误')


# 后台验证证件号码（根据不同的证件）
def check_card_id(type, value):
    card_validate = {
        1: validate_id1,     # 身份证
        2: validate_passport1,   # 护照
        3: validate_driver_license1,  # 驾照
        4: validate_military_officer_card1  # 军官证
    }
    card_validate[type](value)


# 验证统一社会信用代码
def validate_license(value):
    if not re.match(r'^[^_IOZSVa-z\W]{2}\d{6}[^_IOZSVa-z\W]{10}$', value):
        raise ValidationError('统一社会信用代码格式错误')


# 验证邮政编码
def validate_zipcode(value):
    if not re.match(r'^\d{6}$', value):
        raise ValidationError('邮政编码格式错误')


# 验证密码
def validate_password(value):
    if not re.match(r'^[\w\^\$\[\]\{\}`~!@#%&*()-=+?|;:,.<>]{6,16}$', value):
        raise ValidationError('密码格式错误,大小写字母，数字, 符号组合的6-16位字符串')