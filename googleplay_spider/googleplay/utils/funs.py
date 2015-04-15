# -*- coding: utf-8 -*-
import os
#import Image
from PIL import Image
import random
import hashlib
import datetime, time
import urllib, urllib2
import socket, cookielib
import xlrd

def download_file(url, des_path, timeout = 10):

    begin_time = time.time()
    result = {
        "status": False,
        "message": "",
        "cost_time": -1,
    }

    user_agents = [
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.60 Safari/537.17',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1309.0 Safari/537.17',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.2; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0)',
        'Mozilla/5.0 (Windows; U; MSIE 7.0; Windows NT 6.0; en-US)',
        'Mozilla/5.0 (Windows; U; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 2.0.50727)',
        'Mozilla/6.0 (Windows NT 6.2; WOW64; rv:16.0.1) Gecko/20121011 Firefox/16.0.1',
        'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:15.0) Gecko/20100101 Firefox/15.0.1',
        'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:15.0) Gecko/20120910144328 Firefox/15.0.2',
        'Mozilla/5.0 (Windows; U; Windows NT 6.1; rv:2.2) Gecko/20110201',
        'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9a3pre) Gecko/20070330',
        'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2.13; ) Gecko/20101203',
        'Mozilla/5.0 (Windows; U; Win 9x 4.90; SG; rv:1.9.2.4) Gecko/20101104 Netscape/9.1.0285',
        'Mozilla/5.0 (Macintosh; U; PPC Mac OS X Mach-O; en-US; rv:1.8.1.7pre) Gecko/20070815 Firefox/2.0.0.6 Navigator/9.0b3',
        'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.12) Gecko/20080219 Firefox/2.0.0.12 Navigator/9.0.0.6',
    ]

    headers = {
        "User-Agent": random.choice(user_agents)
    }

    try:
        req = urllib2.Request(url, headers = headers)  
        data = urllib2.urlopen(req, timeout = timeout).read()
        f = file(des_path, "wb")
        f.write(data)
        f.close()
        result["status"] = True
    except Exception as e:
        result["message"] = e

    end_time = time.time()
    result["cost_time"] = round(end_time - begin_time, 2)

    return result


def download_file_socket(url, des_path, timeout = 10):

    begin_time = time.time()
    result = {
        "status": False,
        "message": "",
        "cost_time": -1,
    }

    socket.setdefaulttimeout(timeout)
    cookie_support = urllib2.HTTPCookieProcessor(cookielib.CookieJar())
    opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)
    urllib2.install_opener(opener)

    user_agents = [
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.60 Safari/537.17',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1309.0 Safari/537.17',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.2; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0)',
        'Mozilla/5.0 (Windows; U; MSIE 7.0; Windows NT 6.0; en-US)',
        'Mozilla/5.0 (Windows; U; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 2.0.50727)',
        'Mozilla/6.0 (Windows NT 6.2; WOW64; rv:16.0.1) Gecko/20121011 Firefox/16.0.1',
        'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:15.0) Gecko/20100101 Firefox/15.0.1',
        'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:15.0) Gecko/20120910144328 Firefox/15.0.2',
        'Mozilla/5.0 (Windows; U; Windows NT 6.1; rv:2.2) Gecko/20110201',
        'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9a3pre) Gecko/20070330',
        'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2.13; ) Gecko/20101203',
        'Mozilla/5.0 (Windows; U; Win 9x 4.90; SG; rv:1.9.2.4) Gecko/20101104 Netscape/9.1.0285',
        'Mozilla/5.0 (Macintosh; U; PPC Mac OS X Mach-O; en-US; rv:1.8.1.7pre) Gecko/20070815 Firefox/2.0.0.6 Navigator/9.0b3',
        'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.12) Gecko/20080219 Firefox/2.0.0.12 Navigator/9.0.0.6',
    ]
    
    try:
        agent = random.choice(user_agents)
        opener.addheaders = [("User-agent", agent), ("Accept", "*/*"), ('Referer', 'http://www.google.com')]
        data = opener.open(url).read()
        f = file(des_path, "wb")
        f.write(data)
        f.close()
        result["status"] = True
    except Exception as e:
        result["message"] = e

    end_time = time.time()
    result["cost_time"] = round(end_time - begin_time, 2)

    return result


def file_encrypt_sha1(filename):

    """give a filename like `image.jpg`, return the folder and filename encrypted
    eg: ab/cd/ef/gh/helloworlddkfdkjfkldjflk.jpg
    """
    n = 2 
    name, ext = os.path.splitext(filename)
    m = hashlib.sha1()
    m.update(name)
    line = m.hexdigest()
    first, second, third, last = [line[i:i+n] for i in range(0, len(line), n) if i < 8]
    cut_dir = os.path.join(first, second, third, last).replace("\\", "/")
    cut_name = line[8:] + ext
    result = {
        "path": os.path.join(cut_dir, cut_name),
        "dir": cut_dir,
        "name": cut_name,
    }

    return result


def resize_image(src_filename, dest_filename, ratio = 0.5):

    result = {
        "status": False,
        "message": "",
        "data": "",
    }

    try:
        src_img = Image.open(src_filename)
        width = int(src_img.size[0] * ratio)
        height = int(src_img.size[1] * ratio)
        dest_img = src_img.resize((width, height), Image.BILINEAR)
        dest_img.save(dest_filename)
        result["status"] = True
    except Exception as e:
        result["message"] = e

    return result


def get_excel_data(filename, sheet_index = 0, start_row_index = 0):

    result = {
        "status": False,
        "message": "",
        "data": [],
    }

    try:
        data = xlrd.open_workbook(filename)
        table = data.sheets()[sheet_index]

        for i in range(start_row_index, table.nrows):
            result["data"].append(table.row_values(i))

        result["status"] = True
    except Exception as e:
        result["message"] = e


    return result
