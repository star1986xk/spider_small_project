import requests
from lxml import etree
import openpyxl
import time
import pymysql

headers = {
    # 'cookie': '__trackId=162393371346049; __city=lanzhou; _auth_redirect=https%3A%2F%2Flanzhou.baixing.com%2Fgongzuo%2F%3Fpage%3D1',
    'referer': 'https://lanzhou.baixing.com/gongzuo/?page=1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.3',
}
url = 'https://lanzhou.baixing.com/gongzuo/?page={}'
data = []
db = pymysql.connect(user="root", password="123456", host="localhost", database="spider")
cursor = db.cursor()


# 内容提取
def parser_itme(li):
    title = li.xpath('./div[contains(@class,"table-view-body job-list")]/div/a[@class="ad-title"]/text()')[0]
    salary = li.xpath('./div[contains(@class,"table-view-body job-list")]/span/text()')[0]
    job_list = \
        li.xpath('./div[contains(@class,"table-view-body -small")]/div[contains(@class,"table-view-cap job-list")]')[0]
    job = job_list.xpath("string(.)")
    wellfares_list = li.xpath(
        './div[contains(@class,"table-view-body -small")]/div[contains(@class,"wellfares-badges")]/label/text()')
    wellfares = '/'.join(wellfares_list)
    print(title)
    cursor.execute(
        "INSERT INTO `baixing` (`title`, `salary`, `job`, `wellfares`) VALUES ('%s', '%s', '%s', '%s');" % (
            title, salary, job, wellfares))
    db.commit()


# 索引页分析
def parser(url):
    response = requests.get(url)
    html = etree.HTML(response.text)
    li_list = html.xpath('//li[contains(@class,"listing-ad table-view-item apply-item  item-regular")]')
    for li in li_list:
        parser_itme(li)


# 保存表格
def save():
    book = openpyxl.Workbook()
    sheet = book.active
    sheet.append(['序号', '标题', '工资', '工作内容', '福利'])
    cursor.execute('select * from baixing')
    results = cursor.fetchall()
    for li in results:
        sheet.append(li)
    book.save('百姓网.xlsx')


# 主程序
def main():
    for n in range(1, 51):
        parser(url.format(n))
        print(n)
        time.sleep(30)
    save()
    db.close()


if __name__ == "__main__":
    main()
