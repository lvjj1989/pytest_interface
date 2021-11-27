# @Time    :2019/9/25 14:42
# @Author  :lvjunjie
"""
爬去指定网站上的超链接
逐个get请求超链接，发现异常数据进行记录统计
将异常的链接数据位置截图
生成报告
"""
import requests
from bs4 import BeautifulSoup
import re
import os
from urllib.parse import urlparse
import html5lib
import lxml
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from PIL import Image
import logging
import platform
import gc
# import gevent
get_session = requests.session()
requests.packages.urllib3.disable_warnings()

# print(platform.system())
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
if platform.system() in ('Windows', 'Darwin'):
    handler = logging.FileHandler("log.log")
elif platform.system() == 'Linux':
    handler = logging.FileHandler("/opt/apache-tomcat-8.5.34/logs/errorlink_log.log")
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def log_writing(log_text):
    try:
        logger.info(log_text)
    except:
        pass


def get_xpath_screenshot(url, xpath, error_img_name, link):
    try:
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--headless')
        # chrome_options.add_argument('blink-settings=imagesEnabled=false')
        # chrome_options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(chrome_options=chrome_options)
        # driver = webdriver.Chrome()
        # driver.maximize_window()
        driver.get(url)
        html = driver.find_element_by_xpath("//*").get_attribute("outerHTML")
        test_xpath_list = driver.find_elements_by_xpath(xpath)  # 需要截图的元素xpath
        # print(driver.get_window_size())
        error_link_img_list = []
        error_link_index = 0
        for test_xpath in test_xpath_list:
            # 获取超链接文案
            try:
                error_link_text = test_xpath.text
            except:
                error_link_text = ''
            xpath_location = test_xpath.find_element_by_xpath('..')
            left = xpath_location.location['x']  # 区块截图左上角在网页中的x坐标
            top = xpath_location.location['y']  # 区块截图左上角在网页中的y坐标
            right = left + xpath_location.size['width']  # 区块截图右下角在网页中的x坐标
            bottom = top + xpath_location.size['height']  # 区块截图右下角在网页中的y坐标
            # height = driver.get_window_size()['height']
            # width = driver.get_window_size()['width']
            print({"left": left, "top": top, "right": right, "bottom ": bottom})
            if (left, top, right, bottom) == (0, 0, 0, 0):
                print(link, "无法取到")
                error_img_name_new = ""
            else:
                height = bottom - top + 25
                width = right - left + 25
                print({"height": height, "width": width})
                print({"left": left, "top": top, "right": right, "bottom ": bottom})
                driver.set_window_size(width, height)  # 调整浏览器大小
                driver.execute_script("arguments[0].scrollIntoView();", xpath_location)  # 滚动至指定位置
                error_img_name_new = r'{}_'.format(error_link_index) + error_img_name
                driver.save_screenshot(error_img_name_new)  # 截全图
                gc.collect()
                picture = Image.open(error_img_name_new)
                # (left, top, right, bottom)
                picture = picture.crop((0, 0, width - 15, height - 15))  # 二次截图，处理滚动条，形成区块截图
                # error_img_name_new = r'{}_'.format(error_link_index) + error_img_name
                picture.save(error_img_name_new)  # 覆盖截取的全图文件

            # if bottom > height:
            #     # height = bottom - top
            #     driver.set_window_size(width, height)  # 调整浏览器大小
            #     driver.execute_script("arguments[0].scrollIntoView();", xpath_location)  # 滚动至指定位置
            #     driver.save_screenshot(r'photo.png')  # 截全图
            #     picture = Image.open(r'photo.png')
            #     bottom = bottom - top
            #     top = 0
            #     print({"left": left, "top": top, "right": right, "bottom ": bottom})
            # if right > width:
            #     width = right - width
            #     driver.set_window_size(width, height)  # 调整浏览器大小
            #     driver.execute_script("arguments[0].scrollIntoView();", xpath_location)  # 滚动至指定位置
            #     driver.save_screenshot(r'photo.png')  # 截全图
            #     picture = Image.open(r'photo.png')
            #     left = width - (right - left)
            #     if left < 0: left = 0
            #     right = width
            #     print({"left": left, "top": top, "right": right, "bottom ": bottom})
            # else:
            #     driver.save_screenshot(r'photo.png')  # 截全图
            #     picture = Image.open(r'photo.png')
            # picture = picture.crop((left, top, right, bottom))  # 二次截图：形成区块截图
            # error_img_name_new = r'{}_'.format(error_link_index) + error_img_name
            # picture.save(error_img_name_new)
            print({"error_img_name": error_img_name_new, "error_link_text": error_link_text})
            log_writing({"error_img_name": error_img_name_new, "error_link_text": error_link_text})
            error_link_img_list.append({"error_img_name": error_img_name_new, "error_link_text": error_link_text})
            error_link_index += 1
        return {"error_link_img_list": error_link_img_list}
    finally:
        driver.quit()


