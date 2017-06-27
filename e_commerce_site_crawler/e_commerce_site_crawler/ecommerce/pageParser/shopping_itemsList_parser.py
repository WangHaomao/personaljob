# -*- coding:utf-8 _*-
import re
import json
import sys
import pprint
from lxml import etree
from e_commerce_site_crawler.ecommerce.spiderUtils.url_utils import urls_clustering,url_sifter,get_url_domain
from e_commerce_site_crawler.\
    ecommerce.spiderUtils.\
    parser_util \
    import  get_soup_by_request_without_script,\
    get_soup_by_selenium_without_script,\
    get_xpath_doc_by_request_by_html_source,\
    get_soup_by_html_source,get_soup_by_request

reload(sys)
sys.setdefaultencoding('utf-8')

# 判断是否是商品列表的条件
"""
1、是否有足够的图片CONSEQUENT_SIMILAR_TAG_NUMBER个<img>标签
2、数量是否够多，在当前的wrapper中筛选符合条件1的 html数量最长的

后期可以添加筛选条件
"""
def check_is_goods_list(old_html_len,current_tag):
    CONSEQUENT_SIMILAR_TAG_NUMBER = 10
    tag_source = str(current_tag)
    img_len = len(get_soup_by_html_source(tag_source).find_all("img"))
    source_len = len(tag_source)
    if(img_len >= CONSEQUENT_SIMILAR_TAG_NUMBER and old_html_len < source_len):
        return source_len
    return  -1

def is_single_tag(tag):
    inner_tag_number = 0
    for child_tag in tag.children:
        if(child_tag.name != None):
            inner_tag_number +=1
            if(inner_tag_number >= 2):return False

    return True

def analysis_by_tag(goods_list_tag,url):
    detail_url_set = set()
    for each_tag in goods_list_tag.contents:

        if(each_tag.name!=None):

            current_url_list = []
            for inner_tag in each_tag.descendants:

                """
                商品列表页面本身含有一定的信息，此处暂时不做抓取（在商品详细页面抓取）
                
                以下注释信息是对商品信息的抓取
                """
                # if(inner_tag.name!=None and is_single_tag(inner_tag)):
                #     # print inner_tag
                #     tag_text =  inner_tag.text.replace('\n',"")
                #     if(message_len < len(tag_text)):
                #         message_len = len(tag_text)
                #         message = tag_text
                #
                #
                #     if(u'¥' in tag_text):
                #         print tag_text
                #
                #     elif(u'评价' in tag_text or u'评论' in tag_text):
                #         re_comment_res = re.search(u'\d+\+{0,1}人{0,1}评价|\d+\+{0,1}人{0,1}评论|\d+条评论', tag_text)
                #         if re_comment_res !=None:
                #             print re_comment_res.group()

                if(inner_tag.name!=None and inner_tag.name =='a'):
                    try:
                        detail_url =  url_sifter(url=inner_tag['href'],parent_url=url)
                        if('javascript' not in detail_url and 'list' not in detail_url and 'search' not in detail_url
                           and detail_url not in current_url_list):

                            current_url_list_len = len(current_url_list)

                            check_flag = True
                            for i in range(0,current_url_list_len):
                                if(detail_url in current_url_list[i]):
                                    current_url_list[i] = detail_url
                                    check_flag = False
                                    break
                                elif(current_url_list[i] in detail_url):
                                    check_flag = False
                                    break
                            if(check_flag == True):
                                current_url_list.append(detail_url)
                    except:
                        pass
            detail_url_set = detail_url_set | (set(current_url_list))

    res_detail_urls_list = urls_clustering(list(detail_url_set))

    res_max_len = -1
    res_max_list = []
    for i in res_detail_urls_list:
        i_len = len(i)
        if(res_max_len<i_len):
            res_max_len = i_len
            res_max_list = i

    #debug
    pprint.pprint(res_max_list)
    # urls_clustering(res_max_list)
    print len(res_max_list)

    return res_max_list



