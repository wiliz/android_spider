# -*- coding: utf-8 -*-
import sys, os, copy
import re
import datetime, time

reload(sys)
sys.setdefaultencoding("utf-8")

from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.http import Request, FormRequest

from googleplay.utils import funs

from googleplay.settings import DOWNLOAD_IMG_PATH
from googleplay.settings import pymongo, db, db_app_id

class AppidSpider(Spider):

    name = "googleplay_appid_xls"
    allowed_domains = ["play.google.com"]
    start_urls = []

    collection = db.spider_appid_crawl_0805
    collection_app = db_app_id.AppBase

    # Excel Config
    filename = "/data0/www/android_spider/googleplay_spider/googleplay/caches/DESCRIPTION_TRANSLATION_Main_Source_20140804.xls"
    excel_sheet_index = 0
    excel_start_row_index = 1
    custum_field = {  # key: db field, value: excel colum index (begin 0)
        #"name": 1,
        #"description": 2,
        "name": 3 ,
        "description": 6,
    }

    def start_requests(self):

        res = funs.get_excel_data(self.filename, sheet_index = self.excel_sheet_index, start_row_index = self.excel_start_row_index)

        if res["status"]:
            create_time = datetime.datetime.now()
            row_num = self.excel_start_row_index

            for item in res["data"]:
                row_num += 1
                appid = item[2]

                if appid.strip() == "":
                    print"LOG: Row %d, appid is empty" % row_num
                    continue

                item_override = {}
                for key, val in self.custum_field.items():
                    item_override[key] = item[val]

                url = "https://play.google.com/store/apps/details?id=%s&hl=en" % appid
                item_data = {
                    "appid": appid,
                    "is_download_apk": False,
                    "is_download_img": False,
                    "source": "crawler",
                    "channel": "googleplay",
                    "create_time": create_time,
                    "detail_url": url,
                    "remark": "excel,spider",
                }
                
                yield Request(url = url, meta = {"item_data": item_data, "item_override": item_override, "row_num": row_num}, dont_filter = True) 
                #break
        else:
            print "LOG: Get Excel Data Fail, message = %s" % res["message"]
        

    def parse(self, response):

        item = response.meta["item_data"]
        item_override = response.meta["item_override"]
        row_num = response.meta["row_num"]

        items = []

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

        for key, val in item_override.items():
            item[key] = val

        #print item

        if self.collection_app.find({"appid": item["appid"], "version": item["version"]}).limit(1).count():
            tmp_data = copy.deepcopy(item)

            item = {}
            item["appid"] = tmp_data["appid"]
            item["version"] = tmp_data["version"]
            item["category_id"] = tmp_data["category_id"]
            item["create_time"] = tmp_data["create_time"]
            item["is_download_img"] = True
            item["is_download_apk"] = True

            for key, val in item_override.items():
                item[key] = val

        #item["order"] = 10000 - row_num

        if self.collection.find({"appid": item["appid"], "version": item["version"]}).limit(1).count() == 0:
            print "LOG: Data Insert into DB, create_time = %s, category_id= %s, appid = %s, version = %s" % \
                (item["create_time"].strftime("%Y-%m-%d %H:%M:%S"), item["category_id"], item["appid"], item["version"])
            self.collection.insert(item)
        else:
            print "LOG: Data had already in DB, appid = %s, version = %s" % (item["appid"], item["version"])
            '''Used to update some field value
            self.collection.update({"appid": item["appid"], "version": item["version"]}, {"$set": {
                "name": item["name"],
                "description": item["description"],
            }})
            '''

        # Download image
        if item.has_key("icon"):
            self._download_image(item)

        return items


    def _download_image(self, item):

        print "LOG: Begin Download, appid = %s, version = %s" % (item["appid"], item["version"])

        data = {
            "local_icon": "",
            "local_screenshot": [],
        }

        # icon
        filename = "icon#" + item["appid"] + "#" + item["version"] + ".png"
        res = self._do_download_image(item["icon"], filename)
        if res["status"]:
            data["local_icon"] = res["data"]["rel_path"]
        else:
            print "LOG: Download Img Fail, message = %s" % res["message"]

        # screenshot
        num = 1
        for url in item["screenshot"]:
            filename = str(num) + "#" + item["appid"] + "#" + item["version"] + ".png"
            res = self._do_download_image(url, filename)
            num += 1
            if res["status"]:
                data["local_screenshot"].append(res["data"]["rel_path"])
            else:
                print "LOG: Download Screenshot Fail, message = %s" % res["message"]

        if res["status"]:
            data["is_download_img"] = True
            self.collection.update({"appid": item["appid"], "version": item["version"]}, {"$set": data})


    def _do_download_image(self, download_url, filename):
        
        res = funs.file_encrypt_sha1(filename)
        rel_path = res["path"]
        abs_path = os.path.join(DOWNLOAD_IMG_PATH, rel_path)
        abs_dir = os.path.join(DOWNLOAD_IMG_PATH, res["dir"])

        result = {
            "status": False,
            "message": "",
            "data": {
                "rel_path": rel_path,
                "abs_path": abs_path,
            },
        }

        try:
            if not os.path.exists(abs_dir):
                os.makedirs(abs_dir)

            if os.path.exists(abs_path):
                result["status"] = True
                result["message"] = "File existed, path = %s" % abs_path
            else:
                res = funs.download_file(download_url, abs_path)
                if res["status"]:
                    res = funs.resize_image(abs_path, abs_path, 0.5)
                result["status"] = res["status"]
                result["message"] = res["message"]
        except Exception as e:
            result["message"] = e

        return result



