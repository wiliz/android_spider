# -*- coding: utf-8 -*-

from bson.objectid import ObjectId

from scrapy.exceptions import IgnoreRequest
#from scrapy.contrib.downloadermiddleware.retry import RetryMiddleware

from googleplay.settings import pymongo, db

class DealExceptionMiddleware(object):

    '''
    def process_request(self, request, spider):
        print "3333333333"
    '''

    def process_response(self, request, response, spider):
        #print "4444444444"
        
        if spider.name == "googleplay_apk":
            proxy_id = request.meta["proxy_id"] if request.meta.has_key("proxy_id") else ""
            if response.status == 200:
                self._set_agent_priority(proxy_id)
            else:
                print "LOG: Request Error, code = %s, url = %s" % (response.status, request.url)
                self._set_agent_priority(proxy_id, -1)
                raise IgnoreRequest()

        return response


    def process_exception(self, request, exception, spider):

        #print dir(exception)
        if spider.name == "googleplay_apk":
            osError = exception.osError if hasattr(exception, "osError") else 0
            proxy_id = request.meta["proxy_id"] if request.meta.has_key("proxy_id") else ""
            print "LOG: Exception Occur, osError = %s, message = %s" % (osError, exception.message)
            if osError == 111: #Connection refused
                self._set_agent_priority(proxy_id, -10)
            else:
                self._set_agent_priority(proxy_id, -1)

        raise IgnoreRequest()


    def _set_agent_priority(self, id, num = 1):
        
        try:
            db.proxy_http.update({"_id": ObjectId(id)}, {"$inc": {"priority": num}})
        except:
            pass
        
