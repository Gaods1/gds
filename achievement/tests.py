import os
import re
import shutil
from django.test import TestCase
i= '/home/python/Pictures/uploads/微信图片_20180307150756_副本.jpg'
#b = i[:25]+i[30:]
b = '/home/python/Downloads/微信图片_20180307150756_副本.jpg'
#print(b)
#shutil.move(i, b)
#list = os.listdir(url)
    #list1 = []
    #if len(list)!=0:
        #list = [i for i in list if i.endswith('pdf') or i.endswith('jpg')]
        #for i in list
ParamInfo = 'uploads'
if i.endswith('pdf') or i.endswith('jpg'):
    i = re.findall(ParamInfo + r"(.+)", i)
    i = ''.join(i)
print(i)