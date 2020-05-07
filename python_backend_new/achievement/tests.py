"""
 try:
                    # 判断是个人还是企业
                    if owner.owner_type != 2:
                        ownerp = PersonalInfo.objects.get(pcode=owner.owner_code)

                        tel = ownerp.pmobile
                        url = 'http://120.77.58.203:8808/sms/patclubmanage/send/verify/1/' + tel
                        body = {'type': '成果', 'name': Results.r_name}
                        headers = {
                            "Content-Type": "application/x-www-form-urlencoded",
                            "Accept": "application/json"
                        }

                        # 判断是否采集员：1是采集员 2是持有人
                        if ownerp.state in [1,2]:
                            ownerp.state = 2
                            ownerp.save()
                            # 多线程发送短信
                            t1 = threading.Thread(target=massege, args=(url, body, headers))
                            t1.start()
                        else:
                            transaction.savepoint_rollback(save_id)
                            return Response({"detail": {"detail": ['请先通过成果持有人(个人)审核']}}, status=400)

                    else:
                        ownere = EnterpriseBaseinfo.objects.get(ecode=owner.owner_code)

                        tel = ownere.emobile
                        url = 'http://120.77.58.203:8808/sms/patclubmanage/send/verify/1/' + tel
                        body = {'type': '成果', 'name': Results.r_name}
                        headers = {
                            "Content-Type": "application/x-www-form-urlencoded",
                            "Accept": "application/json"
                        }

                        if ownere.state in [1,2]:
                            ownere.state = 2
                            ownere.save()
                            # 多线程发送短信
                            t1 = threading.Thread(target=massege, args=(url, body, headers))
                            t1.start()
                        else:
                            transaction.savepoint_rollback(save_id)
                            return Response({"detail": {"detail": ['请先通过成果持有人(企业)审核']}}, status=400)

                    # 附件与封面
                    move_attachment('attachment', instance.rr_code)
                    move_single('coverImg', instance.rr_code)

                    # 创建推送表
                    mm = Message.objects.create(**{
                        'message_title': '成果消息审核通知',
                        'message_content': history.opinion,
                        'account_code': owner.owner_code,
                        'state': 0,
                        'send_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                        'sender': request.user.account,
                        'sms': 1,
                        'sms_state': 1,
                        'sms_phone': tel,
                        'email': 1,
                        'email_state': 1,
                        'email_account': ''

                    })

                    partial = kwargs.pop('partial', False)
                    serializer = self.get_serializer(instance, data=data, partial=partial)
                    serializer.is_valid(raise_exception=True)
                    self.perform_update(serializer)

                    if getattr(instance, '_prefetched_objects_cache', None):
                        # If 'prefetch_related' has been applied to a queryset, we need to
                        # forcibly invalidate the prefetch cache on the instance.
                        instance._prefetched_objects_cache = {}
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": {"detail": ['申请表更新失败%s' % str(e)]}}, status=400)

                transaction.savepoint_commit(save_id)
                return Response({'message':'审核通过'})
"""

"""
                    try:
                    dict_z = {}
                    if owner.owner_type != 2:
                        ownerp = PersonalInfo.objects.get(pcode=owner.owner_code)

                        tel = ownerp.pmobile
                        url = 'http://120.77.58.203:8808/sms/patclubmanage/send/verify/0/' + tel
                        body = {'type': '成果', 'name': Results.r_name}
                        headers = {
                            "Content-Type": "application/x-www-form-urlencoded",
                            "Accept": "application/json"
                        }

                        if ownerp.state in [1,2]:
                            if ownerp.state == 1:
                                ownerp.state = 3
                                ownerp.save()
                            # 多线程发送短信
                            t1 = threading.Thread(target=massege, args=(url, body, headers))
                            t1.start()
                        else:
                            transaction.savepoint_rollback(save_id)
                            return Response({"detail": {"detail": ['请先通过成果持有人(个人)审核']}}, status=400)


                    else:
                        # 更新企业信息并发送短信
                        ownere = EnterpriseBaseinfo.objects.get(ecode=owner.owner_code)

                        tel = ownere.emobile
                        url = 'http://120.77.58.203:8808/sms/patclubmanage/send/verify/0/' + tel
                        body = {'type': '成果', 'name': Results.r_name}
                        headers = {
                            "Content-Type": "application/x-www-form-urlencoded",
                            "Accept": "application/json"
                        }

                        if ownere.state in [1,2]:
                            if ownere.state == 1:
                                ownere.state = 3
                                ownere.save()
                            # 多线程发送短信
                            t1 = threading.Thread(target=massege, args=(url, body, headers))
                            t1.start()
                        else:
                            transaction.savepoint_rollback(save_id)
                            return Response({"detail": {"detail": ['请先通过成果持有人(企业)审核']}}, status=400)

                    # 创建推送表
                    mm = Message.objects.create(**{
                        'message_title': '成果消息审核通知',
                        'message_content': history.opinion,
                        'account_code': owner.owner_code,
                        'state': 0,
                        'send_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                        'sender': request.user.account,
                        'sms': 1,
                        'sms_state': 1,
                        'sms_phone': tel,
                        'email': 1,
                        'email_state': 1,
                        'email_account': ''

                    })

                    partial = kwargs.pop('partial', False)
                    serializer = self.get_serializer(instance, data=data, partial=partial)
                    serializer.is_valid(raise_exception=True)
                    self.perform_update(serializer)

                    if getattr(instance, '_prefetched_objects_cache', None):
                        # If 'prefetch_related' has been applied to a queryset, we need to
                        # forcibly invalidate the prefetch cache on the instance.
                        instance._prefetched_objects_cache = {}
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": {"detail": ['申请表更新失败%s' % str(e)]}}, status=400)

                transaction.savepoint_commit(save_id)
                return Response({'message':'审核不通过'})
"""

