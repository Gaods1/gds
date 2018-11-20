from rest_framework import serializers
from django.db import transaction
import requests
import json

from .models import *



# 成果合作信息序列化
class ResultsCooperationInfoSerializer(serializers.ModelSerializer):
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    class Meta:
        model = ResultsCooperationTypeInfo
        fields = ['serial',
                  'r_type',
                  'rr_code',
                  'cooperation_code',
                  'cooperation_name',
                  'state',
                  'insert_time',
                  'update_time',
                  ]


# 成果持有人信息序列化
class ResultsOwnerInfoSerializer(serializers.ModelSerializer):
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    class Meta:
        model = ResultsOwnerInfo
        fields = ['serial',
                  'r_code',
                  'owner_type',
                  'owner_code',
                  'main_owner',
                  'state',
                  'r_type',
                  'insert_time',
                  'update_time',
                  ]


# 成果/需求的检索关键字序列化
class KeywordsInfoSerializer(serializers.ModelSerializer):
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    class Meta:
        model = KeywordsInfo
        fields = ['serial',
                  'key_type',
                  'object_code',
                  'key_info',
                  'state',
                  'insert_time',
                  'creater',
                  'update_time',
                  ]

# 成果信息表序列化
class ResultsInfoSerializer(serializers.ModelSerializer):
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    Cooperation = ResultsCooperationInfoSerializer(many=True)
    Owner = ResultsOwnerInfoSerializer(many=True)
    Keywords = KeywordsInfoSerializer(many=True)
    mcode = serializers.CharField(max_length=16,read_only=True)
    class Meta:
        model = ResultsInfo
        fields = ['serial',
                  'r_code',
                  'r_name',
                  'r_form_type',
                  'r_abstract',
                  'use_type',
                  'obtain_type',
                  'osource_name',
                  'obtain_source',
                  'entry_type',
                  'owner_type',
                  'owner_abstract',
                  'r_coop_t_abstract',
                  'expiry_dateb',
                  'expiry_datee',
                  'rexpiry_dateb',
                  'rexpiry_datee',
                  'original_data',
                  'show_state',
                  'sniff_state',
                  'sniff_time',
                  'creater',
                  'insert_time',
                  'account_code',
                  'r_abstract_detail',
                  #'check_state',
                  'update_time',
                  'Cooperation',
                  'Owner',
                  'Keywords',
                  'mcode',
                  ]

#成果审核历史记录表
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

            try:
                ea = ResultsEaInfo.objects.get(r_code=validated_data['apply_code'])
                ea.status = 11
                ea.save()
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                raise serializers.ValidationError('成果评价信息表更新失败')

            try:
                rr = RrApplyHistory.objects.get(rr_code=validated_data['apply_code'])
                rr.status = 11
                rr.save()
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                raise serializers.ValidationError('成果申请表更新失败')

            try:
                ii = ResultsInfo.objects.get(r_code=validated_data['apply_code'])
                ii.status = 1
                ii.save()
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                raise serializers.ValidationError('成果基本信息表更新失败')

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
                return False
            else:
                url = 'http://120.77.58.203/sms/patclubmanage/send/verify/1/'+tel+'/'
                body = {'type': '通过', 'name': ii.r_name}
                response = requests.post(url, data=json.dumps(body))

            # 推送表信息
            try:
                mm = Message.objects.create({
                    'serial':'成果消息审核通知',
                    'message_title':'成果消息审核通知',
                    'message_content':'',
                    'account_code':'',
                    'state':0,
                    'send_time':'',
                    'read_time':'',
                    'sender':'',
                    
                })

            except Exception as e:
                return False


            return history