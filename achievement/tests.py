import shutil
from django.test import TestCase
i = '/home/python/Pictures/微信图片_20180307150756_副本.jpg'
#b = i[:25]+i[30:]
b = '/home/python/Downloads/微信图片_20180307150756_副本.jpg'
#print(b)
shutil.move(i, b)