def get_goods_list_tag_by_soup(soup):
    # 按块查找，找到相似度较高且连续数高于某个值的外围后停止 ，每次选择当前区域内的最复杂区域（此处缩略为字符长最长的）
    # soup = soup = get_soup_by_request_without_script(url)

    has_find_goods_list = False
    max_len_tag = soup.find("body") #初始最大的外围
    goods_tag = max_len_tag
    deep = 0                        #查找深度
    SEARCH_DEEP_LIMIT = 20
    CONSEQUENT_SIMILAR_TAG_NUMBER = 10
    ATTRIBUTES_NUM_LIMIT = 3    #可允许商品中出现的不同class的个数，除了苏宁，一般都是2个以下（taobao 2个，其他（不包含未知） 1个）


    while(has_find_goods_list is False and deep < SEARCH_DEEP_LIMIT):

        max_len = 0
        tmp_max_len_tag = max_len_tag

        for child_tag in max_len_tag.children:
            # 排除不是tag的东西，比如\n，纯字符等等
            if(child_tag.name != None):
                # child_tag_len = len(str(child_tag))
                # if (child_tag_len > max_len):
                current_len =  check_is_goods_list(max_len,child_tag)
                if (current_len!=-1):
                    max_len = current_len
                    tmp_max_len_tag = child_tag

        max_len_tag = tmp_max_len_tag
        # 用来判断是否有多余的属性，初次属性设置为全都一样才算list
        """ 筛选条件：（筛选的缩放宽度）
            版本1：所有的 attributes 都一样
            版本2：允许出现两种以下的attributes
            版本3：将当前已有的 attributes 放入attrs_set内，检测set的长度（有几个attrs_set）
            将所有 attributes 组成一个字符串，比较即可
        """
        #保存当前有几种attributes了
        attrs_set = set()

        """ --------------新增上述一个对象-------------"""
        number_of_effective_children = 0
        tag_list_name = ""

        is_goods_list = True
        # 测试是否符合要求
        for child_tag in max_len_tag.children:

            if(child_tag.name != None):
                # print child_tag.attrs
                tag_attrs = child_tag.attrs
                # 第一次出现的attribute
                current_attrs_str = "".join(tag_attrs.keys())

                if(current_attrs_str not in attrs_set):
                    if(len(attrs_set) >= ATTRIBUTES_NUM_LIMIT):
                        is_goods_list = False
                        break
                    else:
                        attrs_set.add(current_attrs_str)
                    if(is_goods_list is False): break

                number_of_effective_children+=1

        # 同一个中某个标签大于10且服务条件
        if(number_of_effective_children>CONSEQUENT_SIMILAR_TAG_NUMBER and is_goods_list):
            has_find_goods_list = True
            goods_tag = max_len_tag

        deep+=1
    # analysis_by_tag(max_len_tag)
    return max_len_tag

def get_goods_url_from_tag(wrapper_tag):
    goods_url_list = []
    for tag in wrapper_tag:
        if(tag.name != None):
            doc = etree.HTML(str(tag))
            a_list = doc.xpath("//a[@href]/@href")
            # print  a_list[0]
            print (a_list)


"""
解析翻页需要渲染js，交给selenium批量处理
selenium 批量处理将减少大量时间，提高效率
"""
def get_next_page_url(url_list):
    pass



def analysis_json_data(url,soup):
    rank_dic = {}
    def get_json_path(container,json_path):
        # if(rank_dic.has_key(json_path)): rank_dic[json_path] += 1
        # else: rank_dic[json_path] = 1

        if(isinstance(container,dict)):
            # print container
            for key,value in container.items():
                # print ("%s : %s")%(key,value)
                get_json_path(value,json_path+"/"+key)

        elif(isinstance(container,list)):
            # print container
            if (rank_dic.has_key(json_path)):
                rank_dic[json_path] += 1
            else:
                rank_dic[json_path] = 1
            # print json_path
            # return json_path
            for next_container in container:
                # print next_container
                get_json_path(next_container,json_path+"/a_list")

        # else:
            # print container
    # soup = get_soup_by_request(url)
    shop_json = ""
    maxlen = -1
    for y in soup.find_all("script"):
        # print str(y)
        for x in re.findall("\{.*\}",str(y)):
            tmp_len = len(x)
            if (tmp_len > maxlen):
                maxlen = tmp_len
                shop_json = x

    json_praser = json.loads(shop_json)
    get_json_path(json_praser,"")

    second_dic = {}
    max_path_str = ""
    max_path_len = -1
    for key,value in rank_dic.items():
        if value>20 and "a_list" in key:
            # print "(%s,%s)"%(key,value)
            tmp_str = (key).split('a_list')[0]
            if second_dic.has_key(tmp_str):
                second_dic[tmp_str] += 1
            else:
                second_dic[tmp_str] = 1
            if(second_dic[tmp_str] > max_path_len):
                max_path_len = second_dic[tmp_str]
                max_path_str = tmp_str

    print max_path_str
    print len(max_path_str.split('/'))

    def not_empty(s): return s and s.strip()

    json_key_list =  list(filter(not_empty, max_path_str.split('/')))

    json_key_index = 0
    res_dic = json_praser
    while json_key_index < len(json_key_list):
        res_dic = res_dic[json_key_list[json_key_index]]

        json_key_index+=1

    for li in res_dic:
        for key,value in li.items():
            # print "%s:%s"%(key,value)
            if("price" in key):
                print value
            elif("title" in key):
                print value
            elif("detail" in key):
                print value,key
            # try:
            #     print re.search("[0-9]+\.[0-9]+",value).group()
            #     print key
            # except:
            #     # print re.search("[0-9]+\.[0-9]+",value).group()
            #     pass
        print "-------------------"

