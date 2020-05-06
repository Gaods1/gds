import requests
import MySQLdb
from lxml import etree
# 从网络获取IP
# IP检测（可用）
# 存储IP
# 更新，随时补充新的IP


class ProxyPool:
    def __init__(self,maxsize=5,rate=0.7,limit=0):
        # 检测url
        self.localJSON=requests.get(url='http://httpbin.org/ip').text # 获得本机的IPJSON串
        #构建headers
        self.headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36'}
        # 数据库相关内容
        self.dbInit()
        # 设置阈值
        if limit!=0:
            self.limit=limit
        else:
            self.limit=int(maxsize*rate)

    # 构建数据库相关初始化
    def dbInit(self):
        self.conn=MySQLdb.connection(host='localhost', user='root', port=3306,
                                  password='123456', db='crawler', charset='utf8')
        self.cursor=self.conn.cursor()
        # 自动事务提交
        self.conn.autocommit(on=True)

    # 从网络获取IP
    def getOneProxyFromNet(self,targetUrl=None):
        targetUrl=(targetUrl if targetUrl else 'https://www.xicidaili.com/nn/%s')
        res=requests.get(url=targetUrl,headers=self.headers)
        # 解析res
        page = 1
        while 1:
            url = targetUrl % page
            with requests.session() as s:
                res = s.get(url=url)
                E = etree.HTML(res.text)
                trs = E.xpath('//tr[position()>1]')  # trs 列表，每个元素都是Element对象
                for i in trs:
                    tds = i.xpath('//td[2]|//td[3]|//td[6]')
                    p={tds[2]: tds[0] + ':' + tds[1]}
                    if self.checkIP(p):
                        return self.save(p)
            if page > 2000:
                break
            page += 1

    # IP检测可用性
    def checkIP(self,proxy): # url---拿到的IP

        try:
            resJSON=requests.get(url='http://httpbin.org/ip',proxies=proxy).text #
            if resJSON==self.localJSON:
                return False
            else:
                return True
        except:
            return False

    # 存储IP
    def save(self,proxy):
        # 拆代理
        s=proxy.keys()[0]+'='+proxy[proxy.keys()[0]]
        insertSQL='insert into proxy_pool VALUES (%s,1)'
        self.cursor.excute(insertSQL,[s])

    # 更新，补充IP
    def updateByLimit(self):
        if self.getIPNumber()<=self.limit:
            # 补货
            self.getOneProxyFromNet()
            self.updateByLimit()
        else:
            self.checkAll()

    # 获得所有有效IP的个数
    def getIPNumber(self):
        self.cursor.excute('select count(*) from proxy_pool where status=1')
        numer=self.cursor.fetchOne()[0]
        return numer

    # 提供代理服务接口
    def getIPFromPool(self):
        self.cursor.excute('select proxy from proxy_pool where status=1 limit=1')
        temp=self.cursor.fetchOne()[0]
        sList = temp.split('=')
        # 更改状态：
        self.cursor.excute('update proxy_pool set status=0 where proxy=%s'%temp)
        self.updateByLimit()
        return {sList[0]:sList[1]}

    # 重新全面检测所有的IP是否可用
    def checkAll(self):
        self.cursor.excute('select proxy from proxy_pool')
        all_ip=self.cursor.fetchAll()  # [(ip,),(ip,),(ip,)]
        for i in all_ip:
            sList = i[0].split('=')
            if self.checkIP({sList[0]: sList[1]}):
                self.cursor.excute('update proxy_pool set status=1 WHERE proxy=%s'%i[0])

if __name__ == '__main__':

    print(requests.get(url='http://httpbin.org/ip').text)
    print(requests.get(url='http://httpbin.org/ip',proxies={'http':'192.168.222.22:9999'}).text)

# IP代理池
# 爬虫策略 ： 深度优先策略DFS   广度优先策略BFS