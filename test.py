# 好爬取
import urllib.request
from bs4 import BeautifulSoup
from lxml import etree
import requests
import json
import jsonpath
import time
import re
from pymongo import MongoClient
Client = MongoClient('10.0.0.88',27017)
db = Client.test_ctrip
db_scenic = db.scenic_info
db_tickets = db.scenic_tickes
db_comments = db.comment
scenic_information = {}
scenic_ticket = {}

headers = {
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
'Accept-Language':'zh-CN,zh;q=0.8',
'Cache-Control':'max-age=0',
'Connection':'keep-alive',
'Cookie':'_abtest_userid=19680249-578a-4cea-a130-dd753c4e3b7b; adscityen=Beijing; ASP.NET_SessionSvc=MTAuMTUuMTI4LjM2fDkwOTB8b3V5YW5nfGRlZmF1bHR8MTUwOTk3MjI3NTc2Ng; TicketSiteID=SiteID=1008; appFloatCnt=2; manualclose=1; Union=SID=155952&AllianceID=4897&OUID=baidu81|index|||; Session=SmartLinkCode=U155952&SmartLinkKeyWord=&SmartLinkQuary=&SmartLinkHost=&SmartLinkLanguage=zh; traceExt=campaign=CHNbaidu81&adid=index; StartCity_Pkg=PkgStartCity=1; LatelySearch=c=U%7c%e4%b8%ad%e5%9b%bd%7c%e4%b8%ad%e5%9b%bd%7c0; _bfa=1.1522749510879.3opbhu.1.1523151692146.1523172916407.3.20; _bfs=1.13; _RF1=111.198.56.253; _RSG=u34TG6ID9lCLFMyRKV6alB; _RDG=28a48980f464b12add2b98f9420216adf2; _RGUID=cbc93521-9074-40f8-bbe4-19f51bf163d5; Mkt_UnionRecord=%5B%7B%22aid%22%3A%22481080%22%2C%22timestamp%22%3A1522749517020%7D%2C%7B%22aid%22%3A%224897%22%2C%22timestamp%22%3A1523173846471%7D%5D; _ga=GA1.2.1462720675.1522749517; _gid=GA1.2.610751600.1523151703; _gat=1; __zpspc=9.3.1523172922.1523173846.11%231%7Cbaidu%7Ccpc%7Cbaidu81%7C%25E6%2590%25BA%25E7%25A8%258B%25E6%2597%2585%25E8%25A1%258C%25E7%25BD%2591%7C%23; _jzqco=%7C%7C%7C%7C1523151703493%7C1.1402104330.1522749517210.1523173729898.1523173846511.1523173729898.1523173846511.undefined.0.0.17.17; MKT_Pagesource=PC; _bfi=p1%3D103061%26p2%3D103061%26v1%3D20%26v2%3D19',
'Host':'piao.ctrip.com',
'Upgrade-Insecure-Requests':1,
'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
        }

def get_page_url():
    url = 'http://piao.ctrip.com/dest/u-_d6_d0_b9_fa/s-tickets/P1'
    request = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(request)
    html = response.read().decode('utf-8')
    html_etree = etree.HTML(html)
    # 获取网页总页数
    pages_count = html_etree.xpath('//span[@class="c_page2_numtop"]/text()')[0].strip().split('/')[1].split('页')[0]
    # 景点网页url列表
    page_url_list = []
    for page in range(1,int(pages_count)+1):
        page_url = 'http://piao.ctrip.com/dest/u-_d6_d0_b9_fa/s-tickets/P' + str(page)
        page_url_list.append(page_url)
    return page_url_list

# 获取景点url列表
def get_scenic_url():
    url = 'http://piao.ctrip.com/dest/u-_d6_d0_b9_fa/s-tickets/P1'
    request = urllib.request.Request(url,headers=headers)
    response = urllib.request.urlopen(request)
    html = response.read().decode('utf-8')
    # print(html)
    html_etree = etree.HTML(html)

    scenic_href = html_etree.xpath('//a[@class="title"]/@href')
    print(scenic_href)
    scenic_list = []
    for href in scenic_href:
        scenic_url = 'http://piao.ctrip.com/' + href
        scenic_list.append(scenic_url)
    print(scenic_list)
    return scenic_list

