import requests
import json
def massege(url,body,headers):
    response = requests.post(url, data=body,headers=headers)

def diedai(raw_list):
    for x in raw_list:
        yield x

    def create(self, request, *args, **kwargs):
        # 建立事物机制
        with transaction.atomic():
            # 创建一个保存点
            save_id = transaction.savepoint()
            try:
                data = request.data
                single_dict = request.data.pop('single', None)
                attachment_list = request.data.pop('attachment', None)
                mcode_list = request.data.pop('mcode',None)

                if not mcode_list:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('请完善相关信息')

                if not single_dict or not attachment_list:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('请先上传相关文件')

                if len(single_dict) != 1:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('封面只能上传一张')

                # 1 创建需求
                data['creater'] = request.user.account
                serializer = self.get_serializer(data=data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)

                serializer_ecode = serializer.data['r_code']

                # 2 创建所属领域
                major_list = []
                for mcode in mcode_list:
                    major_list.append(MajorUserinfo(mcode=mcode,user_type=4,user_code=serializer_ecode,mtype=2))
                MajorUserinfo.objects.bulk_create(major_list)

                # 3 转移附件创建ecode表
                absolute_path = ParamInfo.objects.get(param_code=1).param_value
                relative_path = ParamInfo.objects.get(param_code=2).param_value
                relative_path_front = ParamInfo.objects.get(param_code=4).param_value
                tcode_attachment = AttachmentFileType.objects.get(tname='attachment').tcode
                tcode_coverImg = AttachmentFileType.objects.get(tname='coverImg').tcode
                param_value = ParamInfo.objects.get(param_code=6).param_value

                url_x_a = '{}{}/{}/{}'.format(relative_path, param_value, tcode_attachment, serializer_ecode)
                url_x_c = '{}{}/{}/{}'.format(relative_path, param_value, tcode_coverImg, serializer_ecode)

                if not os.path.exists(url_x_a):
                    os.makedirs(url_x_a)
                if not os.path.exists(url_x_c):
                    os.makedirs(url_x_a)

                dict = {}
                list1 = []
                list2 = []

                # 封面
                for key, value in single_dict.items():

                    if key != 'coverImg':
                        transaction.savepoint_rollback(save_id)
                        return HttpResponse('封面代名不正确')

                    url_l = value.split('/')
                    url_file = url_l[-1]

                    url_j = settings.MEDIA_ROOT + url_file
                    if not os.path.exists(url_j):
                        transaction.savepoint_rollback(save_id)
                        return HttpResponse('该临时路径下不存在该文件,可能文件名错误')

                    url_x = '{}{}/{}/{}/{}'.format(relative_path,param_value,single_dict, serializer_ecode, url_file)
                    # 拼接给前端的的地址
                    url_x_f = url_x.replace(relative_path,relative_path_front)
                    list2.append(url_x_f)

                    # 拼接ecode表中的path
                    path = '{}/{}/{}/'.format(param_value,single_dict,serializer_ecode)
                    list1.append(AttachmentFileinfo(tcode=single_dict,ecode=serializer_ecode,file_name=url_file,path=path,operation_state=3,state=1))

                    # 将临时目录转移到正式目录
                    shutil.move(url_j, url_x)

                for attachment in attachment_list:
                    url_l = attachment.split('/')
                    url_file = url_l[-1]

                    url_j = settings.MEDIA_ROOT + url_file
                    if not os.path.exists(url_j):
                        transaction.savepoint_rollback(save_id)
                        return HttpResponse('该临时路径下不存在该文件,可能文件名错误')

                    url_x = '{}{}/{}/{}/{}'.format(relative_path,param_value,tcode_attachment, serializer_ecode, url_file)

                    url_x_f = url_x.replace(relative_path, relative_path_front)
                    list2.append(url_x_f)

                    path = '{}/{}/{}/'.format(param_value, tcode_attachment, serializer_ecode)
                    list1.append(
                        AttachmentFileinfo(tcode=tcode_attachment, ecode=serializer_ecode, file_name=url_file, path=path,
                                           operation_state=3, state=1))
                    # 将临时目录转移到正式目录
                    shutil.move(url_j, url_x)

                # 创建atachmentinfo表
                AttachmentFileinfo.objects.bulk_create(list1)

                # 删除临时目录
                shutil.rmtree(settings.MEDIA_ROOT,ignore_errors=True)

                # 给前端抛正式目录
                dict['url'] = list2

                headers = self.get_success_headers(serializer.data)
                #return Response(serializer.data,status=status.HTTP_201_CREATED,headers=headers)
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                return HttpResponse('创建失败%s' % str(e))
            transaction.savepoint_commit(save_id)
            return Response(dict)
