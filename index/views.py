from rest_framework import  permissions
from misc.permissions.permissions import  *
from django.http import JsonResponse
from rest_framework.views import APIView
from expert.models import *
from achievement.models import *
from consult.models import *
import requests,json,math,csv,time,random,os,csv
from bs4 import BeautifulSoup
from index.models import *
from achievement.models import *
from django.db import transaction
from misc.misc import gen_uuid16

class Index(APIView):
    permission_classes = (permissions.IsAuthenticated, ReadOnlyPermission)

    def get(self,request):
        broker_apply_count = BrokerApplyHistory.objects.filter(state=1).count()
        expert_apply_count = ExpertApplyHistory.objects.filter(state=1).count()
        team_apply_count = TeamApplyHistory.objects.filter(state=1).count()
        collector_apply_count = CollectorApplyHistory.objects.filter(state=1).count()
        result_ownerp_apply_count = OwnerApplyHistory.objects.filter(state=1,owner_code__in=ResultOwnerpBaseinfo.objects.values_list('owner_code').filter(type=1)).count()
        result_ownere_apply_count = OwnereApplyHistory.objects.filter(state=1,owner_code__in=ResultOwnereBaseinfo.objects.values_list('owner_code').filter(type=1)).count()
        requirement_ownerp_apply = OwnerApplyHistory.objects.filter(state=1,owner_code__in=ResultOwnerpBaseinfo.objects.values_list('owner_code').filter(type=2)).count()
        requirement_ownere_apply = OwnereApplyHistory.objects.filter(state=1,owner_code__in=ResultOwnereBaseinfo.objects.values_list('owner_code').filter(type=2)).count()
        result_apply_count = RrApplyHistory.objects.filter(type=1,state=1).count()
        requirement_apply_count = RrApplyHistory.objects.filter(type=2,state=1).count()
        consult_apply_count = ConsultInfo.objects.filter(consult_state=0).count()
        consult_reply_count = ConsultReplyInfo.objects.filter(reply_state=1).count()

        return JsonResponse({
            'account_memo':request.user.account_memo,
            'dept_name':request.user.dept,
            'last_login':request.user.last_login,
            'broker_apply_count':broker_apply_count,
            'expert_apply_count':expert_apply_count,
            'team_apply_count':team_apply_count,
            'collector_apply_count':collector_apply_count,
            'result_ownerp_apply_count':result_ownerp_apply_count,
            'result_ownere_apply_count':result_ownere_apply_count,
            'requirement_ownerp_apply':requirement_ownerp_apply,
            'requirement_ownere_apply':requirement_ownere_apply,
            'result_apply_count':result_apply_count,
            'requirement_apply_count':requirement_apply_count,
            'consult_apply_count':consult_apply_count,
            'consult_reply_count':consult_reply_count
        })



class Result(APIView):
    permission_classes = (permissions.IsAuthenticated, ReadOnlyPermission)

    def get(self,request):
        post_url = 'http://www.nstad.cn/nstas/list';
        data = requests.get(post_url)
        result_info_dict = json.loads(data.text)
        total = result_info_dict['count']

        # proxy = getProxies()
        head = {
            "User_Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
            "Referer": "http://www.xicidaili.com/nn/1"
        }

        proxy = {
            'http': 'http://27.29.44.224:9999',
            'http': 'http://110.52.235.151:9999'
        }

        # head = {
        #     'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
        #     'Connection': 'keep-alive'}

        for num in range(1,math.ceil(total/100)):
            result_data = requests.get("http://www.nstad.cn/nstas/list?pageSize=100&pageNo="+str(num), headers=head, proxies=proxy)
            result_info_list = json.loads(result_data.text)['list']
            result_info_list
            for result in result_info_list:
                result['id']
                detail_data = requests.get("http://www.nstad.cn/nstas/getDetalied?id="+str(result['id']), headers=head, proxies=proxy)
                detail_str = detail_data.text

                pattern = re.compile(r'{\'id(.*?)}]}')
                result1 = "{'id" + "".join(pattern.findall(detail_str)) + "}]}"
                strs = re.sub('\'', '\"', result1)
                strs1 = re.sub("cgcsd:",'"cgcsd":',strs)
                strs2 = re.sub("cgcsdqt",'"cgcsdqt"',strs1)
                strs3 = re.sub("cgabs",'"cgabs"',strs2)
                strs4 = re.sub("cgwcdw",'"cgwcdw"',strs3)
                strs5 = re.sub("cgyyqk",'"cgyyqk"',strs4)
                strs6 = re.sub("filename",'"filename"',strs5)
                strs7 = re.sub('""filename""','"filename"',strs6)
                strs8 = re.sub("identfile",'"identfile"',strs7)
                try:
                    result2 = json.loads(strs8)
                    if result2:
                        if result2['cgname']:
                            result_obj = ResultsInfo()
                            result_obj.r_code = gen_uuid32()
                            result_obj.r_name = result2['cgname']
                            result_obj.r_form_type = 1
                            result_obj.r_abstract = result2['cgabs']
                            result_obj.use_type = 1
                            result_obj.obtain_type = 1
                            result_obj.osource_name = result2['cgdywcdw']
                            result_obj.entry_type = 3
                            result_obj.owner_type = 2
                            result_obj.owner_abstract = result2['department']['deptname']
                            result_obj.show_state = 2
                            result_obj.r_abstract_detail = result2['cgabs']
                            result_obj.save()
                        # csvfile = open('/home/tonbochow/python/result.csv', 'wb')
                        # writer = csv.writer(csvfile)
                        # data =[
                        #     (
                        #         result2['cgname'],
                        #         result2['cgdywcdw'],
                        #         result2['cgtxxs'],
                        #         result2['cgcsd'],
                        #         result2['cgabs'],
                        #         result2['cgkey'],
                        #         result2['cgly'],
                        #         result2['department']['deptname'],
                        #         result2['department']['address'],
                        #         result2['department']['zipcode'],
                        #         result2['department']['lianxiren'],
                        #         result2['department']['mobilephone'],
                        #         result2['department']['telephone'],
                        #         result2['attornFinancing']['rzxuqiuje'],
                        #     )
                        # ]
                        # writer.writerows(data)
                        # csvfile.close()
                except Exception as e:
                    cgname_pattern = re.compile(r'cgname":(.*?)",')
                    r_name = "".join(cgname_pattern.findall(strs8))
                    cgabs_pattern = re.compile(r'cgabs":(.*?)",')
                    r_abstract = "".join(cgabs_pattern.findall(strs8))
                    cgdywcdw_pattern = re.compile(r'cgdywcdw":(.*?)",')
                    osource_name = "".join(cgdywcdw_pattern.findall(strs8))
                    deptname_pattern = re.compile(r'deptname":(.*?)",')
                    owner_abstract = "".join(deptname_pattern.findall(strs8))


                    if r_name:
                        result_obj = ResultsInfo()
                        result_obj.r_code = gen_uuid32()
                        result_obj.r_name = r_name
                        result_obj.r_form_type = 1
                        result_obj.r_abstract = r_abstract
                        result_obj.use_type = 1
                        result_obj.obtain_type = 1
                        result_obj.osource_name = osource_name
                        result_obj.entry_type = 3
                        result_obj.owner_type = 2
                        result_obj.owner_abstract = owner_abstract
                        result_obj.show_state = 2
                        result_obj.r_abstract_detail =  r_abstract
                        result_obj.save()

                    time.sleep(5)
                    continue



        return JsonResponse({
            'data':result_info_dict,
            'total':result_info_dict['count']
        })