"""
                    try:
                    dict_z = {}
                    # 如果是个人或者团队
                    if owner.owner_type != 2:
                        ownerp = PersonalInfo.objects.get(pcode=owner.owner_code)

                        tel = ownerp.pmobile
                        url = 'http://120.77.58.203:8808/sms/patclubmanage/send/verify/1/' + tel
                        body = {'type': '需求', 'name': Requirements.req_name}
                        headers = {
                            "Content-Type": "application/x-www-form-urlencoded",
                            "Accept": "application/json"
                        }

                        # 如果申请人审核通过
                        if ownerp.state in [1,2]:
                            ownerp.state = 2
                            ownerp.save()
                            # 多线程发送短信
                            t1 = threading.Thread(target=massege, args=(url, body, headers))
                            t1.start()
                        else:
                            transaction.savepoint_rollback(save_id)
                            return Response({"detail": {"detail": ['请先通过需求持有人(个人)审核']}}, status=400)


                    else:
                        # 企业送短信
                        ownere = EnterpriseBaseinfo.objects.get(ecode=owner.owner_code)

                        tel = ownere.emobile
                        url = 'http://120.77.58.203:8808/sms/patclubmanage/send/verify/1/' + tel
                        body = {'type': '需求', 'name': Requirements.req_name}
                        headers = {
                            "Content-Type": "application/x-www-form-urlencoded",
                            "Accept": "application/json"
                        }

                        if ownere.state in [1, 2]:
                            ownere.state = 2
                            ownere.save()
                            # 多线程发送短信
                            t1 = threading.Thread(target=massege, args=(url, body, headers))
                            t1.start()
                        else:
                            transaction.savepoint_rollback(save_id)
                            return Response({"detail": {"detail": ['请先通过需求持有人(企业)审核']}}, status=400)

                    # 返回相对路径
                    dict_attachment = move_attachment('attachment', instance.rr_code)
                    dict_single = move_single('coverImg', instance.rr_code)

                    dict_z['Attach'] = dict_attachment
                    dict_z['Cover'] = dict_single

                    # 创建推送表
                    mm = Message.objects.create(**{
                        'message_title': '需求消息审核通知',
                        'message_content': history.opinion,
                        'account_code': owner.owner_code,
                        'state': 0,
                        'send_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                        'sender': request.user.account,
                        'sms': 1,
                        'sms_state': 1,
                        'sms_phone': tel,
                        'email': 1,
                        'email_state': 1,
                        'email_account': ''

                    })

                    partial = kwargs.pop('partial', False)
                    serializer = self.get_serializer(instance, data=data, partial=partial)
                    serializer.is_valid(raise_exception=True)
                    self.perform_update(serializer)

                    if getattr(instance, '_prefetched_objects_cache', None):
                        # If 'prefetch_related' has been applied to a queryset, we need to
                        # forcibly invalidate the prefetch cache on the instance.
                        instance._prefetched_objects_cache = {}
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": {"detail": ['申请表更新失败%s' % str(e)]}}, status=400)

                transaction.savepoint_commit(save_id)
                return Response({'message':'审核通过'})
"""

