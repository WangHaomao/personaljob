# -*-encoding:utf-8 -*-
from bs4 import BeautifulSoup
import requests
import re
from lxml import etree
from selenium import webdriver
from e_commerce_site_crawler.ecommerce.spiderUtils.parser_util import get_soup_by_request,get_soup_by_selenium,get_webdriver
from e_commerce_site_crawler.ecommerce.spiderUtils.url_utils import url_sifter
import sys
from lxml.html import fromstring
reload(sys)
sys.setdefaultencoding('utf8')

def _get_price_in_script(soup):
    # print soup.prettify()
    script_list = soup.find_all('script')
    re_str = '"price\w*":"\d+\.\d{1,3}"'
    re_digit_str = "\d+\.\d{1,3}"
    for each_script in script_list:
        res = re.search(re_str,str(each_script))
        if(res!=None):
            # print res.group()
            return re.search(re_digit_str,res.group()).group()


def _get_price_by_class(soup,class_name):
    res_price_list = []
    reg_without_keyword = "\d+\.\d{1,3}"

    tag_symbol_list = soup.find_all(True, class_=re.compile(class_name))
    for tag in tag_symbol_list:
        tag_tmp = tag
        price_text_list = []
        attemps = 0
        while (len(price_text_list) == 0 and attemps < 2):
            price_text_list = re.findall(reg_without_keyword, tag_tmp.text)
            tag_tmp = tag_tmp.parent
            attemps += 1

        print res_price_list
        if (len(price_text_list) != 0):
            res_price_list = res_price_list + price_text_list

    return res_price_list

def _get_price_by_keyword(soup,keyword):
    res_price_list = []
    reg_with_keyword = u"%s\s*\d+\.*\d{1,3}"%keyword

    reg_digit_keyword = u"\d+\.\d{1,3}" #从带有关键字的字符串中提取价格（数字），例如促销价 100,则提取出100


    ttt = u'%s'%keyword
    tag_symbol_list = soup.find_all(True, text=re.compile(ttt))



    for tag in tag_symbol_list:
        tag_tmp= tag
        price_text_list = []
        attemps = 0
        for s_tag in tag.parent.contents:
            # print (s_tag)
            try:
                one_price =  re.search(reg_digit_keyword,str(s_tag)).group()
                res_price_list.append(one_price)
            except:
                print "shopping_detail_parser.py  error"
        # while(len(price_text_list) ==0 and attemps < 2):
        #     price_text_list = re.findall(reg_with_keyword,tag_tmp.text)
        #     tag_tmp = tag_tmp.parent
        #     attemps += 1
        #
        # print res_price_list
        # if(len(price_text_list)!=0):
        #     res_price_list  = res_price_list + re.findall(reg_digit_keyword,"".join(price_text_list))
        # break

    price_dic = {}
    max_appear_price = "-1"
    max_appear_price_num = -1

    for each_price in res_price_list:
        if (price_dic.has_key(each_price)):
            price_dic[each_price] += 1
        else:
            price_dic[each_price] = 1
        if (price_dic[each_price] > max_appear_price_num):
            max_appear_price_num = price_dic[each_price]
            max_appear_price = each_price

    print max_appear_price
    return max_appear_price

def _get_store_by_key(soup,keyword):
    res_comment_degree_list = []
    reg_with_keyword = u"%s" % keyword

    tag_symbol_list = soup.find_all("a", text=re.compile(keyword))
    res_list = []
    for tag in tag_symbol_list:
        try:
            res_list.append(tag['href'])
            print len(tag.parent.parent.parent.contents)

            for dd in  tag.parent.parent.parent.parent.contents:
                if dd.name !=None:
                    store_m =  (dd.text.replace(" ",""))
                    for iii in store_m.split('\n'):
                        if(iii ==''):continue
                        print iii
                    # break
                    print ""
        except:
            pass

    if(len(res_list) > 0) :
        print res_list[0]
        return res_list[0]

    return None
    #     print res_price_list
    #     if (len(price_text_list) != 0):
    #         res_price_list = res_price_list + re.findall(reg_without_keyword, "".join(price_text_list))
    #
    # return res_price_list
