# -*- coding: utf-8 -*-
import os
import datetime, time

from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.http import Request, FormRequest

from googleplay.utils import funs

from googleplay.settings import DOWNLOAD_IMG_PATH
from googleplay.settings import pymongo, db

class ImgSpider(Spider):

    name = "googleplay_img"
    allowed_domains = ["play.google.com"]
    start_urls = ["https://play.google.com/store"]

    def parse(self, response):

        for item in db.spider_appid.find({"is_download_img": False}):
            print "LOG: Begin Download, appid = %s, version = %s" % (item["appid"], item["version"])

            data = {
                "local_icon": "",
                "local_screenshot": [],
            }

            # icon
            filename = "icon#" + item["appid"] + "#" + item["version"] + ".png"
            res = self._download_and_save_img(item["icon"], filename)
            if res["status"]:
                data["local_icon"] = res["data"]["rel_path"]
            else:
                print "LOG: Download Img Fail, message = %s" % res["message"]
                continue

            # screenshot
            num = 1
            for url in item["screenshot"]:
                filename = str(num) + "#" + item["appid"] + "#" + item["version"] + ".png"
                res = self._download_and_save_img(url, filename)
                num += 1
                if res["status"]:
                    data["local_screenshot"].append(res["data"]["rel_path"])
                else:
                    print "LOG: Download Screenshot Fail, message = %s" % res["message"]
                    #break

            if res["status"]:
                data["is_download_img"] = True
                db.spider_appid.update({"_id": item["_id"]}, {"$set": data})
            #break


    def _download_and_save_img(self, download_url, filename):
        
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






