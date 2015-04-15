# Scrapy settings for ipproxy project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'ipproxy'

SPIDER_MODULES = ['ipproxy.spiders']
NEWSPIDER_MODULE = 'ipproxy.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'ipproxy (+http://www.yourdomain.com)'

ITEM_PIPELINES = {
    'ipproxy.pipelines.IpproxyPipeline': 300
}

MONGODB = { 
    'host': '127.0.0.1',
    'port': 27017
}