class One(APIView):        #采集网址: http://www.nstad.cn      http://www.nstad.cn/nstas/list?pageNo=1&pageSize=1   http://www.nstad.cn/nstas/getDetalied?id=20161803
    # permission_classes = (permissions.IsAuthenticated, ReadOnlyPermission)
    permission_classes = (permissions.AllowAny, ReadOnlyPermission)

    def get(self,request):
        # post_url = 'http://www.nstad.cn/nstas/list';
        # data = requests.get(post_url)
        # result_info_dict = json.loads(data.text)
        # total = result_info_dict['count']
        total = 26137   #固定写死减少请求次数

        # head = {
        #     "User_Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",          #代理ip作用不大 先禁用
        #     "Referer": "http://www.xicidaili.com/nn/1"
        # }
        #
        # proxy = {
        #     'http': 'http://182.44.220.196:9999',
        #     'http': 'http://115.151.5.31:9999'
        # }


        # a = '{"id":"20161805", "cgname":"抗耐药菌多肽 Cbf-14", "cgdywcdw":"中国药科大学", "cgwcr":"周长林", "cgtxxs":"新品种；新产品", "cgtxxsqt":"null", "cggxly":"null", "cgxxcy":"null", "cgsx":"原始创新", "cgcsd":"中试产品", "cgcsdqt":"null", "cgabs":"抗菌肽Cbf-14是基于“源于天然结构的高活性抗菌肽发现和理化性质优化策略”关键技术设计和改造获得的新型阳离子小分子多肽，是针对细菌自身（质膜破坏/耐药基因结合）和宿主防御体系（免疫调控通路）多靶点对抗耐药菌活性和机制进行研发的I类新药品种。Cbf-14是含14个氨基酸的短肽，结构新颖，具有完整的自主知识产权，目前已申请发明专利4项（其中授权专利2项，①抗耐药性细菌感染多肽Cbf-14及其用途, ZL 201310413721.0；②一种具有抗耐药性革兰阳性细菌作用的药物组合物, ZL 201410175怂ĸ 睏എ捘监   ʜ΋എႡ┐               鹀Ʃ  鹀Ʃ   伎琂ཱЀ   ￾￿￾￿伛琂伎琂 ཱ  Ѐ ཱ 鹀Ʃ䍠ᗬ顅睁蒕睁Ｇ琙<琚Љ ઴ሆ ￿￿Ȑᾮ䓈琘Ł琚  ໸ᨿ 沔ሆ Ფ 䕄ᗬᗪ瑉浥    䍠ᗬ୔ 䕄ᗬᗪ潃湵t䑩皪 寄皪㏏ᏸ灞⥓睌  ⥓睌鴘΋      ܐ΋ 笠煰ᾮ", "cgwcdw":"中国药科大学", "cgkey":"抗菌肽;耐药菌，药学研究", "cgyyhangye":"C;C27;C271;C272", "cgyyhangyemc":"null", "deptid":"327", "cgglzd":"中科飞测", "changeflg":"null", "cgcqdw":"null", "cgyyqk":"null", "filename":"null", "identfile":"null", "cgfbdate":"null", "source":"基金", "cghxjs":"null", "cgjsxjx":"null", "cgjsfzx":"null", "cgjjwt":"null", "cgshxy":"null", "searchfile":"null", "cgcqgs":"null", "createtime":"2019-01-19 11:30", "cgcqxs":"null", "cgsfzj":"null", "cgzjje":"null", "cgzcxqd":"null", "cgzcmzd":"null", "cggxjsdm":"null", "cgxxcydm":"null", "cgwcdate":"2019", "imgurl":"null", "operationtime":"null", "cgly":"国家科技计划项目", "attornFinancing":{"id":"4244", "cgzhfs":" 自行转化<br>;技术授权<br>", "cgzhfsqt":"null", "cgzhqzdx":"null", "rzduixiang":"null", "rzduixiangqt":"null", "rzxuqiuje":"3000", "proid":"20161805", "source":"20190119", "ysxzhuanhua":"null", "ysxzhuanhuaqt":"null", "zhshouyi":"null", "chdtouzi":"null", "chdtouziqt":"null", "chdjine":"3000", "projectNav":"com.wanfang.omp.nstas.domain.ProjectNav@4bcd049f"}, "department":{"id":"327","deptname":"中国药科大学","zgbumen":"教育部","orgcode":"466006834","address":"南京市童家巷24号","zipcode":"210009","lianxiren":"孙立冰","mobilephone":"13851559021","telephone":"025-83271487","fax":"025-83271310","email":"jm0067@163.com","orgshuxing":"教育机构","orglocation":"江苏@南京@","orgcode_jpg":"201608240954386760.jpg","source":"奖励系统","orgbeizhu":"null","operationtime":"2016/8/24 10:45:14","province":"江苏","sys_user_id":"1628","morg_user_id":"null"}, "right":[], "prize":[], "research":[{"id":"187753", "resname":"2018ZX09721001-004-005", "rescode":"PLYY002", "resfzr":"null", "reslyjh":"I类新药抗真菌多肽PL-18和抗耐药菌多肽Cbf-14临床前研究", "begindate":"null", "enddate":"null", "resyjxs":"null", "resyjxsqt":"null", "resabs":"null", "resamount":"null", "reszyzj":"null", "deptid":"null", "resjibie":"null", "change_flg":"null", "filename":"null", "homefile":"null", "source":"中科飞测", "createtime":"2019-01-19 11:30", "resbeizhu":"20190119", "operationtime":"null"}]}'
        # cgname_pattern = re.compile(r'cgname":"(.*?)",')
        # r_name = "".join(cgname_pattern.findall(a))



        try:
            f = open("/home/tonbochow/python/result_count.txt","r+")
            pageNum = int(f.read().strip('\n'))
        finally:
            if f:
                f.close()

        # for num in range(1,total):
        if pageNum and (pageNum <= total):
            # result_data = requests.get("http://www.nstad.cn/nstas/list?pageSize=1&pageNo="+str(num), headers=head, proxies=proxy)
            result_data = requests.get("http://www.nstad.cn/nstas/list?pageSize=1&pageNo=" + str(pageNum))
            result_info_list = json.loads(result_data.text)['list']
            for result in result_info_list:
                # detail_data = requests.get("http://www.nstad.cn/nstas/getDetalied?id="+str(result['id']), headers=head, proxies=proxy)
                detail_data = requests.get("http://www.nstad.cn/nstas/getDetalied?id=" + str(result['id']))
                detail_str = detail_data.text

                pattern = re.compile(r'{\'id(.*?)}]}')
                if not pattern.findall(detail_str):   #可能Ip被禁用了  不再爬取保存文件
                    return JsonResponse({
                        'data':'匹配失败',
                        'total':total
                    })

                # 把爬取到的text文本保存到文件
                try:
                    f = open("/home/tonbochow/python/spider/nstad/" + str(result['id']) + ".html", "w+")
                    f.write(detail_str)
                finally:
                    if f:
                        f.close()


                collect_data = "{'id" + "".join(pattern.findall(detail_str)) + "}]}"  # 采集到的详情数据

                nstad_obj = Nstad()              #保存采集到详细成果数据
                exist_nstad = Nstad.objects.filter(result_id=result['id'])
                if exist_nstad:
                    try:
                        f = open("/home/tonbochow/python/result_count.txt", "r+")
                        f.write(str(pageNum+1))
                    finally:
                        if f:
                            f.close()
                    return JsonResponse({
                        'data': '采集文集已存在退出',
                        'total': total
                    })

                nstad_obj.result_id = result['id']
                nstad_obj.content = collect_data
                nstad_obj.save()

                strs = re.sub('\'', '\"', collect_data)  #全部将单引号替换为双引号  下面几个为不规则的json串字段
                strs1 = re.sub("cgcsd:",'"cgcsd":',strs)
                strs2 = re.sub("cgcsdqt",'"cgcsdqt"',strs1)
                strs3 = re.sub("cgabs",'"cgabs"',strs2)
                strs4 = re.sub("cgwcdw",'"cgwcdw"',strs3)
                strs5 = re.sub("cgyyqk",'"cgyyqk"',strs4)
                strs6 = re.sub("filename",'"filename"',strs5)
                strs7 = re.sub('""filename""','"filename"',strs6)
                strs8 = re.sub("identfile",'"identfile"',strs7)

                try:
                    result_dict = json.loads(strs8)     #将json串转为字典  可能会失败 因为数据串不规则
                    if result_dict:
                        r_name = result_dict['cgname']
                        if r_name:
                            #保存成果基本信息
                            result_obj = ResultsInfo()
                            result_obj.r_code = gen_uuid32()
                            result_obj.r_name = result_dict['cgname']
                            result_obj.r_form_type = 1
                            result_obj.r_abstract = result_dict['cgabs']
                            result_obj.use_type = 1
                            result_obj.obtain_type = 1
                            result_obj.osource_name = result_dict['cgdywcdw']
                            result_obj.entry_type = 3
                            result_obj.owner_type = 2
                            result_obj.owner_abstract = result_dict['department']['deptname']+result_dict['department']['lianxiren']+result_dict['department']['mobilephone']+result_dict['department']['telephone']+result_dict['department']['zipcode']+result_dict['department']['address']
                            result_obj.r_coop_t_abstract = result_dict['attornFinancing']['cgzhfs']
                            result_obj.show_state = 2
                            result_obj.r_abstract_detail = result_dict['cgabs']
                            result_obj.save()
                except Exception as e:                    #进入异常说明json穿转字典失败  采用正则匹配采集数据
                    cgname_pattern = re.compile(r'cgname":"(.*?)",')
                    r_name = "".join(cgname_pattern.findall(str(strs8)))

                    ss = re.compile(r'cgname":(.*?)",')
                    r_name = "".join(ss.findall(str(strs8)))

                    cgabs_pattern = re.compile(r'cgabs":"(.*?)",')
                    r_abstract = "".join(cgabs_pattern.findall(strs8))
                    cgdywcdw_pattern = re.compile(r'cgdywcdw":"(.*?)",')
                    osource_name = "".join(cgdywcdw_pattern.findall(strs8))
                    deptname_pattern = re.compile(r'deptname":"(.*?)",')
                    owner_abstract = "".join(deptname_pattern.findall(strs8))
                    lianxiren_pattern = re.compile(r'lianxiren":"(.*?)",')
                    lianxiren = "".join(lianxiren_pattern.findall(strs8))
                    mobilephone_pattern = re.compile(r'mobilephone":"(.*?)",')
                    mobilephone = "".join(mobilephone_pattern.findall(strs8))
                    telephone_pattern =  re.compile(r'telephone_pattern":"(.*?)",')
                    telephone = "".join(telephone_pattern.findall(strs8))
                    zipcode_pattern = re.compile(r'zipcode":"(.*?)",')
                    zipcode = "".join(zipcode_pattern.findall(strs8))
                    address_pattern = re.compile(r'address":"(.*?)",')
                    address = "".join(address_pattern.findall(strs8))
                    cgzhf_pattern = re.compile(r'cgzhfs":"(.*?)",')
                    cgzhf = "".join(cgzhf_pattern.findall(strs8))
                    if r_name:
                        result_obj = ResultsInfo()
                        result_obj.r_code = gen_uuid32()
                        result_obj.r_name = r_name
                        result_obj.r_form_type = 1
                        result_obj.r_abstract = r_abstract
                        result_obj.use_type = 1
                        result_obj.obtain_type = 1
                        result_obj.osource_name = osource_name
                        result_obj.entry_type = 3
                        result_obj.owner_type = 2
                        result_obj.owner_abstract = owner_abstract+lianxiren+mobilephone+telephone+zipcode+address
                        result_obj.r_coop_t_abstract = cgzhf
                        result_obj.show_state = 2
                        result_obj.r_abstract_detail =  r_abstract
                        result_obj.save()

                if r_name:           #采集成果则文本保存的数字自增1
                    try:
                        f = open("/home/tonbochow/python/result_count.txt", "r+")
                        f.write(str(pageNum+1))
                    finally:
                        if f:
                            f.close()

        return JsonResponse({
            'data':r_name,
            'total':total
        })



