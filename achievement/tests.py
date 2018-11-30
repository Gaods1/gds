import os
import re
import shutil
from django.test import TestCase

from .models import ResultsInfo
from public_models.models import AttachmentFileinfo

i= '/home/python/Pictures/uploads/微信图片_20180307150756_副本.jpg'
#b = i[:25]+i[30:]
b = '/home/python/Picture'
#print(b)
#shutil.move(i, b)
#list = os.listdir(url)
    #list1 = []
    #if len(list)!=0:
        #list = [i for i in list if i.endswith('pdf') or i.endswith('jpg')]
        #for i in list
#ParamInfo = 'uploads'
#if i.endswith('pdf') or i.endswith('jpg'):
    #i = re.findall(ParamInfo + r"(.+)", i)
    #i = ''.join(i)
#print(i)

#list = os.listdir(b)
#print(list)
#list1 = []
#if len(list) != 0:
    #for i in list:
        #if i.endswith('pdf') or i.endswith('jpg'):
            ###i = re.findall(ParamInfo.objects.get(param_code=0).param_value + r"(.+)", i)
            #i = ''.join(i)
            #list1.append(i)
#print(list1)

#url = '/{}/{}/{}'.format(a,b,c)
#print(url)
files = ResultsInfo.objects.all()
print(type(files))
file = ResultsInfo.objects.filter(show_state=2)
print(type(file))
# operation_state_list = [file.operation_state for file in files]
# 遍历所有状态下的对象
for file in files:
    # 找出伪删除的对象并从表中删除
    if file.show_state == 0:

        #url = '{}{}/{}/{}/{}'.format(xiangdui, canshu, tcode, ecode, file.file_name)
        file.delete()
        print(file.show_state)
        print(len(files))
        # 找出该路径下是否有文件并删除
        #if os.path.exists(url):
            #os.remove(url)
    # 将临时文件转为正式文件
    else:
        #url_x = '{}{}/{}/{}/{}'.format(juedui, canshu, tcode, ecode, file.file_name)
        ##shutil.move(url_x, url_j)
        print('******')