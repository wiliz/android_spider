# -*- coding: utf-8 -*-
import sys, re, copy
import datetime, time

from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.http import Request, FormRequest

from googleplay.settings import pymongo, db

class GoogleplaySpider(Spider):

    name = "googleplay_appid_daily"
    allowed_domains = ["play.google.com"]
    start_urls = []

    def start_requests(self):

        create_time = datetime.datetime.now()

        urls = [
            {
                "url": "https://play.google.com/store/apps/category/GAME/collection/topselling_free?hl=en",
                "class": "Top Charts",
                "group": "game",
                "type": "topselling_free",
            },{
                "url": "https://play.google.com/store/apps/category/GAME/collection/topselling_paid?hl=en",
                "class": "Top Charts",
                "group": "game",
                "type": "topselling_paid",
            },{
                "url": "https://play.google.com/store/apps/category/GAME/collection/topgrossing?hl=en",
                "class": "Top Charts",
                "group": "game",
                "type": "topgrossing",
            },{
                "url": "https://play.google.com/store/apps/collection/topselling_free?hl=en",
                "class": "Top Charts",
                "group": "app",
                "type": "topselling_free",
            },{
                "url": "https://play.google.com/store/apps/collection/topselling_paid?hl=en",
                "class": "Top Charts",
                "group": "app",
                "type": "topselling_paid",
            },{
                "url": "https://play.google.com/store/apps/collection/topgrossing?hl=en",
                "class": "Top Charts",
                "group": "app",
                "type": "topgrossing",
            },{
                "url": "https://play.google.com/store/apps/category/GAME/collection/topselling_new_free?hl=en",
                "class": "New Releases",
                "group": "game",
                "type": "topselling_free",
            },{
                "url": "https://play.google.com/store/apps/category/GAME/collection/topselling_new_paid?hl=en",
                "class": "New Releases",
                "group": "game",
                "type": "topselling_paid",
            },{
                "url": "https://play.google.com/store/apps/collection/topselling_new_free?hl=en",
                "class": "New Releases",
                "group": "app",
                "type": "topselling_free",
            },{
                "url": "https://play.google.com/store/apps/collection/topselling_new_paid?hl=en",
                "class": "New Releases",
                "group": "app",
                "type": "topselling_paid",
            },
        ]

        for item in urls:
            for i in range(5):
                start = str(i * 100 + 1)
                item["create_time"] = create_time
                yield FormRequest(url = item["url"], formdata = {"start": start, "num": "100"}, meta = {"data": item}, dont_filter = True)
                #break
            #break

    def parse(self, response):

        data = {
            "class": response.meta["data"]["class"],
            "group": response.meta["data"]["group"],
            "type": response.meta["data"]["type"],
            "is_crawled": False,
            "batch": response.meta["data"]["create_time"].strftime("%Y%m%d"),
            "create_time": response.meta["data"]["create_time"],
        }

        appids = re.findall(r'<div class="card no-rationale square-cover apps small".*?data-docid="(.*?)"', response.body)
        for appid in appids:
            item = copy.copy(data)
            item["appid"] = appid
            if db.spider_appid_daily.find({"appid": appid, "batch": item["batch"]}).count() == 0:
                print "LOG: Data Insert Into DB, create_time = %s, appid = %s" % (item["create_time"], appid)
                db.spider_appid_daily.insert(item)