# 选择最好多测试几遍，影响后续的策略
def debug_script_html_len(url):
    soup = get_soup_by_request(url)

    print len(str(soup.prettify()))
    print "---------------------------------------------"
    for ss in soup.find_all("script"):
        print len(str(ss))
    # 去除所有script脚本文件后的html标签树
    [script.extract() for script in soup.findAll('script')]
    print "---------------------------------------------"
    print len(str(soup.prettify()))

def analysis_method_selector(soup):
    # try:
    #     soup = get_soup_by_request(url)
    # except:
    #
    #     return 'selenium'

    tag_script_list =  soup.find_all('script')
    max_script_len = -1

    for each_script in tag_script_list:
        current_str = str(each_script)
        current_len = len(current_str)
        if(current_len > max_script_len):
            max_script_len = current_len
            max_script_str = current_str
    # 去除所有script脚本文件后的html标签树
    [script.extract() for script in soup.findAll('script')]
    html_without_script_len =  len(str(soup.prettify()))

    if(html_without_script_len < 10000 and max_script_len < 10000 ):
       # or (max(html_without_script_len,max_script_len)*1.0 / min(html_without_script_len,max_script_len) *1.0) <10.0):
        return 'WEBDRIVER'
    # 大了很多
    elif(max_script_len > html_without_script_len):
        return 'JSON'
    else:
        return 'REQUEST'

def analysis_goods_list(method,url,soup):
    if(method == 'WEBDRIVER'):
        pass
    elif(method == 'JSON'):
        analysis_json_data(url,soup)
    else:
        soup = get_soup_by_request(url)
        return analysis_by_tag(get_goods_list_tag_by_soup(soup),url)


if __name__ == '__main__':

    # url = "https://list.jd.com/list.html?cat=1620,1621,1626"
    # url = "https://s.taobao.com/search?initiative_id=tbindexz_20170509&ie=utf8&spm=a21bo.50862.201856-taobao-item.2&sourceId=tb.index&search_type=item&ssid=s5-e&commend=all&imgfile=&q=%E6%89%8B%E6%9C%BA&suggest=0_1&_input_charset=utf-8&wq=shouji&suggest_query=shouji&source=suggest"
    # url = "http://list.mogujie.com/s?q=%E6%89%8B%E6%9C%BA%E5%A3%B3%E8%8B%B9%E6%9E%9C6&from=querytip0&ptp=1._mf1_1239_15261.0.0.5u1T9Y"
    # url = "http://search.dangdang.com/?key=%CA%E9"
    # url = "http://search.suning.com/%E6%89%8B%E6%9C%BA/"
    #
    url = "http://search.yhd.com/c0-0/k%25E9%259B%25B6%25E9%25A3%259F/?tp=1.1.12.0.3.Ljm`JdW-10-4v5ud"
    # url = "http://www.meilishuo.com/search/goods/?page=1&searchKey=%E8%A3%99%E5%AD%90%E5%A4%8F&acm=3.mce.1_4_.17721.33742-33692.3Va85qjefPdEZ.mid_17721-lc_201"
    # url = "http://search.gome.com.cn/search?question=%E6%89%8B%E6%9C%BA"
    # url = "http://search.jumei.com/?referer=yiqifa_cps__ODg5MjEzfDAwczliN2JmZGVjN2EzOWQ2M2I5"
    # url = "https://www.vmall.com/search?keyword=%E6%89%8B%E6%9C%BA"

    # soup = get_soup_by_selenium_without_script(url)
    # soup = get_soup_by_request_without_script(url)
    # 已经获得
    # goods_list_tag = get_goods_list_tag_from_soup(soup)
    # goods_list_method_selector(url)

    # url = "https://list.jd.com/list.html?cat=1713,4855,4859"
    url = "https://s.taobao.com/list?q=%E6%8B%BE%E8%B4%A7"

    soup = get_soup_by_request("https://s.taobao.com/list?q=%E6%8B%BE%E8%B4%A7")
    print analysis_method_selector(soup)

    # goods_list_tag = analysis_by_tag(get_goods_list_tag_by_soup(get_soup_by_request(url)),url)

    # debug_script_html_len(url)
    '''
        暂时不考虑没attribute的标签
    '''
    # print goods_list_tag
    # print goods_list_tag.name
    # print goods_list_tag.attrs
    #
    # tag_name = goods_list_tag.name
    # attrs_dic =  goods_list_tag.attrs


    # print soup.find_all(tag_name,attrs=attrs_dic)

    # for x in goods_list_tag:
    #     print x

    # get_goods_url_from_tag(goods_list_tag)

    # url = 'https://s.taobao.com/list?q=%E8%B4%9D%E5%8F%B8'
    # analysis_json_data(url)