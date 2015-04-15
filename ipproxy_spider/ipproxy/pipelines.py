# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
import ipproxy.settings as settings
db_host = settings.MONGODB["host"]
db_port = settings.MONGODB["port"]
db = pymongo.MongoClient(db_host, db_port).android_spider

class IpproxyPipeline(object):

    def process_item(self, item, spider):

        if db.proxy_http.find({"ip": item["ip"]}).count() == 0:
            db.proxy_http.insert(dict(item))

        return item