def get_link(url, url_index, headers):
    host = urlparse(url).netloc
    # headers = {
    #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.75 Safari/537.36"
    # }
    try:
        res = get_session.get(url=url, headers=headers, timeout=6, verify=False)
    except:
        print('link error')
        log_writing('link error')
    soup = BeautifulSoup(res.text, 'lxml')
    # print(res.text)
    link_list = []
    error_index = 0
    error_link_info_list = []
    for a in soup.find_all('a'):
        try:
            link = a['href']
            print(link)
            if link[0:11] == 'javascript:' or link[0:1] == '#' or link == '/':
                continue
            elif re.search('^(http)|(https.)+', link):
                new_link = link
            elif link[0:2] == '//':
                new_link = 'https:' + link
            else:
                new_link = "https://" + host + link
            new_link = new_link.rstrip()  # 去除尾部空格
            # 去重
            if new_link in link_list:
                continue
            else:
                link_list.append(new_link)
            # if re.search('(.+jiehun.com.cn.+)|(.+jiabasha.com.+)|(.+yingbasha.com.+)', new_link):
            if new_link:
                try:
                    res = get_session.get(url=new_link, headers=headers, timeout=6, verify=False)
                    if res.status_code == 404:
                        error_link_info = get_xpath_screenshot(url, '//a[@href="{}"]'.format(link),
                                                                   r'error_photo_{}_{}.png'.format(error_index, url_index), link)

                        error_index += 1
                        error_link_info['url'] = url
                        error_link_info['link'] = new_link
                        error_link_info['error_info'] = "status_code is 404"
                        error_link_info_list.append(error_link_info)
                        print(error_link_info)
                        logger.info(error_link_info)
                        logger.info(error_link_info)
                        print("发现异常链接：{}  ，返回404".format(new_link))
                        logger.info("发现异常链接：{}  ，返回404".format(new_link))

                    elif res.status_code == 500:
                        error_link_info = get_xpath_screenshot(url, '//a[@href="{}"]'.format(link),
                                                                   r'error_photo_{}_{}.png'.format(error_index, url_index), link)

                        error_index += 1
                        error_link_info['url'] = url
                        error_link_info['link'] = new_link
                        error_link_info['error_info'] = "status_code is 500"
                        error_link_info_list.append(error_link_info)
                        print(error_link_info)
                        logger.info(error_link_info)
                        logger.info(error_link_info)
                        print("发现异常链接：{}  ，返回500".format(new_link))
                        logger.info("发现异常链接：{}  ，返回500".format(new_link))
                    elif re.search("(.+<h1>Error Found:</h1>.+)|(.+<em>HapN</em>+)", res.text):
                        res = get_session.get(url=new_link, headers=headers, timeout=6, verify=False)
                        if re.search("(.+<h1>Error Found:</h1>.+)|(.+<em>HapN</em>+)", res.text):
                            error_link_info = get_xpath_screenshot(url, '//a[@href="{}"]'.format(link), r'error_photo_{}_{}.png'.format(error_index, url_index), link)
                            error_index += 1
                            error_link_info['url'] = url
                            error_link_info['link'] = new_link
                            error_link_info['error_info'] = "'Error Found:' or 'HapN' in Response"
                            error_link_info_list.append(error_link_info)
                            print(error_link_info)
                            log_writing(error_link_info)
                            print("发现异常链接：{}  ，接口响应{}".format(new_link, res.text))
                            logger.info("发现异常链接：{}  ，接口响应{}".format(new_link, res.text))
                    elif re.search("tthunbohui", res.text):
                        # error_link_info = get_xpath_screenshot(url, '//a[@href="{}"]'.format(link), r'error_photo_{}_{}.png'.format(error_index, url_index), link)
                        # error_index += 1
                        # error_link_info['url'] = url
                        # error_link_info['link'] = new_link
                        # error_link_info['error_info'] = "tthunbohui in Response"
                        # error_link_info_list.append(error_link_info)
                        # print(error_link_info)
                        # log_writing(error_link_info)
                        try:
                            print("发现异常链接：{}  ，接口响应{}".format(new_link, res.text[res.text.index('tthunbohui') - 100, res.text.index('tthunbohui') + 100]))
                            logger.info("发现异常链接：{}  ，接口响应{}".format(new_link, res.text[res.text.index('tthunbohui') - 100, res.text.index('tthunbohui') + 100]))
                        except:
                            print(00000)
                except Exception as err:
                    print('link = ', link)
                    log_writing(link)
                    print(err)
                    log_writing(err)
        except Exception as error_info:
            print("get_link error_info = ", error_info)
            print('link = ', link)

    return error_link_info_list


