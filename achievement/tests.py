from django.test import TestCase
from rest_framework import serializers
from django.db import transaction
import requests
import json
from datetime import datetime

from .models import *


# Create your tests here.

#成果审核历史记录通过序列化
class ResultCheckHistorySerializer(serializers.ModelSerializer):
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    class Meta:
        model = ResultCheckHistory
        fields = '__all__'

    def create(self, validated_data):
        #建立事物机制
        with transaction.atomic():
            # 创建一个保存点
            save_id = transaction.savepoint()

            # 修改成果持有人信息表状态
            try:
                ea = ResultsOwnerInfo.objects.get(r_code=validated_data['apply_code'])
                ea.status = 1
                ea.save()
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                raise serializers.ValidationError('成果持有人信息表更新失败')

            # 角色个人或者企业
            try:
                ea = ResultsOwnerInfo.objects.get(r_code=validated_data['apply_code'])
                if ea.owner_type == 1:
                    rr = ResultOwnerpBaseinfo.objects.get(owner_code=ea.owner_code)
                    rr.status = 1
                    rr.save()
                rr = ResultOwnereBaseinfo.objects.get(owner_code=ea.owner_code)
                rr.status = 1
                rr.save()
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                raise serializers.ValidationError('角色个人或者企业信息表更新失败')

            # 修改成果合作方式信息表状态
            try:
                ea = ResultsCooperationTypeInfo.objects.get(rr_code=validated_data['apply_code'])
                ea.status = 11
                ea.save()
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                raise serializers.ValidationError('成果合作方式信息表更新失败')

            # 修改成果申请表状态
            try:
                rr = RrApplyHistory.objects.get(a_code=validated_data['apply_code'])
                rr.status = 11
                rr.save()
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                raise serializers.ValidationError('成果申请表更新失败')
            # 修改成果基本信息表状态
            try:
                ii = ResultsInfo.objects.get(r_code=validated_data['apply_code'])
                ii.status = 1
                ii.save()
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                raise serializers.ValidationError('成果基本信息表更新失败')

            # 创建历史记录表
            try:
                history = ResultCheckHistory.objects.create(validated_data)
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                raise serializers.ValidationError('历史记录创建失败')

            transaction.savepoint_commit(save_id)

            # 发送短信
            try:
                ownerp = ResultOwnerpBaseinfo.objects.get(pcod=validated_data['apply_code'])
                tel = ownerp.owner_mobile
            except Exception as e:
                raise serializers.ValidationError('发送短信失败')
            else:
                url = 'http://120.77.58.203/sms/patclubmanage/send/verify/1/'+tel
                body = {'type': '通过', 'name': ii.r_name, 'reason':history.opinion}
                response = requests.post(url, data=json.dumps(body))

            # 推送表信息
            try:
                mm = Message.objects.create({
                    'message_title':'成果消息审核通知',
                    'message_content':history.opinion,
                    'account_code':ii.account_code,
                    'state':0,
                    'send_time':datetime.now(),
                    'read_time':datetime.now(),
                    'sender':self.context['request'].user.user_name,
                    'sms':'',
                    'sms_state':'',
                    'sms_phone':'',
                    'email':'',
                    'email_state':'',
                    'email_account':''

                })

            except Exception as e:
                raise serializers.ValidationError('推送表生成失败')

            return history

# 成果审核历史记录未通过序列化
class NoResultCheckHistorySerializer(serializers.ModelSerializer):
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = ResultCheckHistory
        fields = '__all__'

    def create(self, validated_data):
        # 建立事物机制
        with transaction.atomic():
            # 创建一个保存点
            save_id = transaction.savepoint()

            # 修改成果持有人信息表状态
            try:
                ea = ResultsOwnerInfo.objects.get(r_code=validated_data['apply_code'])
                ea.status = 0
                ea.save()
                a = ea.owner_type
                if a==1:
                    pass

            except Exception as e:
                transaction.savepoint_rollback(save_id)
                raise serializers.ValidationError('成果持有人信息表更新失败')

            # 角色个人或者企业
            try:
                ea = ResultsOwnerInfo.objects.get(r_code=validated_data['apply_code'])
                if ea.owner_type == 1:
                    rr = ResultOwnerpBaseinfo.objects.get(owner_code=ea.owner_code)
                    rr.status = 9
                    rr.save()
                rr = ResultOwnereBaseinfo.objects.get(owner_code=ea.owner_code)
                rr.status = 9
                rr.save()
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                raise serializers.ValidationError('角色个人或者企业信息表更新失败')

            # 修改成果合作方式信息表状态
            try:
                ea = ResultsCooperationTypeInfo.objects.get(rr_code=validated_data['apply_code'])
                ea.status = 4
                ea.save()
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                raise serializers.ValidationError('成果合作方式信息表更新失败')

            # 修改成果申请表状态
            try:
                rr = RrApplyHistory.objects.get(rr_code=validated_data['apply_code'])
                rr.status = 4
                rr.save()
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                raise serializers.ValidationError('成果申请表更新失败')
            # 修改成果基本信息表状态
            try:
                ii = ResultsInfo.objects.get(r_code=validated_data['apply_code'])
                ii.status = 0
                ii.save()
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                raise serializers.ValidationError('成果基本信息表更新失败')

            # 创建历史记录表
            try:
                history = ResultCheckHistory.objects.create(validated_data)
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                raise serializers.ValidationError('历史记录创建失败')

            transaction.savepoint_commit(save_id)

            # 发送短信
            try:
                ownerp = ResultOwnerpBaseinfo.objects.get(pcod=validated_data['apply_code'])
                tel = ownerp.owner_mobile
            except Exception as e:
                raise serializers.ValidationError('发送短信失败')
            else:
                url = 'http://120.77.58.203/sms/patclubmanage/send/verify/0/' + tel
                body = {'type': '未通过', 'name': ii.r_name, 'reason':history.opinion}
                response = requests.post(url, data=json.dumps(body))

            # 推送表信息
            try:
                mm = Message.objects.create({
                    'message_title': '成果消息审核通知',
                    'message_content': history.opinion,
                    'account_code': ii.account_code,
                    'state': 0,
                    'send_time': datetime.now(),
                    'read_time': datetime.now(),
                    'sender':self.context['request'].user.user_name,
                    'sms': '',
                    'sms_state': '',
                    'sms_phone': '',
                    'email': '',
                    'email_state': '',
                    'email_account': ''

                })

            except Exception as e:
                raise serializers.ValidationError('推送表生成失败')

            return history

