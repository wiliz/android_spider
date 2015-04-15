# -*- coding: utf-8 -*-
import random

from googleplay.settings import pymongo, db, HTTP_AGENT

class RotateHttpAgentMiddleware(object):

    def process_request(self, request, spider):
        #print "1111111111"

        '''
        if spider.name == "googleplay_apk":
            request.meta["proxy"] = HTTP_AGENT
        '''

        if spider.name == "googleplay_apk":
            num = random.randint(1, 200)
            for item in db.proxy_http.find({"deleted": False}).sort("priority", pymongo.DESCENDING).skip(num).limit(1):
                proxy = "http://%s:%s" % (item["ip"], item["port"])
                request.meta["proxy"] = proxy
                request.meta["proxy_id"] = str(item["_id"])
                request.meta["priority"] = int(item.get("priority", 0))

    '''
    def process_response(self, request, response, spider):
        print "2222222222"
        return response
    '''


