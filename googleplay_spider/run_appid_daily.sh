#!/bin/bash
cd /data0/www/android_spider/googleplay_spider
PATH=$PATH:/usr/local/bin
export PATH
scrapy crawl googleplay_appid_daily
