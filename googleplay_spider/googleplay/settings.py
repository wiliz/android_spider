# Scrapy settings for googleplay project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

import os

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
CACHE_DIR = os.path.join(PROJECT_DIR, "caches")
LOG_FILE = os.path.join(PROJECT_DIR, "logs/scrapy.log")

DOWNLOAD_PATH = os.path.join(PROJECT_DIR, "downloads")
DOWNLOAD_APK_PATH = os.path.join(PROJECT_DIR, "downloads/apks")
DOWNLOAD_IMG_PATH = os.path.join(PROJECT_DIR, "downloads/images")

BOT_NAME = 'googleplay'

SPIDER_MODULES = ['googleplay.spiders']
NEWSPIDER_MODULE = 'googleplay.spiders'

#REDIRECT_ENABLED = False
RETRY_ENABLED = False
COOKIES_ENABLED = False

#DOWNLOAD_DELAY = 1
#DOWNLOAD_TIMEOUT = 10
DOWNLOAD_TIMEOUT = 300

DOWNLOADER_MIDDLEWARES = {
    'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': None,
    'googleplay.middlewares.base_useragent.RotateUserAgentMiddleware': 100,
    'googleplay.middlewares.rotate_httpagent.RotateHttpAgentMiddleware': 200,
    'googleplay.middlewares.base_exception.DealExceptionMiddleware': 900,
}

HTTP_AGENT = "http://111.161.126.88:8080"

#MONGODB_HOST = "127.0.0.1"
MONGODB_HOST = "54.255.213.40"
MONGODB_PORT = 27017

MONGODB_HOST_APPCENTER = "54.255.213.40"
MONGODB_PORT_APPCENTER = 27017

import pymongo
db = pymongo.MongoClient(MONGODB_HOST, MONGODB_PORT).android_spider
db_app_th = pymongo.MongoClient(MONGODB_HOST_APPCENTER, MONGODB_PORT_APPCENTER).android_appcenter
db_app_id = pymongo.MongoClient(MONGODB_HOST_APPCENTER, MONGODB_PORT_APPCENTER).android_appcenter_id


