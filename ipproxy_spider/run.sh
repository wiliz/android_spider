#!/bin/bash
cd /data0/www/android_spider/ipproxy_spider
PATH=$PATH:/usr/local/bin
export PATH
scrapy crawl ipproxy
