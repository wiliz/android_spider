# -*- coding: utf-8 -*-
import sys, os
import signal
import re, random
import datetime, time

reload(sys)
sys.setdefaultencoding("utf-8")

from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.http import Request, FormRequest

from googleplay.settings import pymongo, db

class GoogleplaySpider(Spider):

    name = "googleplay_appid_all"
    #download_delay = 1
    allowed_domains = ["play.google.com"]
    start_urls = ["https://play.google.com/store/apps"]

    collection = db.spider_appid_all

    def parse(self, response):

        self.crawler.stats.set_value("app_crawled_count", 0)

        #appid = "com.gameloft.android.ANMP.GloftM5HM"
        #url = "https://play.google.com/store/apps/details?id=%s&hl=en" % appid 

        # Get Appid From Googleplay Home Page
        #r = re.findall(r'<div class="card no-rationale square-cover apps.*?data-docid="(.*?)"', response.body)
        #index = random.randint(0, len(r) - 1)
        #url = "https://play.google.com/store/apps/details?id=%s&hl=en" % r[index] 

        item = db.spider_appid_daily.find_one({"is_crawled": False})
        url = "https://play.google.com/store/apps/details?id=%s&hl=en" % item["appid"] 
        
        yield Request(url, meta = {"item": item}, callback = self.parse_item, errback = self.parse_item_errback)


    def parse_item(self, response):

        meta_data = response.meta["item"]
        create_time = datetime.datetime.now()

        item = {
            "is_download_apk": False, 
            "is_download_img": False,
            "source": "crawler",
            "channel": "googleplay",
            "create_time": create_time, 
        }

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

        # Insert to DB
        if self.collection.find({"appid": item["appid"], "version": item["version"]}).limit(1).count() == 0:
            print "LOG: Data Insert into DB, create_time = %s, category_id = %s, appid = %s, version = %s" % \
                (item["create_time"].strftime("%Y-%m-%d %H:%M:%S"), item["category_id"], item["appid"], item["version"])
            self.collection.insert(item)
            self.crawler.stats.set_value("app_crawled_count", 0)
        else:
            tmp_num = self.crawler.stats.get_value("app_crawled_count")
            print "LOG: [%s] Data Already In DB" % tmp_num
            self.crawler.stats.inc_value("app_crawled_count")

        if self.crawler.stats.get_value("app_crawled_count") >= 100:
            db.spider_appid_daily.update({"_id": meta_data["_id"]}, {"$set": {"is_crawled": True}})
            print "Kill Spider Progress"
            os.kill(os.getpid(), signal.SIGKILL) 

        # Get relative app
        appids = re.findall(r'<div class="card no-rationale square-cover apps small" data-docid="(.*?)"', response.body)
        for appid in appids:
            url = "https://play.google.com/store/apps/details?id=%s&hl=en" % appid
            yield Request(url, meta = {"item": meta_data}, callback = self.parse_item, dont_filter = True)


    def parse_item_errback(self, response):

        err_msg = response.getErrorMessage()
        meta_data = response.request.meta["item"]
        db.spider_appid_daily.update({"_id": meta_data["_id"]}, {"$set": {"is_crawled": True, "": err_msg}})
        print "Kill Spider Progress"
        os.kill(os.getpid(), signal.SIGKILL) 