class Template_mixin:
    """html报告"""
    # http://libs.baidu.com/bootstrap/3.0.3/css/bootstrap.min.css
    HTML_TMPL = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>异常链接测试报告</title>
            <link href="http://qatest.jiehun.tech/bootstrap.min.css" rel="stylesheet">
            <h1 style="font-family: Microsoft YaHei">异常链接测试报告</h1>
            <!--<p class='attribute'><strong>测试结果 : </strong> %(value)s</p>-->
            <style type="text/css" media="screen">
        body  { font-family: Microsoft YaHei,Tahoma,arial,helvetica,sans-serif;padding: 20px;}
        </style>
        </head>
        <body>
            <table id='result_table' class="table table-condensed table-bordered table-hover">
                <colgroup>
                    <col align='left' />
                    <col align='right' />
                    <col align='right' />
                    <col align='right' />
                </colgroup>
                <tr id='header_row' class="text-center success" style="font-weight: bold;font-size: 14px;">
                    <th>序号</th>
                    <th>链接名称</th>
                    <th>主链接</th>
                    <th>异常链接</th>
                    <th>链接文本</th>
                    <th>链接位置截图</th>
                    <th>失败原因</th>
                </tr>
                %(table_tr)s
            </table>
        </body>
        </html>"""

    TABLE_TMPL = """
        <tr class='failClass warning'>
            <td>%(num)s</td>
            <td>%(url_name)s</td>
            <td>%(url)s</td>
            <td>%(error_link)s</td>
            <td>%(error_link_text)s</td>
            <td>%(error_img)s</td>
            <td>%(error_info)s</td>
        </tr>"""


if __name__ == '__main__':

    start_time = time.time()
    url_list = ['https://portal.dxy.cn/']
    url_name_list = ['丁香园首页']
    # print('url_list = ', url_list)
    print('url_name_list = ', url_name_list)
    # html报告数据初始化
    table_tr0 = ''
    html = Template_mixin()
    num = 1
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.75 Safari/537.36 lvjj"
    }
    # headers = {
    #     "User-Agent": "Mozilla/5.0 (Linux; Android 9; BKL-AL20 Build/HUAWEIBKL-AL20; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/045008 Mobile Safari/537.36<<a=hunbasha_android&p=ciw&m=3>> <[[on=Android&ov=9&dn=BKL-AL20&m=HONOR&r=2160X1080]]>"
    # }
    for url_index, url in enumerate(url_list):
        url_name = url_name_list[url_index]
        print(url)
        error_link_info_list = get_link(url, url_index, headers)
        print(error_link_info_list)
        url_index += 1

        # 生成html报告
        for error_link_info in error_link_info_list:
            for error_link_img in error_link_info['error_link_img_list']:
                table_td = html.TABLE_TMPL % dict(
                    num=num,
                    url_name=url_name,
                    url=error_link_info['url'],
                    error_link=error_link_info['link'],
                    error_link_text=error_link_img['error_link_text'],
                    error_img='<img src="{}">'.format(error_link_img['error_img_name']),
                    error_info=error_link_info['error_info']
                )
                table_tr0 += table_td
                num += 1
        output = html.HTML_TMPL % dict(
            value="",
            table_tr=table_tr0,
        )

    with open("index.html", 'wb') as f:
        f.write(output.encode('utf-8'))
        with open("../index.html", 'wb') as f:
            f.write(output.encode('utf-8'))
    with open("urlerror.html", 'wb') as f:
        f.write(output.encode('utf-8'))

    end_time = time.time()
    total_time = end_time - start_time

    print("执行使用时间: {}分钟".format(int(total_time/60)))
    log_writing("执行使用时间: {}分钟".format(int(total_time/60)))

