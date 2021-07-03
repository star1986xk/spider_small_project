import requests
from lxml import etree
import openpyxl
import pymysql

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 6.1;) AppleWebKit/537.3 Chrome/85.0'
}
url = 'http://college.gaokao.com/schlist/p%d/'
data = []
db = pymysql.connect(user="root", password="123456", host="localhost", database="spider")
cursor = db.cursor()

# 内容提取
def get_content(li):
    title = li.xpath('./dt/strong/a/text()')[0]
    li_list = li.xpath('./dd/ul/li')
    dizhi = str(li_list[0].xpath('./text()')[0]).replace('高校所在地：', '')
    tese_list = li_list[1].xpath('./span/text()')
    tese = '/'.join(tese_list) if tese_list else '——'
    leixing = str(li_list[2].xpath('./text()')[0]).replace('高校类型：', '')
    lishu = str(li_list[3].xpath('./text()')[0]).replace('高校隶属：', '')
    xingzhi = str(li_list[4].xpath('./text()')[0]).replace('高校性质：', '')
    wangzhi = str(li_list[5].xpath('./text()')[0]).replace('学校网址：', '')
    print(title)
    data.append([title, dizhi, tese, leixing, lishu, xingzhi, wangzhi])
    cursor.execute(
        "INSERT INTO `gaokao` (`title`, `dizhi`, `tese`, `leixing`, `lishu`, `xingzhi`, `wangzhi`) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s');" % (
            title, dizhi, tese, leixing, lishu, xingzhi, wangzhi))
    db.commit()

# 索引页分析
def get_index(url):
    response = requests.get(url)
    html = etree.HTML(response.text)
    dl_list = html.xpath('//div[@class="scores_List"]/dl')
    for li in dl_list:
        get_content(li)


# 保存表格
def save():
    book = openpyxl.Workbook()
    sheet = book.active
    sheet.append(['学校名称', '高校所在地', '院校特色', '高校类型', '高校隶属', '高校性质', '学校网址'])
    cursor.execute('select * from gaokao')
    results = cursor.fetchall()
    for li in results:
        sheet.append(li)
    book.save('学校.xlsx')


# 主程序
def main():
    for n in range(1, 95):
        print(n)
        get_index(url % n)
    save()


if __name__ == "__main__":
    main()
