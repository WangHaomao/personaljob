# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from scrapy.http import request
from bs4 import BeautifulSoup
from e_commerce_site_crawler.items import ECommerceSiteCrawlerItem

from e_commerce_site_crawler.ecommerce.pageParser.shopping_navigation_parser import get_nav
from e_commerce_site_crawler.ecommerce.pageParser.selenium_batch_parser import \
    get_pageKeyDic_and_searchKeywordKey,get_next_urlList_by_firstpage_url,get_all_page_number,get_all_page_urls
from urllib2 import quote,unquote
import time

"""
1、获取网站首页的导航栏 关键字：url
2、判断是否存在 关键字 in url
如果 关键字 in url:
    那么解析出翻页
        

"""

if __name__ == '__main__':

    # url = "https://www.taobao.com/"
    # url = "http://www.dangdang.com/"

    url = "https://www.jd.com/"
    number, mylist = get_nav(url)
    searchKeywordValue = None
    page_list = []
    pageKeyDic = {}


    for tlist in mylist:
        # pass
        # if (tlist[0] != None and tlist[1] != None and tlist[0] in tlist[1]):
            # searchKeywordValue = quote(tlist[0].encode('utf8'))
            # item_list_url = tlist[1].replace(tlist[0], searchKeywordValue)
            # print(item_list_url)
            # page_list = get_next_urlList_by_firstpage_url(item_list_url)
            # pageKeyDic, searchKeywordKey = get_pageKeyDic_and_searchKeywordKey(page_list, searchKeywordValue)

            # if (searchKeywordKey != "SEARCHKEYERROR"): break
        print ("%s:%s"%(tlist[0],tlist[1]))

    # demo_url0 = page_list[0]
    # demo_url1 = page_list[1]
    #
    # for tlist in mylist:
    #     if (tlist[0] != None and tlist[1] != None):
    #         next_url1 = demo_url0.replace("%s=%s" % (searchKeywordKey, searchKeywordValue),
    #                                       "%s=%s" % (searchKeywordKey, quote(tlist[0].encode('utf8'))))
    #         next_url2 = demo_url1.replace("%s=%s" % (searchKeywordKey, searchKeywordValue),
    #                                       "%s=%s" % (searchKeywordKey, quote(tlist[0].encode('utf8'))))
    #
    #         # print (next_url1)
    #         # print "pagetlist = %s" % page_list
    #         allnumber = get_all_page_number(next_url1)
    #         print ("%s,%s,%s"%(searchKeywordKey,str(searchKeywordValue),str(tlist[0])))
    #         print next_url2
    #         next_all_url_list = get_all_page_urls(pageKeyDic, page_urls=page_list,
    #                                                                        all_page_number=allnumber)
    #         print len(next_all_url_list)
    #         print "-------------------------------------------------------------------------------------------------"
    #         print (time.ctime())
            # for next_url in next_all_url_list:
            #     print (next_url)
                # Request(callback=self.goods_list_parse, url=next_url)