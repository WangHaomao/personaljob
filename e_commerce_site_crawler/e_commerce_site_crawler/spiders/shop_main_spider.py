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

class ShopMainSpider(scrapy.Spider):
    name = "shopspider"
    # allowed_domains = ["https://www.baidu.com"]
    start_urls = [
                    'https://www.taobao.com/',
                    # "http://www.dangdang.com/",
                    # "http://www.vip.com/",
                    # "http://www.vancl.com/",
                    # "http://www.yhd.com/",
                    # "https://www.amazon.cn/",
                    # "http://www.meilishuo.com/",
                 ]

    def parse(self, response):
        number, mylist = get_nav(response.url)
        searchKeywordValue = None
        page_list = []
        pageKeyDic = {}

        for tlist in mylist:
            if(tlist[0] != None and tlist[1] != None and tlist[0] in tlist[1]):
                searchKeywordValue = quote(tlist[0].encode('utf8'))
                item_list_url = tlist[1].replace(tlist[0],searchKeywordValue)
                print(item_list_url)
                page_list = get_next_urlList_by_firstpage_url(item_list_url)
                pageKeyDic, searchKeywordKey = get_pageKeyDic_and_searchKeywordKey(page_list, searchKeywordValue)



                if(searchKeywordKey!= "SEARCHKEYERROR"):break


        demo_url0 = page_list[0]
        demo_url1 = page_list[1]



        for tlist in mylist:
            if (tlist[0] != None and tlist[1] != None):
                next_url1 = demo_url0.replace("%s=%s"%(searchKeywordKey,searchKeywordValue),"%s=%s"%(searchKeywordKey,quote(tlist[0].encode('utf8'))))
                next_url2 = demo_url1.replace("%s=%s"%(searchKeywordKey,searchKeywordValue),"%s=%s"%(searchKeywordKey,quote(tlist[0].encode('utf8'))))

                # print (next_url1)
                print "pagetlist = %s" % page_list
                allnumber = get_all_page_number(next_url1)

                next_all_url_list = [next_url1,next_url2]+ get_all_page_urls(pageKeyDic,page_urls=page_list,all_page_number=allnumber)

                for next_url in next_all_url_list:
                    print (next_url)
                    Request(callback=self.goods_list_parse,url=next_url)



            #----------------------------------------------------------------------
            # import ConfigParser
            # from e_commerce_site_crawler.ecommerce.spiderUtils.url_utils import get_url_domain
            # cp = ConfigParser.SafeConfigParser()
            # cp.read("shostruct.txt")
            # domain = get_url_domain(item_list_url)
            # if(cp.has_section(domain) is False):
                # page_list = get_next_urlList_by_firstpage_url(item_list_url)
                # pageKeyDic,searchKeywordKey = get_pageKeyDic_and_searchKeywordKey(page_list,searchKeywordValue)

                "将商品读取信息保存"
                # cp.add_section(domain)
                # cp.set(domain, "pageKeyDic", str(pageKeyDic))
                # cp.set(domain,"searchKeywordKey",searchKeywordKey)
                # cp.set(domain,"demoSKValue",searchKeywordValue)
                # cp.set(domain, "demoPageList", str(page_list))
                # print pageKeyDic
            # else:
            #     pass


        # except:
        #     print ("SHOPSTRUCT ERROR")


    def goods_list_parse(self,response):
        # pass
        item = ECommerceSiteCrawlerItem()
        print  (response.xpath("//a"))

        item['url']  = response.url

        yield item
