# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from scrapy.http import request
from bs4 import BeautifulSoup
from e_commerce_site_crawler.items import ECommerceSiteCrawlerItem

from e_commerce_site_crawler.ecommerce.pageParser.shopping_navigation_parser import get_nav
from e_commerce_site_crawler.ecommerce.pageParser.selenium_batch_parser import \
    get_pageKeyDic,get_next_urlList_by_firstpage_url,get_all_page_number,get_all_page_urls
from e_commerce_site_crawler.ecommerce.spiderUtils.parser_util import get_html_with_request
from urllib2 import quote,unquote
import time

"""
1、获取网站首页的导航栏 关键字：url
2、判断是否存在 关键字 in url
如果 关键字 in url:
    那么解析出翻页
        

"""

if __name__ == '__main__':

    url = "https://www.taobao.com/"
    # url = "http://www.dangdang.com/"
    # url = "https://www.jd.com/"

    number, mylist = get_nav(url,0)
    searchKeywordValue = None
    page_list = []
    pageKeyDic = {}

    # 第一遍遍历
    goal_url = ""
    goal_key = ""
    goal_url_len = -1
    all_meets_url_number = 0 #统计有多少个关键字在url中
    for tlist in mylist:
        # pass
        o_url = tlist[1]
        o_key = tlist[0]
        if ((o_key != None and o_url != None and o_key in o_url)
            and ("search" in o_url or 'list' in o_url)):
            if goal_url_len == -1 or len(tlist[1]) < goal_url_len:
                goal_url = tlist[1]
                goal_key = tlist[0]
                goal_url_len = len(tlist[1])

            all_meets_url_number+=1
    print goal_url

    res_url_list = []
    if(goal_url != -1):
        """
            对url进行一遍简化
        """
        goal_url_spilted = goal_url.split('&')
        key_index = 0
        simple_url = ""
        # print goal_url_spilted
        while key_index < len(goal_url_spilted):
            if(goal_key in goal_url_spilted[key_index]):
                # [:]左闭右开
                simple_url = ('&'.join(goal_url_spilted[:key_index+1]))

                key_index += 1
                break
            key_index+=1

        original_html_len = len(get_html_with_request(goal_url))

        while (key_index<len(goal_url_spilted)):
            if (original_html_len <= len(get_html_with_request(simple_url))):
                break
            simple_url = simple_url + "&" + goal_url_spilted[key_index]
            key_index+=1
        for tlist in mylist:
            if tlist[0] != None and tlist[0] != '':
                searchKeywordValue = quote(tlist[0].encode('utf8'))
                item_list_url = simple_url.replace(goal_key, searchKeywordValue)
                # print item_list_url
                res_url_list.append(item_list_url)
    else:
        # 假设所有url类型都相同，且默认为商品列表页面，进行解析
        for tlist in mylist:
            # print item_list_url
            if tlist[1]!= None and tlist[1]!='':
                res_url_list.append(tlist[1])




    if(len(res_url_list)>1):

        test_url = res_url_list[0]

        page_list = get_next_urlList_by_firstpage_url(test_url)
        pageDict = get_pageKeyDic(page_list)

        print pageDict

        print page_list

        attached_1 = page_list[1].replace(test_url, '')
        attached_2 = page_list[2].replace(test_url, '')


        for goods_list_url in res_url_list:
            next_url1 =  goods_list_url + attached_1
            next_url2 =  goods_list_url + attached_2

            # print next_url2
            allnumber = get_all_page_number(goods_list_url)
            print allnumber
            # next_all_url_list = get_all_page_urls(pageKeyDic,page_list,allnumber)

            res = get_all_page_urls(pageDict, [u'https://s.taobao.com/list?q=%E7%BE%BD%E7%BB%92%E6%9C%8D',
                                                        u'https://s.taobao.com/list?q=%E7%BE%BD%E7%BB%92%E6%9C%8D&bcoffset=12&s=60',
                                                        u'https://s.taobao.com/list?q=%E7%BE%BD%E7%BB%92%E6%9C%8D&bcoffset=12&s=120'],
                                    allnumber)
            for x in res:
                print str(x)
            print "----------$$$$$$$$$------------"
