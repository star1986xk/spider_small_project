import requests
from lxml import etree
import openpyxl
import time
import random
import re
import pymysql


class Fangtianxia():
    def __init__(self, total):
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0',
            'referer': 'https://www.baidu.com/'
        }
        self.url = 'https://lz.esf.fang.com/house/i3{}/'
        self.total = total

        self.db = pymysql.connect(user="root", password="123456", host="localhost", database="spider")
        self.cursor = self.db.cursor()

    def parser(self, dl):
        try:
            biaoti = dl.xpath('./dd/h4/a/span/text()')[0].strip()
            info = dl.xpath('./dd/p[@class="tel_shop"]')[0].xpath("string(.)").split('|')
            huxing = info[0].strip()
            mianji = info[1].strip()
            louceng = info[2].strip()
            chaoxiang = info[3].strip()
            nianfen = info[4].strip()
            nianfen = nianfen if re.search('^\d+', nianfen) else ''
            xiaoqu = dl.xpath('./dd/p[@class="add_shop"]/a/text()')[0].strip()
            dizhi = dl.xpath('./dd/p[@class="add_shop"]/span/text()')[0].strip()
            zongjia = dl.xpath('./dd[@class="price_right"]/span[1]')[0].xpath("string(.)").strip()
            danjia = dl.xpath('./dd[@class="price_right"]/span[2]/text()')[0].strip()
            print(biaoti)
            self.cursor.execute(
                "INSERT INTO `fangtianxia` (`biaoti`, `huxing`, `mianji`, `louceng`, `chaoxiang`, `nianfen`, `xiaoqu`, `dizhi`, `zongjia`, `danjia`) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');" % (
                    biaoti, huxing, mianji, louceng, chaoxiang, nianfen, xiaoqu, dizhi, zongjia, danjia))
            self.db.commit()
        except Exception as e:
            pass

    def spider(self):
        for n in range(1, self.total + 1):
            response = requests.get(self.url.format(n), headers=self.headers)
            html = etree.HTML(response.text)
            dl_list = html.xpath('//dl[@class="clearfix"]')
            for dl in dl_list:
                self.parser(dl)
            time.sleep(random.uniform(2, 5))

    def save(self):
        self.book = openpyxl.Workbook()
        self.sheet = self.book.active
        self.sheet.append(['标题', '户型', '面积', '楼层', '朝向', '年份', '小区名称', '地址', '总价', '单价'])
        self.cursor.execute('select * from fangtianxia')
        results = self.cursor.fetchall()
        for li in results:
            self.sheet.append(li)
        self.book.save('房天下.xlsx')
        self.db.close()

f = Fangtianxia(20)
f.spider()
