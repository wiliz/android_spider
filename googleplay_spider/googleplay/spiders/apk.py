# -*- conding: utf-8 -*-
import os, re, random, json
import signal
import datetime, time
import urllib, urllib2
import socket, cookielib

from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.http import Request, FormRequest

from googleplay.utils import funs 

from googleplay.settings import DOWNLOAD_APK_PATH, CACHE_DIR
from googleplay.settings import pymongo, db

cache_file = "%s/apk-downloader.tmp" % CACHE_DIR 

class ApkSpider(Spider):

    name = "googleplay_apk"
    download_delay = 1
    allowed_domains = ["evozi.com"]
    start_urls = []

    def start_requests(self):

        exp_data = self._get_exp_data()
         
        url = "http://api.evozi.com/apk-downloader/download"

        skip_num = random.randint(0, 100)
        if db.spider_appid_indonesia.find({"is_download_apk": False}).count() <= skip_num:
            skip_num = 0

        for item in db.spider_appid.find({"is_download_apk": False}).skip(skip_num).limit(30):
            post_data = {
                    "packagename": item["appid"],
                    exp_data["key"]: exp_data["value"],
                    "t": exp_data["t"],
                    "fetch": "false"
                }
            yield FormRequest(url, meta = {"appid": item["appid"]}, formdata = post_data)
            #break


    def parse(self, response):

        print "\nLOG: appid = %s, http_agent = %s, priority = %s" % \
            (response.meta.get("appid"), response.meta.get("proxy", ""), response.meta.get("priority", ""))

        appid = response.meta["appid"]
        res = json.loads(response.body)

        if res["status"] == "success":
            print "LOG: version = %s, size = %s, url = %s" % (res["version"], res["filesize"], res["url"])
            path_info = self._create_apk_path(appid, res["version"])

            if path_info["status"]:
                print "LOG: Begin Download, it will take several minute, please waiting ..."

                if path_info["message"].startswith("File existed"):
                    download_info = {
                        "status": True,
                        "cost_time": -1,
                    }
                else:
                    download_info = funs.download_file(res["url"], path_info["abs_path"])

                if download_info["status"]:
                    print "LOG: Download Completed, cost_time = %s seconds, path = %s" % (download_info["cost_time"], path_info["rel_path"])
                    db.spider_appid.update({"appid": appid}, {"$set": {
                        "local_apk": path_info["rel_path"],
                        "is_download_apk": True,
                        "remote_version": res["version"],
                        "remote_filesize": res["filesize"],
                        "remote_md5": res["md5"]
                    }})
                else:
                    print "LOG: Download Error, message = %s" % download_info["message"]
            else:
                print "LOG: Create Apk Path Error, message = %s" % path_info["message"]

        elif res["status"] == "error":
            print "LOG: Error Message = %s" % res["data"]
            if res["data"].startswith("Invalid or Expired Token"):
                print "LOG: Kill the spider progress"
                self._get_exp_data(True)
                os.kill(os.getpid(), signal.SIGKILL)
            elif res["data"].startswith("Rate limit exceeded"):
                print "LOG: Sleeping 120 second ..."
                time.sleep(120)
                print "LOG: Kill the spider progress"
                os.kill(os.getpid(), signal.SIGKILL)


    def _get_exp_data(self, no_cache = False):

        if no_cache is False and os.path.exists(cache_file):
            file = open(cache_file, "r")
            data = file.readline()
            file.close()
            result = json.loads(data)
        else:
            print "LOG: Getting new exp data"
            url = 'http://apps.evozi.com/apk-downloader/'
            socket.setdefaulttimeout(20)
            cookie_support = urllib2.HTTPCookieProcessor(cookielib.CookieJar())
            self.opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)
            urllib2.install_opener(self.opener)
            
            user_agents = [
                'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
                'Opera/9.25 (Windows NT 5.1; U; en)',
                'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
                'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
                'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
                'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9',
                "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7",
                "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0 ",
            ]
            agent = random.choice(user_agents)
            self.opener.addheaders = [("User-agent", agent), ("Accept", "*/*"), ('Referer', 'http://www.google.com')]

            str_html = self.opener.open(url).read()

            '''
            matchObj = re.search(r'var packageguide = .+?;\s*var .+? = \'(.+?)\';.*var evoziData = {packagename: packagename, (.+?):.*t: (.+?),.*}', str_html, re.S)
            result = {
                "value": matchObj.group(1),
                "key": matchObj.group(2),
                "t": matchObj.group(3)
            }
            '''
            
            matchObj = re.search(r'var evoziData = {packagename: packagename, (.+?): (.+?), t: (.+?),.*}', str_html, re.S)
            key = matchObj.group(1)
            value = matchObj.group(2)
            t = matchObj.group(3)
            
            matchObj = re.search(r"var %s = '(.+?)'" % value, str_html, re.S)
            value = matchObj.group(1)

            result = {}
            if matchObj:
                result['value'] = value
                result['key'] = key
                result['t'] = t

            file = open(cache_file, "w")
            file.write(json.dumps(result))
            file.close()

        return result


    def _create_apk_path(self, appid, version):

        result = {
            "status": False,
            "message": "",
            "abs_path": "",
            "rel_path": "",
        }

        if version is None:
            result["message"] = "Version is None"
            return result

        filename = appid + "#" + version + ".apk"
        res = funs.file_encrypt_sha1(filename)
        abs_path = os.path.join(DOWNLOAD_APK_PATH, res["path"])
        abs_dir = os.path.join(DOWNLOAD_APK_PATH, res["dir"])

        try:
            if not os.path.exists(abs_dir):
                os.makedirs(abs_dir)

            if os.path.exists(abs_path):
                result["message"] = "File existed, path = %s" % abs_path

            result["abs_path"] = abs_path
            result["rel_path"] = res["path"]
            result["status"] = True
        except Exception as e:
            result["message"] = e

        return result




