#coding:utf-8
import random
import scrapy
from scrapy import log
import time
from scrapy.contrib.downloadermiddleware.httpproxy import HttpProxyMiddleware
# logger = logging.getLogger()

# class ProxyMiddleWare(object):
#     """docstring for ProxyMiddleWare"""
#
#     def process_request(self, request, spider):
#         '''对request对象加上proxy'''
#         proxy = self.get_random_proxy()
#         print("this is request ip:" + proxy)
#         request.meta['proxy'] = proxy
#
#     def process_response(self, request, response, spider):
#         '''对返回的response处理'''
#         # 如果返回的response状态不是200，重新生成当前request对象
#         if response.status != 200:
#             proxy = self.get_random_proxy()
#             print("this is response ip:" + proxy)
#             # 对当前reque加上代理
#             request.meta['proxy'] = proxy
#             return request
#         return response
#
#     def get_random_proxy(self):
#         '''随机从文件中读取proxy'''
#         while 1:
#             with open('proxies.txt', 'r') as f:
#                 proxies = f.readlines()
#                 # print proxies
#             if proxies:
#                 break
#             else:
#                 time.sleep(1)
#         proxy = "http://" + random.choice(proxies).strip()
#         print "now ip:%s"%proxy
#         return proxy
import json
class ProxyMiddleWare(HttpProxyMiddleware):




    ip_pool = []
    def __init__(self,ip=''):
        self.ip = ip
        json_s = '{"ERRORCODE":"0","RESULT":[{"port":"44306","ip":"171.13.36.228"},{"port":"20975","ip":"117.94.204.25"},{"port":"33779","ip":"182.42.44.155"},{"port":"33902","ip":"113.101.137.102"},{"port":"39143","ip":"114.230.127.62"},{"port":"38965","ip":"114.239.3.155"},{"port":"46996","ip":"123.161.154.64"},{"port":"45700","ip":"120.33.247.82"},{"port":"43573","ip":"113.121.41.165"},{"port":"21527","ip":"122.242.92.6"},{"port":"46535","ip":"49.79.58.186"},{"port":"48241","ip":"113.121.47.91"},{"port":"48750","ip":"27.154.183.45"},{"port":"26306","ip":"182.34.20.19"},{"port":"35181","ip":"223.242.177.44"},{"port":"35052","ip":"114.225.84.235"},{"port":"33385","ip":"117.86.20.26"},{"port":"38541","ip":"49.84.70.182"},{"port":"21002","ip":"114.239.1.18"},{"port":"40891","ip":"117.94.207.140"}]}'
        json_parser = json.loads(json_s)
        for ip_dic in json_parser["RESULT"]:
            self.ip_pool.append(ip_dic["ip"] + ":" + ip_dic["port"])

    def process_request(self, request, spider):
        thisip = random.choice(self.ip_pool)

        try:
            request.meta["proxy"] = "http://%s" % thisip

            print "current_ip = %s" % request.meta["proxy"]
        except  Exception as e:
            pass