def get_price(soup):
    # soup = get_soup_by_request(url)
    # print soup.prettify()
    price_keys = [u"¥",u"促销价",u"价格",u"价"]
    for keyword in price_keys:
        res = _get_price_by_keyword(soup, keyword)
        if(res !=None and res !=[] and res != "-1"):
            # print res
            return res


    res_price_list = _get_price_by_class(soup, "price.*")
    if (len(res_price_list) != 0):
        return res_price_list

    _get_price_in_script(soup)

    res = _get_price_in_script(soup)
    print res
# def _get_comments_by_keyword(soup,keyword):


def get_comments(soup):



    # req = requests.get(url)
    # req.encoding = "utf-8"
    # doc = etree.HTML(driver.page_source)
    key = u"评论"
    # print  doc.xpath("//*[text()='%s']"%(key))
    driver = get_webdriver()
    driver.get(url)
    # soup = BeautifulSoup(driver.page_source,'lxml')
    # print driver.page_source
    # print soup.prettify()
    # for y in soup.find_all(True,text=re.compile(key)):
    #     for x in y.parent.parent.children:
    #         print x
    # driver = get_webdriver(url)
    # driver.get(url)
    xxx = driver.find_element_by_xpath('//*[contains(text(),"%s")]' % key)

    print  xxx.text
    # print  xxx.tag
    driver.close()



def get_store(soup,url):

    soup = get_soup_by_request(url)

    store_keys = [u'旗舰店',u'进入店',u'店铺',u'进店',u'店']
    for keyword in store_keys:
        res_url = _get_store_by_key(soup, keyword)
        if(res_url !=None and res_url !=[]):
            test_url =  url_sifter(url,res_url)
            print get_soup_by_request(test_url).find('title').text
            return url_sifter(url,res_url)


def get_title(url):
    soup = get_soup_by_request(url)
    tag_script = soup.find("title")
    print tag_script.text

def get_comment_degree(url):
    key = u"好评"


def shopping_item_parser(url):

    # soup = get_soup_by_request(url)
    soup = get_soup_by_selenium(url)
    # [script.extract() for script in soup.findAll('script')]
    # print soup.prettify()
    # 价格
    get_price(url)



if __name__ == '__main__':
    url = "https://detail.tmall.com/item.htm?spm=a230r.1.14.14.AT6RIa&id=544429684821&cm_id=140105335569ed55e27b&abbucket=20"
    # url = "https://item.taobao.com/item.htm?spm=a230r.1.14.97.oI9e6K&id=545728190154&ns=1&abbucket=20#detail"
    # url = "https://item.jd.com/11225370508.html"
    # url = "http://item.meilishuo.com/detail/1kaosga?acm=3.ms.2_4_1kaosga.0.24476-25176.94mOaqibAUDJd.t_0-lc_3&ptp=1.9Hyayb.classsearch_mls_1kaosga_2017%E6%96%B0%E6%AC%BE%E6%AC%A2%E4%B9%90%E9%A2%82%E7%8E%8B%E5%AD%90%E6%96%87%E6%9B%B2%E7%AD%B1%E7%BB%A1%E5%90%8C%E6%AC%BE%E5%8C%85%E6%97%B6%E5%B0%9A%E5%B0%8F%E6%96%B9%E5%8C%85%E5%8D%95%E8%82%A9%E6%96%9C%E6%8C%8E%E5%B0%8F%E5%8C%85%E5%8C%85_10057053_pop.1.mNWwi"
    # url = "http://shop.mogujie.com/detail/18jws1w?acm=3.ms.1_4_18jws1w.43.1185-22922.wGTRPqnDRVaKO.t_0-lc_4&ptp=1.eW5XD._b_4bce2add492e4c56_2.1.DijfM"
    # get_comments(url)
    # get_price(url)
    get_store(url)
    # get_title(url)