class Weihengtech(APIView):        #采集网址: http://www.weihengtech.com/index.php?s=/Home/Invention/lists
    permission_classes = (permissions.AllowAny, ReadOnlyPermission)

    def get(self, request):
        post_url = "http://www.weihengtech.com/index.php?s=/Home/Invention/shushangRequest/key/patentQuery.html"
        # unix_timestamp = int(time.time())
        unix_timestamp = int(round(time.time() * 1000))
        try:
            f = open("/home/tonbochow/python/spider/weihengtech_count.txt","r+")
            page_num = int(f.read().strip('\n'))
        finally:
            if f:
                f.close()
        queryData = {"page_size": 100, "page_num": page_num}

                     # "ids": "CN00100445.X,CN02113654.8,CN03128399.3,CN200610024232.6,CN200610122268.8,CN200810058439.4,CN201110259566.2,CN201210205498.6,CN201210296810.7,CN201310235094.6"}
        js = """
        (function($) {
            'use strict';

            function safe_add(x, y) {
                var lsw = (x & 0xFFFF) + (y & 0xFFFF),
                    msw = (x >> 16) + (y >> 16) + (lsw >> 16);
                return (msw << 16) | (lsw & 0xFFFF)
            }

            function bit_rol(num, cnt) {
                return (num << cnt) | (num >>> (32 - cnt))
            }

            function md5_cmn(q, a, b, x, s, t) {
                return safe_add(bit_rol(safe_add(safe_add(a, q), safe_add(x, t)), s), b)
            }

            function md5_ff(a, b, c, d, x, s, t) {
                return md5_cmn((b & c) | ((~b) & d), a, b, x, s, t)
            }

            function md5_gg(a, b, c, d, x, s, t) {
                return md5_cmn((b & d) | (c & (~d)), a, b, x, s, t)
            }

            function md5_hh(a, b, c, d, x, s, t) {
                return md5_cmn(b ^ c ^ d, a, b, x, s, t)
            }

            function md5_ii(a, b, c, d, x, s, t) {
                return md5_cmn(c ^ (b | (~d)), a, b, x, s, t)
            }

            function binl_md5(x, len) {
                x[len >> 5] |= 0x80 << (len % 32);
                x[(((len + 64) >>> 9) << 4) + 14] = len;
                var i, olda, oldb, oldc, oldd, a = 1732584193,
                    b = -271733879,
                    c = -1732584194,
                    d = 271733878;
                for (i = 0; i < x.length; i += 16) {
                    olda = a;
                    oldb = b;
                    oldc = c;
                    oldd = d;
                    a = md5_ff(a, b, c, d, x[i], 7, -680876936);
                    d = md5_ff(d, a, b, c, x[i + 1], 12, -389564586);
                    c = md5_ff(c, d, a, b, x[i + 2], 17, 606105819);
                    b = md5_ff(b, c, d, a, x[i + 3], 22, -1044525330);
                    a = md5_ff(a, b, c, d, x[i + 4], 7, -176418897);
                    d = md5_ff(d, a, b, c, x[i + 5], 12, 1200080426);
                    c = md5_ff(c, d, a, b, x[i + 6], 17, -1473231341);
                    b = md5_ff(b, c, d, a, x[i + 7], 22, -45705983);
                    a = md5_ff(a, b, c, d, x[i + 8], 7, 1770035416);
                    d = md5_ff(d, a, b, c, x[i + 9], 12, -1958414417);
                    c = md5_ff(c, d, a, b, x[i + 10], 17, -42063);
                    b = md5_ff(b, c, d, a, x[i + 11], 22, -1990404162);
                    a = md5_ff(a, b, c, d, x[i + 12], 7, 1804603682);
                    d = md5_ff(d, a, b, c, x[i + 13], 12, -40341101);
                    c = md5_ff(c, d, a, b, x[i + 14], 17, -1502002290);
                    b = md5_ff(b, c, d, a, x[i + 15], 22, 1236535329);
                    a = md5_gg(a, b, c, d, x[i + 1], 5, -165796510);
                    d = md5_gg(d, a, b, c, x[i + 6], 9, -1069501632);
                    c = md5_gg(c, d, a, b, x[i + 11], 14, 643717713);
                    b = md5_gg(b, c, d, a, x[i], 20, -373897302);
                    a = md5_gg(a, b, c, d, x[i + 5], 5, -701558691);
                    d = md5_gg(d, a, b, c, x[i + 10], 9, 38016083);
                    c = md5_gg(c, d, a, b, x[i + 15], 14, -660478335);
                    b = md5_gg(b, c, d, a, x[i + 4], 20, -405537848);
                    a = md5_gg(a, b, c, d, x[i + 9], 5, 568446438);
                    d = md5_gg(d, a, b, c, x[i + 14], 9, -1019803690);
                    c = md5_gg(c, d, a, b, x[i + 3], 14, -187363961);
                    b = md5_gg(b, c, d, a, x[i + 8], 20, 1163531501);
                    a = md5_gg(a, b, c, d, x[i + 13], 5, -1444681467);
                    d = md5_gg(d, a, b, c, x[i + 2], 9, -51403784);
                    c = md5_gg(c, d, a, b, x[i + 7], 14, 1735328473);
                    b = md5_gg(b, c, d, a, x[i + 12], 20, -1926607734);
                    a = md5_hh(a, b, c, d, x[i + 5], 4, -378558);
                    d = md5_hh(d, a, b, c, x[i + 8], 11, -2022574463);
                    c = md5_hh(c, d, a, b, x[i + 11], 16, 1839030562);
                    b = md5_hh(b, c, d, a, x[i + 14], 23, -35309556);
                    a = md5_hh(a, b, c, d, x[i + 1], 4, -1530992060);
                    d = md5_hh(d, a, b, c, x[i + 4], 11, 1272893353);
                    c = md5_hh(c, d, a, b, x[i + 7], 16, -155497632);
                    b = md5_hh(b, c, d, a, x[i + 10], 23, -1094730640);
                    a = md5_hh(a, b, c, d, x[i + 13], 4, 681279174);
                    d = md5_hh(d, a, b, c, x[i], 11, -358537222);
                    c = md5_hh(c, d, a, b, x[i + 3], 16, -722521979);
                    b = md5_hh(b, c, d, a, x[i + 6], 23, 76029189);
                    a = md5_hh(a, b, c, d, x[i + 9], 4, -640364487);
                    d = md5_hh(d, a, b, c, x[i + 12], 11, -421815835);
                    c = md5_hh(c, d, a, b, x[i + 15], 16, 530742520);
                    b = md5_hh(b, c, d, a, x[i + 2], 23, -995338651);
                    a = md5_ii(a, b, c, d, x[i], 6, -198630844);
                    d = md5_ii(d, a, b, c, x[i + 7], 10, 1126891415);
                    c = md5_ii(c, d, a, b, x[i + 14], 15, -1416354905);
                    b = md5_ii(b, c, d, a, x[i + 5], 21, -57434055);
                    a = md5_ii(a, b, c, d, x[i + 12], 6, 1700485571);
                    d = md5_ii(d, a, b, c, x[i + 3], 10, -1894986606);
                    c = md5_ii(c, d, a, b, x[i + 10], 15, -1051523);
                    b = md5_ii(b, c, d, a, x[i + 1], 21, -2054922799);
                    a = md5_ii(a, b, c, d, x[i + 8], 6, 1873313359);
                    d = md5_ii(d, a, b, c, x[i + 15], 10, -30611744);
                    c = md5_ii(c, d, a, b, x[i + 6], 15, -1560198380);
                    b = md5_ii(b, c, d, a, x[i + 13], 21, 1309151649);
                    a = md5_ii(a, b, c, d, x[i + 4], 6, -145523070);
                    d = md5_ii(d, a, b, c, x[i + 11], 10, -1120210379);
                    c = md5_ii(c, d, a, b, x[i + 2], 15, 718787259);
                    b = md5_ii(b, c, d, a, x[i + 9], 21, -343485551);
                    a = safe_add(a, olda);
                    b = safe_add(b, oldb);
                    c = safe_add(c, oldc);
                    d = safe_add(d, oldd)
                }
                return [a, b, c, d]
            }

            function binl2rstr(input) {
                var i, output = '';
                for (i = 0; i < input.length * 32; i += 8) {
                    output += String.fromCharCode((input[i >> 5] >>> (i % 32)) & 0xFF)
                }
                return output
            }

            function rstr2binl(input) {
                var i, output = [];
                output[(input.length >> 2) - 1] = undefined;
                for (i = 0; i < output.length; i += 1) {
                    output[i] = 0
                }
                for (i = 0; i < input.length * 8; i += 8) {
                    output[i >> 5] |= (input.charCodeAt(i / 8) & 0xFF) << (i % 32)
                }
                return output
            }

            function rstr_md5(s) {
                return binl2rstr(binl_md5(rstr2binl(s), s.length * 8))
            }

            function rstr_hmac_md5(key, data) {
                var i, bkey = rstr2binl(key),
                    ipad = [],
                    opad = [],
                    hash;
                ipad[15] = opad[15] = undefined;
                if (bkey.length > 16) {
                    bkey = binl_md5(bkey, key.length * 8)
                }
                for (i = 0; i < 16; i += 1) {
                    ipad[i] = bkey[i] ^ 0x36363636;
                    opad[i] = bkey[i] ^ 0x5C5C5C5C
                }
                hash = binl_md5(ipad.concat(rstr2binl(data)), 512 + data.length * 8);
                return binl2rstr(binl_md5(opad.concat(hash), 512 + 128))
            }

            function rstr2hex(input) {
                var hex_tab = '0123456789abcdef',
                    output = '',
                    x, i;
                for (i = 0; i < input.length; i += 1) {
                    x = input.charCodeAt(i);
                    output += hex_tab.charAt((x >>> 4) & 0x0F) + hex_tab.charAt(x & 0x0F)
                }
                return output
            }

            function str2rstr_utf8(input) {
                return unescape(encodeURIComponent(input))
            }

            function raw_md5(s) {
                return rstr_md5(str2rstr_utf8(s))
            }

            function hex_md5(s) {
                return rstr2hex(raw_md5(s))
            }

            function raw_hmac_md5(k, d) {
                return rstr_hmac_md5(str2rstr_utf8(k), str2rstr_utf8(d))
            }

            function hex_hmac_md5(k, d) {
                return rstr2hex(raw_hmac_md5(k, d))
            }

            function md5(string, key, raw) {
                if (!key) {
                    if (!raw) {
                        return hex_md5(string)
                    }
                    return raw_md5(string)
                }
                if (!raw) {
                    return hex_hmac_md5(key, string)
                }
                return raw_hmac_md5(key, string)
            }

            function encrty(s, e, t) {
                if (typeof s == "object") {
                    s = JSON.parse(s)
                }
                if (typeof s != "string") {
                    s = s + ""
                }
                s = md5(s + t);
                var res = "";
                for (var i = 0; i < s.length; i++) {
                    if (i % 2 == 0) {
                        res += String.fromCharCode(s.charCodeAt(i) + e.charCodeAt(i))
                    } else {
                        res += String.fromCharCode(s.charCodeAt(i) - e.charCodeAt(i))
                    }
                }
                return md5(res)
            }
            if (typeof define === 'function' && define.amd) {
                define(function() {
                    return encrty
                })
            } else {
                $.encrty = encrty
            }
        }(this));
                function getToken(unix_timestamp,queryData){
                    var key = "1YT7sdkI4pLw2OA6P3T5E2shDKgTBMbR";
                    var parmStr = "";
                    for (var k in queryData) {
                        parmStr += queryData[k];
                    }
                    queryData.sid = "nxf.ynmaker.com";
                    queryData.timestamp = unix_timestamp;
                    return encrty(parmStr, key, queryData.timestamp);
                }
            """
        ctx = execjs.compile(js)
        token = ctx.call("getToken", unix_timestamp, queryData)
        queryData['name'] = ""
        queryData['type'] = ""
        queryData['city_code'] = ""
        queryData['ipc'] = ""
        queryData['sid'] = "nxf.ynmaker.com"
        queryData['timestamp'] = unix_timestamp
        queryData['token'] = token
        results = requests.post(post_url, queryData)
        results_dict = json.loads(results.text)
        #成果列表页面返回的json格式
        """
        {
            "data": {
                "total": 1500790,
                "data": [{
                    "patent_id": "CN1306954",                        #专利号
                    "apply_date": "2000-01-28 00:00:00",
                    "name": "一种多元有机肥及其制备方法",                #成果名称
                    "id": "CN00100005.2",
                    "legal_status": "发明专利申请公布后的视为撤回",      #成果法律状态
                    "public_date": "2001-08-08 00:00:00",            #发布日期
                    "type": "发明专利",                               #成果类型
                    "ipc": "C05F11/08;C05F15/00;C05F17/00"
                }, {
                    "patent_id": "CN1256090",
                    "apply_date": "2000-01-04 00:00:00",
                    "name": "糯玉米粉的制备方法",
                    "id": "CN00100015.2",
                    "legal_status": "专利申请权、专利权的转移专利权的转移",
                    "public_date": "2002-07-17 00:00:00",
                    "type": "发明专利",
                    "ipc": "A23L1/105"
                }, {
                    "patent_id": "CN1302539",
                    "apply_date": "2000-01-06 00:00:00",
                    "name": "角隅灌溉系统",
                    "id": "CN00100089.6",
                    "legal_status": "公开",
                    "public_date": "2001-07-11 00:00:00",
                    "type": "发明专利",
                    "ipc": "A01G25/02;B05B3/02"
                }]
            },
            "success": 1
        }
        """
        if results_dict['success']:
            for result_list in results_dict['data']['data']:
                result_id = result_list['id']
                #成果详情返回的json格式
                """
                {
                    "data": {
                        "agent": "孙皓晨;韩小雷",                                  #代理人
                        "city_code": "370000",                                   #城市code
                        "source": "http://www.dataagri.com/agriculture/data/patentDetail.action?id=11B0C1E90A95905FE05302C711AC1D15",        #成果来源网址
                        "type": "发明专利",                                       #成果类型
                        "cmp_name": "费福生",                                     #申请(专利权)人
                        "cmp_id": null,
                        "create_by": "lichunyu",              
                        "apply_date": "2000-01-28 00:00:00",                     #申请日
                        "main_ipc": "C05F11/08",                                 #主分类号
                        "id": "CN00100005.2",
                        "legal_status": "发明专利申请公布后的视为撤回",              #成果状态
                        "public_date": "2001-08-08 00:00:00",                    #公开(公告)日
                        "create_date": "2018-01-22 06:08:01",
                        "update_by": "lichunyu",
                        "ipc": "C05F11/08;C05F15/00;C05F17/00",                  #分类号
                        "peoples": "费福生;邹连义",                                #发明(设计)人
                        "patent_id": "CN1306954",
                        "del_flag": "0",
                        "legal_histary": null,
                        "address": "山东省菏泽市技术监督局",                        #山东省菏泽市技术监督局
                        "agency": "北京科龙环宇专利事务所",                         #专利代理机构
                        "update_date": "2018-04-27 15:25:35",
                        "abstr": "本发明的多元有机肥的原料包括有机发酵物、尿素、硫酸钾和过磷酸钙,所述有机发酵物是由秸秆、粪便、麦麸子、红糖、钙镁磷肥和酵素菌等组成;制备时先发酵制得有机发酵物,再将尿素、硫酸钾或氯化钾、过磷酸钙混合搅拌均匀造粒即可。本发明的多元有机肥具有成本低、效果好、增产显著等特点。",                  #摘要
                        "name": "一种多元有机肥及其制备方法",                       #成果名称   下为成果详情
                        "detail": "<div class=\"patent_inner_right\">\r\n                <table width=\"100%\" border=\"0\" cellspacing=\"0\" cellpadding=\"0\">\r\n                    <tr>\r\n                        <td class=\"td_a\"> 专利名称</td>\r\n                        <td class=\"td_c\" colspan=\"3\"> 一种多元有机肥及其制备方法</td>\r\n                    </tr>\r\n                    <tr>\r\n                        <td class=\"td_a\"> 申请号</td>\r\n                        <td class=\"td_b\"> CN00100595.2</td>\r\n                        <td class=\"td_a\" colspan=\"-1\"> 申请日</td>\r\n                        <td class=\"td_b\"> 2000-01-28</td>\r\n                    </tr>\r\n                    <tr>\r\n                        <td class=\"td_a\"> 公开（公告）号</td>\r\n                        <td class=\"td_b\"> CN1306954</td>\r\n                        <td class=\"td_a\" colspan=\"-1\"> 公开（公告）日</td>\r\n                        <td class=\"td_b\"> 2001-08-08</td>\r\n                    </tr>\r\n                    <tr>\r\n                        <td class=\"td_a\"> 主分类号</td>\r\n                        <td class=\"td_b\"> C05F11/08</td>\r\n                        <td class=\"td_a\" colspan=\"-1\"> 分案原申请号</td>\r\n                        <td class=\"td_b\"> </td>\r\n                    </tr>\r\n                    <tr>\r\n                        <td class=\"td_a\"> 分类号</td>\r\n                        <td class=\"td_c\" colspan=\"3\"> C05F11/08;C05F15/00;C05F17/00</td>\r\n                    </tr>\r\n                    <tr>\r\n                        <td class=\"td_a\" colspan=\"-1\"> 颁证日</td>\r\n                        <td class=\"td_b\">  </td>\r\n                        <td class=\"td_a\"> 优先权</td>\r\n                        <td class=\"td_b\"> </td>\r\n\r\n                    </tr>\r\n                    <tr>\r\n                        <td class=\"td_a\"> 申请（专利权）人</td>\r\n                        <td class=\"td_b\"> 费福生</td>\r\n                        <td class=\"td_a\"> 发明（设计）人</td>\r\n                        <td class=\"td_b\"> 费福生;邹连义</td>\r\n\r\n                    </tr>\r\n                    <tr>\r\n                        <td class=\"td_a\"> 地址</td>\r\n                        <td class=\"td_c\" colspan=\"3\"> 山东省菏泽市技术监督局</td>\r\n                    </tr>\r\n                    <tr>\r\n                        <td class=\"td_a\"> 专利代理机构</td>\r\n                        <td class=\"td_b\"> 北京科龙环宇专利事务所 </td>\r\n                        <td class=\"td_a\"> 代理人</td>\r\n                        <td class=\"td_b\"> 孙皓晨;韩小雷 </td>\r\n                    </tr>\r\n                    <tr>\r\n                        <td class=\"td_a\"> 国际申请</td>\r\n                        <td class=\"td_b\"> </td>\r\n                        <td class=\"td_a\"> 国际公布</td>\r\n                        <td class=\"td_b\">  </td>\r\n                    </tr>\r\n                    <tr>\r\n                        <td class=\"td_a\"> 进入国家日期</td>\r\n                        <td class=\"td_b\">  </td>\r\n                        <td class=\"td_a\"></td>\r\n                        <td class=\"td_b\"></td>\r\n                    </tr>\r\n                    <tr>\r\n                        <td class=\"td_d\"> 摘要</td>\r\n                        <td class=\"td_c\" colspan=\"3\"> 本发明的多元有机肥的原料包括有机发酵物、尿素、硫酸钾和过磷酸钙,所述有机发酵物是由秸秆、粪便、麦麸子、红糖、钙镁磷肥和酵素菌等组成;制备时先发酵制得有机发酵物,再将尿素、硫酸钾或氯化钾、过磷酸钙混合搅拌均匀造粒即可。本发明的多元有机肥具有成本低、效果好、增产显著等特点。</td>\r\n                    </tr>\r\n                </table>\r\n                <table width=\"100%\" border=\"0\" cellspacing=\"0\" cellpadding=\"0\" style=\"display: none;\">\r\n                    \r\n                    <tr>\r\n                        <td class=\"td_a\">申请（专利）号</td>\r\n                        <td class=\"td_c\" colspan=\"3\"> CN00100595.2 </td>\r\n                    </tr>\r\n                    <tr>\r\n                        <td class=\"td_a\">法律状态公告日</td>\r\n                        <td class=\"td_c\" colspan=\"3\"> 2001-08-08 </td>\r\n\r\n                    </tr>\r\n                    <tr>\r\n                        <td class=\"td_a\"> 法律状态</td>\r\n                        <td class=\"td_c\" colspan=\"3\"> 公开 </td>\r\n                    </tr>\r\n                    \r\n                    <tr>\r\n                        <td class=\"td_a\">申请（专利）号</td>\r\n                        <td class=\"td_c\" colspan=\"3\"> CN00100595.2 </td>\r\n                    </tr>\r\n                    <tr>\r\n                        <td class=\"td_a\">法律状态公告日</td>\r\n                        <td class=\"td_c\" colspan=\"3\"> 2003-11-05 </td>\r\n\r\n                    </tr>\r\n                    <tr>\r\n                        <td class=\"td_a\"> 法律状态</td>\r\n                        <td class=\"td_c\" colspan=\"3\"> 发明专利申请公布后的视为撤回 </td>\r\n                    </tr>\r\n                    \r\n                </table>\r\n            </div>",
                        "remarks": null
                    },
                    "success": 1
                }
                """
                detail_url = 'http://www.weihengtech.com/index.php?s=/Home/Invention/shushangRequest/key/patentDetail.html'
                detail_query_data = {'id':result_id,'sid':'nxf.ynmaker.com','timestamp':unix_timestamp,'token':token}
                s = requests.session()
                s.keep_alive = False
                result_detail = requests.post(detail_url,detail_query_data)
                result_detail_dict = json.loads(result_detail.text)
                if result_detail_dict['success']:
                    result_detail_info = result_detail_dict['data']
                    result_detail_info['cmp_name'] = str(result_detail_info['cmp_name']) if result_detail_info['cmp_name'] is not None else ""
                    result_detail_info['abstr'] = str(result_detail_info['abstr']) if result_detail_info['abstr'] is not None else ""
                    result_detail_info['name'] = str(result_detail_info['name']) if result_detail_info['name'] is not None else ""
                    result_detail_info['source'] = str(result_detail_info['source']) if result_detail_info['source'] is not None else ""
                    result_detail_info['peoples'] = str(result_detail_info['peoples']) if result_detail_info['peoples'] is not None else ""
                    result_detail_info['address'] = str(result_detail_info['address']) if result_detail_info['address'] is not None else ""
                    #将采集到成果信息直接入库
                    owner_length = len(result_detail_info['cmp_name'])   #简单通过名字长度判断是个人还是企业  >3为企业  否则为个人
                    try:
                        with transaction.atomic():
                            #1 成果基本信息表入库
                            results_info = ResultsInfo.objects.create(
                                r_name = result_detail_info['name'] if len(result_detail_info['name']) <=64 else result_detail_info['name'][0,63],
                                r_form_type = 1,
                                r_abstract = result_detail_info['abstr'] if len(result_detail_info['abstr']) <=500 else result_detail_info['abstr'][0,499],
                                use_type = 1,
                                obtain_type = 1,
                                osource_name = result_detail_info['cmp_name'] if len(result_detail_info['cmp_name']) <=64 else result_detail_info['cmp_name'][0,63],
                                obtain_source = result_detail_info['source'] if len(result_detail_info['source']) <=255 else result_detail_info['source'][0,254],
                                entry_type = 3,
                                owner_type = 2 if owner_length >3 else 1,
                                expiry_dateb = result_detail_info['public_date'],
                                expiry_datee="2030-01-01",
                                rexpiry_dateb = result_detail_info['public_date'],
                                rexpiry_datee = "2030-01-01",
                                show_state = 1,
                                r_abstract_detail = result_detail_info['abstr'],
                                patent_number  = result_detail_info['patent_id'],
                            )
                            #2 成果持有个人|企业信息表入库
                            if owner_length > 3:
                                person_enterprise = enterprise_baseinfo = EnterpriseBaseinfo.objects.create(
                                    ename = result_detail_info['cmp_name'] if len(result_detail_info['cmp_name']) <=64 else result_detail_info['cmp_name'][0,63],
                                    manager = result_detail_info['peoples'] if len(result_detail_info['peoples']) <=16 else result_detail_info['peoples'][0,15],
                                    addr = result_detail_info['address'] if len(result_detail_info['address']) <=255 else result_detail_info['address'][0,254],
                                    state = 2,
                                )
                                person_enterprise_code = enterprise_baseinfo.ecode
                            else:
                                person_enterprise = person_baseinfo = PersonalInfo.objects.create(
                                    pname = result_detail_info['cmp_name'] if len(result_detail_info['cmp_name']) <=64 else result_detail_info['cmp_name'][0,63],
                                    pid_type = 1,
                                    pid = gen_uuid16(),
                                    state = 2,
                                )
                                person_enterprise_code = person_baseinfo.pcode
                            #3 领域类型信息入库
                            MajorUserinfo.objects.create(
                                mtype = 2,
                                user_type = 4,
                                user_code = results_info.r_code,
                                mcode = 'L1_0011',   #暂时都归到化学工业下面
                            )
                            #4 成果持有人信息入库
                            ResultsOwnerInfo.objects.create(
                                r_code = results_info.r_code,
                                owner_type = 2 if owner_length >3 else 1,
                                owner_code = person_enterprise.ecode if owner_length > 3 else person_enterprise.pcode,
                                main_owner = 1,
                                state = 1,
                                r_type = 1,
                            )
                    except Exception as e:
                        continue
                        # fail_msg = "入库失败%s" % str(e)
                        # return JsonResponse({"state": 0, "msg": fail_msg})

                    # csvfile = open('/home/tonbochow/python/spider/weihengtech.csv', 'a')
                    # csv_write = csv.writer(csvfile, dialect='excel')
                    # # csv_write = csv.writer(csvfile)
                    # result_info = [
                    #     result_detail_info['name'],                                #成果名称
                    #     result_detail_info['agent'],                               #代理人
                    #     result_detail_info['source'],                              #成果来源网址
                    #     result_detail_info['type'],                                #发明专利
                    #     result_detail_info['cmp_name'],                            #申请(专利权)人
                    #     result_detail_info['apply_date'],                          #申请日
                    #     result_detail_info['main_ipc'],                            #分类号
                    #     result_detail_info['legal_status'],                        #成果状态
                    #     result_detail_info['public_date'],                         #公开(公告)日
                    #     result_detail_info['ipc'],                                 #分类号
                    #     result_detail_info['peoples'],                             #发明(设计)人
                    #     result_detail_info['address'],                             #地址
                    #     result_detail_info['agency'],                              #专利代理机构
                    #     result_detail_info['abstr'],                               #摘要
                    #     # result_detail_info['detail'],                              #详情
                    # ]
                    # csv_write.writerow(result_info)
                    # csvfile.close()

                    try:
                        f = open("/home/tonbochow/python/spider/weihengtech_count.txt", "r+")
                        f.write(str(page_num + 1))
                    finally:
                        if f:
                            f.close()


        else:
            return JsonResponse({
                'count':0,
                'results':'',
                'results_detail':'',
            })




def get_ip_list(url, headers):
    web_data = requests.get(url, headers=headers)
    soup = BeautifulSoup(web_data.text, 'lxml')
    ips = soup.find_all('tr')
    ip_list = []
    for i in range(1, len(ips)):
        ip_info = ips[i]
        tds = ip_info.find_all('td')
        ip_list.append(tds[1].text + ':' + tds[2].text)
    return ip_list

def get_random_ip(ip_list):
    proxy_list = []
    for ip in ip_list:
        proxy_list.append('http://' + ip)
    proxy_ip = random.choice(proxy_list)
    proxies = {'http': proxy_ip}
    return proxies

# if __name__ == '__main__':
def getProxies():
    url = 'http://www.xicidaili.com/nn/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
    }
    ip_list = get_ip_list(url, headers=headers)
    proxies = get_random_ip(ip_list)
    return proxies
    # print(proxies)



