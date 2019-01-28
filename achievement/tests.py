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