"""
                try:
                    if owner.owner_type != 2:
                        ownerp = PersonalInfo.objects.get(pcode=owner.owner_code)

                        tel = ownerp.pmobile
                        url = 'http://120.77.58.203:8808/sms/patclubmanage/send/verify/0/' + tel
                        body = {'type': '需求', 'name': Requirements.req_name}
                        headers = {
                            "Content-Type": "application/x-www-form-urlencoded",
                            "Accept": "application/json"
                        }

                        if ownerp.state in [1,2]:
                            if ownerp.state == 1:
                                ownerp.state = 3
                                ownerp.save()
                                # 多线程发送短信
                                t1 = threading.Thread(target=massege, args=(url, body, headers))
                                t1.start()
                        else:
                            transaction.savepoint_rollback(save_id)
                            return Response({"detail": {"detail": ['请先通过需求持有人(个人)审核']}}, status=400)


                    else:
                        # 更新企业信息并发送短信
                        ownere = EnterpriseBaseinfo.objects.get(ecode=owner.owner_code)

                        tel = ownere.emobile
                        url = 'http://120.77.58.203:8808/sms/patclubmanage/send/verify/0/' + tel
                        body = {'type': '成果', 'name': Requirements.req_name}
                        headers = {
                            "Content-Type": "application/x-www-form-urlencoded",
                            "Accept": "application/json"
                        }

                        if ownere.state in [1,2]:
                            if ownere.state == 1:
                                ownere.state = 3
                                ownere.save()
                                # 多线程发送短信
                                t1 = threading.Thread(target=massege, args=(url, body, headers))
                                t1.start()
                        else:
                            transaction.savepoint_rollback(save_id)
                            return HttpResponse('请先通过需求持有人(企业)审核')

                    # 创建推送表
                    mm = Message.objects.create(**{
                        'message_title': '需求消息审核通知',
                        'message_content': history.opinion,
                        'account_code': owner.owner_code,
                        'state': 0,
                        'send_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                        'sender': request.user.account,
                        'sms': 1,
                        'sms_state': 1,
                        'sms_phone': tel,
                        'email': 1,
                        'email_state': 1,
                        'email_account': ''

                    })

                    partial = kwargs.pop('partial', False)
                    serializer = self.get_serializer(instance, data=data, partial=partial)
                    serializer.is_valid(raise_exception=True)
                    self.perform_update(serializer)

                    if getattr(instance, '_prefetched_objects_cache', None):
                        # If 'prefetch_related' has been applied to a queryset, we need to
                        # forcibly invalidate the prefetch cache on the instance.
                        instance._prefetched_objects_cache = {}
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": {"detail": ['申请表更新失败%s' % str(e)]}}, status=400)

                transaction.savepoint_commit(save_id)
                return Response({'messege':'审核不通过'})

"""




"""

实现关联表的模糊搜索
    def list(self, request, *args, **kwargs):
        search = request.query_params.get('search', None)
        if search:
            rq = ResultsInfo.objects.values_list('r_code').filter(r_code__in=self.get_queryset().values_list('rr_code'),
                                                                  r_name__icontains=search)
            kq = KeywordsInfo.objects.values_list('object_code').filter(object_code__in=self.get_queryset().values_list('rr_code'),
                                                                        key_info__icontains=search)
            queryset = self.get_queryset().filter(Q(rr_code__in=rq) | Q(rr_code__in=kq))
        else:
            queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
"""




