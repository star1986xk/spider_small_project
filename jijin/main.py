import requests
from lxml import etree
import openpyxl
import time
import pymysql

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'
}
db = pymysql.connect(user="root", password="123456", host="localhost", database="spider")
cursor = db.cursor()


def create_excel():
    '''
    创建一个新的excel
    :return:
    '''
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(['标题', '发布时间', '内容', '网址'])
    cursor.execute('select * from jijin')
    results = cursor.fetchall()
    for li in results:
        ws.append(li)
    wb.save('data.xlsx')


def spider_index(page: int):
    '''
    解析索引页
    :param page: 页码
    :return: 索引URL列表
    '''
    url = 'https://roll.eastmoney.com/fund_{}.html'.format(page)
    response = requests.get(url)
    html = etree.HTML(response.text)
    index_url = html.xpath('//div[@id="artList"]/ul/li/a/@href')
    index_url = [str(li) for li in index_url if 'http' in li]
    return index_url


def parser_content(url: str):
    '''
    解析内容页
    :param url:网址a
    :return:
    '''
    try:
        response = requests.get(url, headers=headers)
        response.encoding = response.apparent_encoding
        html = etree.HTML(response.text)
        title = html.xpath('//div[@class="title"]/text()')[0].strip()
        datetime = html.xpath('//div[@class="infos"]/div[1]/text()')[0].strip()
        content = html.xpath('//div[@id="ContentBody"]')[0]
        content = str(etree.tostring(content, encoding="utf-8", pretty_print=True, method="html"),
                      encoding='utf8').strip()
        print(title, datetime)
        cursor.execute(
            "INSERT INTO `jijin` (`title`, `datetime`, `content`, `url`) VALUES ('%s', '%s', '%s', '%s');" % (
                title, datetime, content, url))
        db.commit()
    except Exception as e:
        pass


def run(page_star: int, page_end: int):
    '''
    主程序
    :param page_star:开始页数
    :param page_end: 结束页数
    :return:
    '''
    for page in range(page_star, page_end + 1):
        index_url = spider_index(page)
        for url in index_url:
            parser_content(url)
            time.sleep(0.1)
    create_excel()
    db.close()

if __name__ == '__main__':
    run(1, 100)
