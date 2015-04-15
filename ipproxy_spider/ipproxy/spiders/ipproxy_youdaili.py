# -*- coding: utf-8 -*-

import re
import datetime
import socket

from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.http import Request

from ipproxy.items import IpproxyItem

class IpproxySpider(Spider):

    name = "ipproxy"
    allowed_domains = ["youdaili.cn"]
    start_urls = [ 
        "http://www.youdaili.cn/Daili/http/list_1.html",
        #"http://www.youdaili.cn/Daili/http/list_2.html",
        #"http://www.youdaili.cn/Daili/http/list_3.html",
        #"http://www.youdaili.cn/Daili/http/list_4.html",
        #"http://www.youdaili.cn/Daili/http/list_5.html",
        #"http://www.youdaili.cn/Daili/http/list_6.html",
        #"http://www.youdaili.cn/Daili/http/list_7.html",
        #"http://www.youdaili.cn/Daili/http/list_8.html",
        #"http://www.youdaili.cn/Daili/http/list_9.html",
        #"http://www.youdaili.cn/Daili/http/list_10.html",
    ]


    def parse(self, response):
        sel = Selector(response)
        documents = sel.xpath("/html/body/div[@class='container']/div[@class='content_full']/div[@class='content']/div[@class='content_newslist']/div[@class='newslist_body']/ul[@class='newslist_line']/li")
        #print len(documents)

        for doc in documents:
            url = doc.xpath("a/@href").extract()[0]
            if doc.xpath("span[@class='articlelist_time']/font"):
                public_time = doc.xpath("span[@class='articlelist_time']/font/text()").extract()[0]
            else:
                public_time = doc.xpath("span[@class='articlelist_time']/text()").extract()[0]
            yield Request(url, meta = {"public_time": public_time}, callback = self.parse_item)
            #break


    def parse_item(self, response):
        url = response.url

        sel = Selector(response)
        data = sel.xpath("/html/body/div[@class='container']/div[@class='content_full']/div[@class='content']/div[@class='content_newslist']/div[@class='newsdetail_cont']/div[@class='cont_font']/div[@class='dede_pages']/ul[@class='pagelist']/li[1]/a/text()").extract()[0]
        page_size = int(re.search(r"(\d)", data).group(0))

        for i in range(1, page_size + 1): 
            if i == 1:
                yield Request(url, meta = {"public_time": response.meta["public_time"]}, callback = self.parse_data, dont_filter = True)
            else:
                url2 = url.replace(".html", "_%s.html" % i)
                yield Request(url, meta = {"public_time": response.meta["public_time"]}, callback = self.parse_data)


    def parse_data(self, response):
        items = []
        sel = Selector(response)

        document = sel.xpath("/html/body/div[@class='container']/div[@class='content_full']/div[@class='content']/div[@class='content_newslist']/div[@class='newsdetail_cont']/div[@class='cont_font']/p/text()").extract()
        for doc in document:
            res = re.search(r"(.*):(.*)@(.*)#(.*)", doc)
            item = IpproxyItem()
            item["channel"] = "youdaili"
            item["ip"] = res.group(1)
            item["port"] = res.group(2)
            item["site"] = res.group(4)
            item["priority"] = 0
            item["deleted"] = False
            item["public_time"] = response.meta["public_time"]
            item["create_time"] = datetime.datetime.now()
            items.append(item)

            '''
            flag = self._check_proxy(item["ip"], item["port"])
            print str(flag) + "    " + item["ip"] + "    " + item["port"]
            if flag: items.append(item)
            '''

        return items

 
    def _check_proxy(self, ip, port):
        result = True
        sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sk.settimeout(5)
        try:
            sk.connect((ip,port))
        except Exception:
            result = False
        sk.close()
        return result