"""
# 1 创建需求
                obtain_type = request.data['obtain_type']
                owner_type = request.data['owner_type']

                # 如果是采集员
                if obtain_type == 1:
                    # 个人或者团队
                    if owner_type in [1, 3]:
                        #personalinfo表
                        pid = request.data.pop('pid', None)
                        pname = request.data.pop('pname', None)
                        psex = request.data.pop('psex', None)
                        pid_type = request.data.pop('pid_type', None)
                        pmobile = request.data.pop('pmobile', None)
                        ptel = request.data.pop('ptel', None)
                        pemail = request.data.pop('pemail', None)
                        peducation = request.data.pop('peducation', None)
                        pabstract = request.data.pop('pabstract', None)
                        account_code = request.data.pop('account_code', None)

                        #成果/需求合作方式信息表
                        r_type = request.data.pop('r_type', None)
                        cooperation_code = request.data.pop('cooperation_code', None)
                        cooperation_name = request.data.pop('cooperation_name', None)

                        #成果持有人信息表
                        main_owner = request.data.pop('main_owner', None)

                        #关键字表
                        key_info = request.data.pop('key_info', None)

                        pcode_list = PersonalInfo.objects.filter(pid=pid)

                        #判断是否存在personalinfo表
                        if pcode_list:
                            pcode = pcode_list[0]

                            #创建resultsinfo表
                            data['creater'] = request.user.account
                            serializer = self.get_serializer(data=data)
                            serializer.is_valid(raise_exception=True)
                            self.perform_create(serializer)

                            serializer_ecode = serializer.data['r_code']

                            #创建合作方式表
                            ResultsCooperationTypeInfo.objects.create(r_type=r_type,
                            rr_code=serializer_ecode,cooperation_code=cooperation_code,
                            cooperation_name=cooperation_name,state=1)

                            #创建持有人信息表
                            ResultsOwnerInfo.objects.create(r_code=serializer_ecode,
                            owner_type=owner_type,owner_code=pcode,main_owner=main_owner,
                            state=1,r_type=r_type)

                            #创建关键字表
                            KeywordsInfo.objects.create(key_type=r_type,object_code=serializer_ecode,
                            key_info=key_info,state=1,creater=request.user.account)

                        else:
                            #创建personalinfo表
                            pcode_element = PersonalInfo.objects.create(pid=pid,pname=pname,psex=psex,
                            pid_type=pid_type,pmobile=pmobile,ptel=ptel,pemail=pemail,
                            peducation=peducation,pabstract=pabstract,state=2,creater
                            =request.user.account,account_code=account_code)
                            pcode = pcode_element.pcode

                            #创建resultsinfo表
                            data['creater'] = request.user.account
                            serializer = self.get_serializer(data=data)
                            serializer.is_valid(raise_exception=True)
                            self.perform_create(serializer)

                            serializer_ecode = serializer.data['r_code']

                            # 创建合作方式表
                            ResultsCooperationTypeInfo.objects.create(r_type=r_type,
                            rr_code=serializer_ecode,
                            cooperation_code=cooperation_code,
                            cooperation_name=cooperation_name, state=1)

                            # 创建持有人信息表
                            ResultsOwnerInfo.objects.create(r_code=serializer_ecode,
                            owner_type=owner_type, owner_code=pcode,
                            main_owner=main_owner,
                            state=1, r_type=r_type)

                            # 创建关键字表
                            KeywordsInfo.objects.create(key_type=r_type, object_code=serializer_ecode,
                            key_info=key_info, state=1, creater=request.user.account)

                    # 企业的情况
                    else:
                        manager_id = request.data.pop('manager_id', None)

                        # 判断是否存在enterpriseinfo表
                        ecode_list = EnterpriseBaseinfo.objects.filter(manager_id=manager_id)
                        if ecode_list:
                            ecode = ecode_list[0]

                            #创建resultsinfo表
                            data['creater'] = request.user.account
                            serializer = self.get_serializer(data=data)
                            serializer.is_valid(raise_exception=True)
                            self.perform_create(serializer)

                            serializer_ecode = serializer.data['r_code']

                        else:

                            EnterpriseBaseinfo.objects.create()

                            #创建resultsinfo表
                            data['creater'] = request.user.account
                            serializer = self.get_serializer(data=data)
                            serializer.is_valid(raise_exception=True)
                            self.perform_create(serializer)

                            serializer_ecode = serializer.data['r_code']

                else:
                    # 个人或者团队
                    if owner_type in [1, 3]:
                        # personalinfo表
                        pid = request.data.pop('pid', None)
                        pname = request.data.pop('pname', None)
                        psex = request.data.pop('psex', None)
                        pid_type = request.data.pop('pid_type', None)
                        pmobile = request.data.pop('pmobile', None)
                        ptel = request.data.pop('ptel', None)
                        pemail = request.data.pop('pemail', None)
                        peducation = request.data.pop('peducation', None)
                        pabstract = request.data.pop('pabstract', None)
                        account_code = request.data.pop('account_code', None)

                        # 成果/需求合作方式信息表
                        r_type = request.data.pop('r_type', None)
                        cooperation_code = request.data.pop('cooperation_code', None)
                        cooperation_name = request.data.pop('cooperation_name', None)

                        # 成果持有人信息表
                        main_owner = request.data.pop('main_owner', None)

                        # 关键字表
                        key_info = request.data.pop('key_info', None)

                        pcode = PersonalInfo.objects.get(pid=pid).pcode

                        # 创建resultsinfo表
                        data['creater'] = request.user.account
                        serializer = self.get_serializer(data=data)
                        serializer.is_valid(raise_exception=True)
                        self.perform_create(serializer)

                        serializer_ecode = serializer.data['r_code']

                        # 创建合作方式表
                        ResultsCooperationTypeInfo.objects.create(r_type=r_type,
                        rr_code=serializer_ecode,
                        cooperation_code=cooperation_code,
                        cooperation_name=cooperation_name, state=1)

                        # 创建持有人信息表
                        ResultsOwnerInfo.objects.create(r_code=serializer_ecode,
                        owner_type=owner_type, owner_code=pcode, main_owner=main_owner,
                        state=1, r_type=r_type)

                        # 创建关键字表
                        KeywordsInfo.objects.create(key_type=r_type, object_code=serializer_ecode,
                        key_info=key_info, state=1, creater=request.user.account)


                    # 企业的情况
                    else:
                        manager_id = request.data.pop('manager_id', None)
                        ecode = EnterpriseBaseinfo.objects.get(manager_id=manager_id).ecode

                        # 创建resultsinfo表
                        data['creater'] = request.user.account
                        serializer = self.get_serializer(data=data)
                        serializer.is_valid(raise_exception=True)
                        self.perform_create(serializer)

                        serializer_ecode = serializer.data['r_code']

                        /alidata1/patclub/uploads/Results/0110/L1AYcahuGrN2KWpgLka4Qwgjbq4iojFP


"""
"""
逻辑删除：
            try:
                instance = self.get_object()
                serializer_ecode = instance.r_code

                #1 删除resultsinfo表
                self.perform_destroy(instance)
                # 2 删除合作方式表
                ResultsCooperationTypeInfo.objects.filter(rr_code=serializer_ecode).delete()
                # 3 删除成果持有人表
                ResultsOwnerInfo.objects.filter(r_code=serializer_ecode).delete()
                # 4 删关键字表
                KeywordsInfo.objects.filter(object_code=serializer_ecode).delete()
                # 5 删除所属领域表记录
                MajorUserinfo.objects.filter(user_code=serializer_ecode).delete()
                # 6 删除文件以及ecode表记录
                relative_path = ParamInfo.objects.get(param_code=2).param_value
                tcode_attachment = AttachmentFileType.objects.get(tname='attachment').tcode
                tcode_coverImg = AttachmentFileType.objects.get(tname='coverImg').tcode
                param_value = ParamInfo.objects.get(param_code=6).param_value
                obj = AttachmentFileinfo.objects.filter(ecode=serializer_ecode)
                if obj:
                    try:
                        for i in obj:
                            url = settings.MEDIA_ROOT
                            url = url + 'uploads/'
                            url = '{}{}{}'.format(url, i.path, i.file_name)
                            # 创建对象
                            a = FileSystemStorage()
                            # 删除文件
                            a.delete(url)
                            # 删除表记录
                            i.delete()
                        url_att = '{}{}/{}/{}'.format(relative_path, param_value, tcode_attachment, serializer_ecode)
                        if os.path.exists(url_att):
                            shutil.rmtree(url_att,ignore_errors=True)
                        url_cov = '{}{}/{}/{}'.format(relative_path, param_value, tcode_coverImg, serializer_ecode)
                        if os.path.exists(url_cov):
                            shutil.rmtree(url_cov,ignore_errors=True)
                    except Exception as e:
                        transaction.savepoint_rollback(save_id)
                        return Response({'detail': '删除失败%s' % str(e)}, status=400)

            except Exception as e:
                transaction.savepoint_rollback(save_id)
                return Response({'detail': '删除失败%s' % str(e)}, status=400)
            transaction.savepoint_commit(save_id)
            return Response({'message':'ok'})

"""

