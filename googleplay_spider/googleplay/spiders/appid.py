# -*- coding: utf-8 -*-
import sys, os
import re
import datetime, time

reload(sys)
sys.setdefaultencoding("utf-8")

from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.http import Request, FormRequest

from googleplay.settings import pymongo, db

class AppidSpider(Spider):

    name = "googleplay_appid"
    allowed_domains = ["play.google.com"]
    start_urls = []

    def start_requests(self):

        create_time = datetime.datetime.now()
        latest_time = db.spider_category.find({"channel": "googleplay"}).sort("create_time", pymongo.DESCENDING).limit(1)
        for item in db.spider_category.find({"channel": "googleplay", "create_time": latest_time[0]["create_time"]}):
            url = item["href"] + "/collection/topselling_free?hl=en"
            for i in range(5):
                start = str(i * 100 + 1)
                yield FormRequest(url, formdata = {"start": start, "num": "100"}, meta = {"create_time": create_time})
                #break
            #break

        '''Used for update some field value
        for item in db.spider_appid.find():
            url = "https://play.google.com/store/apps/details?id=%s&hl=en" % item["appid"]
            item = {
                "appid": item["appid"],
                "source": "crawler",
                "channel": "googleplay",
                "detail_url": url,
            }
            yield Request(url = url, meta = {"app_info": item}, callback = self.parse_item, dont_filter = True)
        '''
        

    def parse(self, response):

        items = []
        sel = Selector(response)
        apps = sel.xpath("//div[@id='wrapper']/div[@id='body-content']/div/div[@class='cluster-container']/div[@class='cluster normal square-cover apps show-all']/div[@class='card-list']/div[@class='card no-rationale square-cover apps small']")
        for app in apps:
            item = {
                "appid": app.xpath("@data-docid").extract()[0],
                "is_download_apk": False,
                "is_download_img": False,
                "source": "crawler",
                "channel": "googleplay",
                "create_time": response.meta["create_time"],
            }
            item["detail_url"] = "https://play.google.com/store/apps/details?id=%s&hl=en" % item["appid"]
            items.append(item)

        for item in items:
            yield Request(url = item["detail_url"], meta = {"app_info": item}, callback = self.parse_item, dont_filter = True)
            #break


    def parse_item(self, response):

        item = response.meta["app_info"]

        sel = Selector(response)
        item["price"] = sel.xpath("/html/body[@class='no-focus-outline']/div[@id='wrapper']/div[@id='body-content']/div[@class='details-wrapper apps square-cover id-track-partial-impression']/div[@class='details-info']/div[@class='info-container']/div[@class='details-actions']/span[@class='buy-button-container apps medium play-button']/button[@class='price buy']/span[2]/text()").extract()[0]
        if item["price"] == "Install": item["price"] = "free"

        r = re.search(r'data-docid="(.*?)"', response.body)
        if r:
            item['appid'] = r.group(1)

        r = re.search(r'itemprop="name">\s+<div>(.*?)</div>', response.body)
        if r:
            item['name'] = r.group(1)

        r = re.search(r'<span\s+itemprop="name">(.*?)</span>', response.body)
        if r:
            item['developer'] = r.group(1).encode('utf-8')

        r = re.search(r'href="/store/apps/category/(.*?)">\s+<span itemprop="genre">(.*?)</span>\s+</a>', response.body)
        if r:
            item['category_id'] = r.group(1)

        r = re.search(r'<div\s+class="id-app-orig-desc">(.*?)</div>', response.body)
        if r:
            item['description'] = r.group(1).encode('utf-8')

        r = re.search(r'<div\s+class="score">(.*?)</div>', response.body)
        if r:
            item['rating'] = float(r.group(1))

        r = re.search(r'<span\s+class="reviews-num">(.*?)</span>', response.body)
        if r:
            item['rating_user'] = r.group(1)

        r = re.search(r'<div\s+class="content"\s+itemprop="fileSize">(.*?)</div>', response.body)
        if r:
            item['size'] = r.group(1).strip()

        r = re.search(r'<div\s+class="content"\s+itemprop="softwareVersion">(.*?)</div>', response.body)
        if r:
            item['version'] = r.group(1).strip()

        r = re.search(r'<div\s+class="content"\s+itemprop="operatingSystems">(.*?)</div>', response.body)
        if r:
            item['operating_systems'] = r.group(1).replace('and up', '').strip() + '+'

        r = re.search(r'<div\s+class="content"\s+itemprop="datePublished">(.*?)</div>', response.body)
        if r:
            item['release_time'] = datetime.datetime.strptime(r.group(1).strip(), '%B %d, %Y')
            if not isinstance(item['release_time'], datetime.datetime):
                item['release_time'] = ''

        r = re.search(r'<div\s+class="cover-container">\s+<img\s+class="cover-image"\s+src="(.*?)"', response.body)
        if r:
            item['icon'] = r.group(1).strip()

        item['screenshot'] = re.findall(r'<img\s+class="full-screenshot".*?src="(.*?)"', response.body)

        #print item
        if db.spider_appid.find({"appid": item["appid"], "version": item["version"]}).count() == 0:
            print "LOG: Data Insert into DB, create_time = %s, category_id= %s, appid = %s, version = %s" % \
                (item["create_time"].strftime("%Y-%m-%d %H:%M:%S"), item["category_id"], item["appid"], item["version"])
            db.spider_appid.insert(item)
        else:
            print "LOG: Data had already in DB, appid = %s, version = %s" % (item["appid"], item["version"])

        return items