# 获取景点基本信息
def get_scenic_data(url):
    request = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(request)
    html = response.read().decode('utf-8')
    html_etree = etree.HTML(html)
    # 景点产品id
    product_id = re.findall(r'productid:(.*),.*',html)[0].strip()
    print(product_id)
    # 景点id
    scenic_id = re.findall(r'.*\/t(\d+)',url)[0]
    print(scenic_id)
    # print(html)

    # 景点基本信息抓取
    # 景点名字
    scenic_name = html_etree.xpath('//div[@class="media-right"]/h2[@class="media-title"]/text()')[0]
    scenic_information['scenic_name'] = scenic_name
    # 景点等级
    scenic_grade = html_etree.xpath('//div[@class="media-right"]/span[@class="media-grade"]/strong/text()')[0]
    scenic_information['scenic_grade'] = scenic_grade
    # 景点地址
    scenic_address = html_etree.xpath('//div[@class="media-right"]/ul/li[@style=""]/span/text()')[0].strip()
    scenic_information['scenic_address'] = scenic_address
    # 景点开放时间
    scenic_time = html_etree.xpath('//div[@class="media-right"]/ul/li[@class="time"]/span[@class="j-limit"]/text()')[0]
    scenic_information['scenic_time'] = scenic_time
    # 景点评分
    scenic_score = html_etree.xpath('//div[@class="grade"]/i/text()')[0] + '/5分'
    scenic_information['scenic_score'] = scenic_score
    # 景点价格
    scenic_price = html_etree.xpath('//div[@class="media-price"]/div/span/text()')[0].strip()
    scenic_information['scenic_price'] = scenic_price
    # 景点交通
    scenic_traffic = html_etree.xpath('//div[@class="feature-traffic"]')[0].xpath('string(.)')
    scenic_information['scenic_traffic'] = scenic_traffic
    # 景点评论数
    sceinc_comments_count = html_etree.xpath('//div[@class="grade"]/a/text()')[0].split('看')[1].split('点')[0]
    scenic_information['scenic_comments_count'] = sceinc_comments_count
    # 景点政策
    scenic_polic = html_etree.xpath('//dl[@class="c-wrapper-info"]/dd[@style=""]/div[2]/text()')[0].strip()
    scenic_information['scenic_polic'] = scenic_polic
    # 景区特色
    scenic_feature = html_etree.xpath('//div[@class="feature-wrapper"]/ul/li/p/text()')
    scenic_information['scenic_feature'] = scenic_feature
    # 景区简介
    scenic_feature_count = html_etree.xpath('//div[@class="feature-content"]/p/text()')
    scenic_information['scenic_feature_count'] = scenic_feature_count
    # 景区图片
    scenic_img = html_etree.xpath('//div[@class="feature-content"]/p/img/@data-src')
    scenic_information['scenic_img'] = scenic_img
    # print('景点基本信息：', scenic_information)
    # 景点信息写入
    # with open('scenic_information.txt','a',encoding='utf-8') as fp:
    #     fp.write(str(scenic_information))
    # 写入MongoDB数据库
    # db_scenic.insert_one(scenic_information)

    # 门票产品信息抓取
    # 门票名称列表
    scenic_tickets_list = html_etree.xpath('//td[@class="ticket-title-wrapper"]/a[@class="ticket-title"]/text()')
    # print(scenic_tickets_list)
    # 门票提前预定时间列表
    # scenic_reserve_list = html_etree.xpath('//tr[starts-with(@class,"ticket-info")]/td[3]/text()')
    # print(scenic_reserve_list)
    # 门票市场价价格列表
    scenic_market_list =html_etree.xpath('//td[@class="del-price"]/strong/text()')
    # print(scenic_market_list)
    # 门票携程价格列表
    scenic_ctrip_list =html_etree.xpath('//span[@class="ctrip-price"]/strong/text()')
    # print(scenic_ctrip_list)
    # 门票id列表
    scenic_detail_list = html_etree.xpath('//tr[starts-with(@class,"ticket-info")]/@data-id')
    # print(scenic_detail_list)
    # 储存门票类型列表
    scenic_type_list = [1]
    for i in range(len(scenic_tickets_list)):
        # 自建id
        scenic_ticket['_id'] = i
        # 门票名称
        scenic_ticket["ticket_name"] = scenic_tickets_list[i]
        # 门票类型
        if html_etree.xpath('//tr[starts-with(@class,"ticket-info")]' + str([i+1]) + '/td[@class="ticket-type"]/span/text()') != []:
            scenic_ticket['scenic_type'] = html_etree.xpath('//tr[starts-with(@class,"ticket-info")]' + str([i+1]) + '/td[@class="ticket-type"]/span/text()')[0]
            scenic_type_list.append(scenic_ticket['scenic_type'])
            del scenic_type_list[0]
            print('scenic_type_list',scenic_type_list)
            # 门票提前预定时间
            scenic_ticket['scenic_reserve_time'] = html_etree.xpath('//tr[starts-with(@class,"ticket-info")]' + str([i+1]) + '/td[3]/text()')[0].strip()
        else:
            scenic_ticket['scenic_type'] = scenic_type_list[0]
            # 门票提前预定时间
            scenic_ticket['scenic_reserve_time'] = html_etree.xpath(
                '//tr[starts-with(@class,"ticket-info")]' + str([i + 1]) + '/td[2]/text()')[0].strip()
        # 门票市场价格
        scenic_ticket["market_price"] = scenic_market_list[i].strip()
        # 门票携程价格
        scenic_ticket['ctrip_price'] = scenic_ctrip_list[i].strip()
        # 门票详情抓取
        detail_url = 'http://piao.ctrip.com/Thingstodo-Booking-ShoppingWebSite/api/TicketStatute?resourceID=' + scenic_detail_list[i]
        # print(detail_url)
        detail_response = requests.get(detail_url)
        # print(detail_response.text)
        detail_html = detail_response.text
        time.sleep(3)
        scenic_obj = json.loads(detail_html)
        # 门票详情
        scenic_detail = jsonpath.jsonpath(scenic_obj,'$..data')[0]
        scenic_ticket['ticket_detail'] = scenic_detail
        # print(scenic_detail)
        #  门票政策
        scenic_promise = html_etree.xpath('//div[@class="media-right"]/ul/li[@class="promise"]/div/div[@class="jmp pop-content"]/text()')[0].strip()
        scenic_ticket['scenic_promise'] = scenic_promise
        # 景点名称
        scenic_ticket['scenic_name'] = scenic_name
        # 支付方式
        scenic_ticket['ticket_payment'] = url
        # print('门票信息',scenic_ticket)
        # 门票信息写入
        # with open('scenic_ticket.txt','a',encoding='utf-8') as fp:
        #     fp.write(str(scenic_ticket)+'\n')
        # 保存数据库
        # db_tickets.insert_one(scenic_ticket)

    # 景点评论抓取
    for i in range(100000):
        commnet_url = 'http://piao.ctrip.com/Thingstodo-Booking-ShoppingWebSite/api/TicketDetailApi' \
                      '/action/GetUserComments?productId=' + str(product_id) + '&scenicSpotId=' +\
                      str(scenic_id) + '&page=' + str(i)
        comments_response = requests.get(url=commnet_url)
        comments_text = comments_response.text
        obj_comments = json.loads(comments_text)
        print(obj_comments)
        if obj_comments['Comment'] != '[]':
            comments = obj_comments['Comment']
            for comment in comments:
                print(comment)
            #     comments['scenic_name'] = scenic_name
            #     print(comments)
            #     time.sleep(2)
                with open('scenic_comments.txt','a',encoding='utf-8') as fp:
                    fp.write(str(comment)+'\n')
            #     # 保存数据库
            #     # db_comments.insert_one(comments)
        # else:
        #     break

if __name__ == '__main__':
    url = 'http://piao.ctrip.com//dest/t229.html'
    get_scenic_data(url)
    # get_scenic_url()