"""


# 富文本编辑内容
    element = ResultsInfo.objects.get(r_code=serializer_ecode)
    detail = element.r_abstract_detail
    if detail:
        img_pattern = re.compile(r'src=\"(.*?)\"')
        editor_imgs_list = img_pattern.findall(detail)
        if editor_imgs_list:
            for i in editor_imgs_list:
                editor_temppath = i.replace(absolute_path_front, absolute_path)
                if not os.path.exists(editor_temppath):
                    transaction.savepoint_rollback(save_id)
                    return Response({'detail': '富文本图片' + i + '不存在'}, 400)
                url_file_editor = i.split('/')[-1]

                editor_zhengshi = '{}{}/{}/{}'.format(relative_path, param_value, tcode_editor,
                                                      serializer_ecode)
                if not os.path.exists(editor_zhengshi):
                    os.makedirs(editor_zhengshi)
                editor_zhengshi_file = '{}/{}'.format(editor_zhengshi,url_file_editor)

                #shutil.move(editor_temppath, editor_zhengshi_file)
                dict_items[editor_temppath]=editor_zhengshi_file

                editor_zhengshi_f = editor_zhengshi_file.replace(relative_path, relative_path_front)
                detail = detail.replace(i, editor_zhengshi_f)

                element.r_abstract_detail = detail
                element.save()
"""