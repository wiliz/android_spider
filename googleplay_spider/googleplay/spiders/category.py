import re
import datetime

from scrapy.spider import Spider
from scrapy.selector import Selector

from googleplay.settings import pymongo, db

class CategorySpider(Spider):

    name = "googleplay_category"
    allowed_domains = ["play.google.com"]
    start_urls = [
        "https://play.google.com/store/apps?hl=en"
    ]

    def parse(self, response):

        create_time = datetime.datetime.now()
        items = []

        sel = Selector(response)
        # App Category
        categories = sel.xpath("//div[@id='wrapper']/div[@class='action-bar-container']/div[@class='action-bar-inner']/div[@class='action-bar apps']/div[@class='action-bar-item']/div[@class='action-bar-dropdown-container']/div[@class='action-bar-dropdown-children-container']/div[@class='dropdown-submenu']/ul/li[@class='action-dropdown-outer-list-item'][1]/ul/li[@class='child-submenu-link-wrapper']")
        for category in categories:
            item = {
                "title": category.xpath("a/@title").extract()[0],
                "href": "https://play.google.com" + category.xpath("a/@href").extract()[0],
                "group": "app",
                "channel": "googleplay",
                "create_time": create_time,
            }
            item["name"] = re.match(".*/(.*)", item["href"]).group(1)
            items.append(item)

        # Game Category
        categories = sel.xpath("//div[@id='wrapper']/div[@class='action-bar-container']/div[@class='action-bar-inner']/div[@class='action-bar apps']/div[@class='action-bar-item']/div[@class='action-bar-dropdown-container']/div[@class='action-bar-dropdown-children-container']/div[@class='dropdown-submenu']/ul/li[@class='action-dropdown-outer-list-item'][2]/ul/li[@class='child-submenu-link-wrapper']")
        for category in categories:
            item = {
                "title": category.xpath("a/@title").extract()[0],
                "href": "https://play.google.com" + category.xpath("a/@href").extract()[0],
                "group": "game",
                "channel": "googleplay",
                "create_time": create_time,
            } 
            item["name"] = re.match(".*/(.*)", item["href"]).group(1)
            items.append(item)
        
        for item in items:
            print "LOG: Data Insert into DB, create_time = %s, category_name = %s" % \
                (item["create_time"].strftime("%Y-%m-%d %H:%M:%S"), item["name"])
            db.spider_category.insert(item)

