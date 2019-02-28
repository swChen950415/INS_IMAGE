import json
import random
import time
import requests
import urllib.parse
import pymongo
import re
import sys
from lxml import etree
from fake_useragent import UserAgent





def parse_first_page(user_name):
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        # 'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        # 'Content-Type':'application/x-www-form-urlencoded',
        'Host': 'www.veryins.com',
        'Pragma': 'no-cache',
        'Cookie': _cookie,
        # 'Upgrade - Insecure - Requests': '1',
        'User-Agent': random.choice(uas)
    }
    url = ins_url + user_name

    #更新html
    res = requests.get(url,headers)

    try :
        if res.status_code == 200:
            html_res = etree.HTML(res.text)



            next_cursor = str(html_res.xpath('//*[@id="list"]/@next-cursor')[0])
            print(user_name)
            if re.search('.*?(tag).*?',user_name) == None :
                user_id = int(html_res.xpath('//*[@id="username"]/@data-uid')[0])
                rg = str(html_res.xpath('//*[@id="list"]/@data-rg')[0])
                print(rg,user_id)
                cookie = res.cookies.keys()[0]+'='+res.cookies.values()[0]+';'+res.cookies.keys()[1]+res.cookies.values()[1]
                user_info = str(ins_url + '/user' + user_name +'?next=%s&uid=%d&rg=%s'%(next_cursor,user_id,rg))
                # print(user_info)
                info_headers = {
                    'Accept':'*/*',
                    'Content-Length':'0',
                    'Cache-Control': 'no-cache',
                    # 'accept-language': 'zh-CN,zh;q=0.9',
                    'Connection': 'keep-alive',
                    'origin':ins_url,
                    'pragma':'no-cache',
                    'referer':ins_url + user_name,
                    'x-requested-with':'XMLHttpRequest',
                    'user-agent':random.choice(uas),
                    'cookie':cookie,


                }
                url_list = html_res.xpath('//*[@id="list"]//div/a/@href')
                for user in url_list:
                    if user not in user_list:
                        user_list.append(user)
                print('**********开始抓取:', user_info)
                print(user_id)
                single_info(user_info,info_headers,user_id,rg,user_name)
                print('-----%s用户爬取完毕，爬取下一个用户---'%user_name)
                # parse_more_user(user_list)





                #访问连接是/tag/***情况，此时无id和rg
                #url_info = ins_url + user_name +'?next=next_cursor'
            else:
                user_info = str(ins_url + user_name + '?next=%s'%next_cursor)
                print(user_info)
                cookie = res.cookies.keys()[0]+'='+res.cookies.values()[0]+';'+res.cookies.keys()[1]+res.cookies.values()[1]

                info_headers = {
                    'Accept': '*/*',
                    # 'accept-language':'zh-CN,zh;q=0.9',
                    'Content-Length': '0',
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                    'origin': ins_url,
                    'pragma': 'no-cache',
                    'referer': ins_url + user_name,
                    'x-requested-with': 'XMLHttpRequest',
                    'user-agent': random.choice(uas),
                    'cookie': cookie,

                }
                print('**********开始抓取:',user_info)
                single_info(user_info,info_headers)
                print('-----%s用户爬取完毕，爬取下一个用户---' % user_name)




        else:
            print('访问不成功,状态码:%d'%res.status_code)
    except TimeoutError:
        print('超时')


def single_info(user_info,info_headers,user_id=None,rg=None,user_name=None):
    res = requests.post(user_info, headers=info_headers)
    rg = rg
    user_name = user_name
    try:
        _json = json.loads(res.text)
        if rg !=None :

            for info in  _json['user']['media']['nodes']:
                info_list = {}
                info_list['_id'] = info['_id']
                info_list['code'] = info['code']
                info_list['date'] = info['date']
                info_list['display_src'] = info['display_src']
                info_list['is_video'] = info['is_video']
                info_list['likes'] = info['likes']
                info_list['srcset'] = info['srcset']
                info_list['__typename'] = info['__typename']
                ins.insert(info_list)

            if _json['user']['media']['page_info']['has_next_page'] == True:
                    new_cursor = _json['user']['media']['page_info']['end_cursor']

                    next_info_url = ins_url + '/user' + user_name +'?next=%s&uid=%d&rg=%s'%(new_cursor,user_id,rg)
                    print(next_info_url)
                    single_info(next_info_url,info_headers,user_id,rg,user_name)


        else:
            for info in _json['media']['top_posts']:
                info_list = {}
                info_list['_id'] = info['_id']
                info_list['code'] = info['code']
                info_list['date'] = info['date']
                info_list['display_src'] = info['display_src']
                info_list['is_video'] = info['is_video']
                info_list['likes'] = info['likes']
                info_list['srcset'] = info['srcset']
                info_list['__typename'] = info['__typename']
                info_list['thumbnail_src'] = info['thumbnail_src']
                ins.insert(info_list)

                try:
                    if _json['media']['page_info']['has_next_page'] == True:
                        new_cursor = _json['media']['page_info']['end_cursor']
                        new_cursor_url = ins_url + user_name + '?next=%s'%new_cursor
                        print(new_cursor)
                        single_info(new_cursor_url, info_headers)
                except Exception as e :
                    return '该用户爬取完毕'
    except:
        res = requests.get(user_info, headers=info_headers)
        html_res = etree.HTML(res.text)
        likes = html_res.xpath('//*[@id="list"]//span/text()')[0]
        code = str(html_res.xpath('//*[@id="list"]//div/@data-code')[0])
        pic_url = 'https://www.veryins.com/p/' + code
        pic_res = requests.post(pic_url,headers=info_headers)
        _json = json.loads(pic_res.text)
        info_list={}
        for info in _json['owner']:
            info_list['caption'] = info['caption']
            info_list['display_url'] = info['display_url']
            info_list['is_video'] = info['false']
            info_list['likes'] = likes

        ins.insert(info_list)




def parse_more_user(user_list):
    for user_name in user_list:
        print(user_name)
        parse_first_page(user_name)

if __name__ == '__main__':
    db = pymongo.MongoClient('127.0.0.1', 27017)
    ins = db['INS']['info']

    count = 0
    uas = UserAgent()

    ins_url = "https://www.veryins.com"

    _cookie = '__cfduid=d7d220d92ef0ae37854ac93e389f582ac1551235574; Hm_lvt_453ab3ca06e82d916be6d6937c3bf101=1551235609; hd_hongbao=1; Hm_lpvt_453ab3ca06e82d916be6d6937c3bf101=1551272361; connect.sid=s%3A-k52E1krx1I7en6Gw8sWZIjDB0drnVgo.rP7VGYO91Dp6Gj4dhlktaZ7fuhTydpiHHFNEbptC5Hw'
    cookie_id = ''
    next_cookie = _cookie + str(cookie_id)

    created_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    updated_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    star_user = '/xxxibgdrgn'

    start_url = ins_url + star_user

    user_list = []

    parse_first_page(star_user)
    parse_more_user(user_list)


