from django.db import models
import time

# Create your models here.

class Nstad(models.Model):
    serial = models.AutoField(primary_key=True)
    result_id = models.IntegerField(unique=True,blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True,default=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))


    class Meta:
        managed = False
        db_table = 'nstad'

