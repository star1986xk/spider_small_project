import requests
from lxml import etree
import openpyxl
import pymysql

url = 'http://gs.people.com.cn/GB/183283/index{}.html'
home = 'http://gs.people.com.cn'
db = pymysql.connect(user="root", password="123456", host="localhost", database="spider")
cursor = db.cursor()


# 生成表格
def excel():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(['标题', '发布时间', '作者', '内容', '网址'])
    cursor.execute('select * from renminwang')
    results = cursor.fetchall()
    for li in results:
        ws.append(li)
    wb.save('结果.xlsx')


# 解析索引页
def spider_index(n: int):
    response = requests.get(url.format(n))
    response.encoding = 'GBK'
    html = etree.HTML(response.text)
    index_url = html.xpath('//ul[contains(@class,"list_16")]/li/a/@href')
    index_url = [home + str(li) for li in index_url]
    return index_url


# 解析内容页
def parser_content(url: str):
    try:
        response = requests.get(url)
        response.encoding = response.apparent_encoding
        html = etree.HTML(response.text)
        title = html.xpath('//h1[@id="newstit"]/text()')[0].strip()
        datetime = str(html.xpath('//div[@class="box01"]/div/text()')[0].strip()).split(' ')[0]
        author = html.xpath('//p[@class="author"]/text()')[0].strip()
        content = html.xpath('//div[@class="box_con"]')[0]
        content = str(etree.tostring(content, encoding="utf-8", pretty_print=True, method="html"),
                      encoding='utf8').strip()
        print(title, datetime)
        cursor.execute(
            "INSERT INTO `renminwang` (`title`, `datetime`, `author`, `content`, `url`) VALUES ('%s', '%s', '%s', '%s', '%s');" % (
                title, datetime, author, content, url))
        db.commit()
    except Exception as e:
        pass


# 入口
def main(star: int, end: int):
    for n in range(star, end + 1):
        index_url = spider_index(n)
        for url in index_url:
            parser_content(url)
    excel()
    db.close()


if __name__ == '__main__':
    main(1, 100)
