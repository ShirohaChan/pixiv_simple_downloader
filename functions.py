import os
import re
import sys
import time
import requests
import urllib3
from PyQt5 import QtWidgets
from requests.exceptions import ProxyError
from get_cookie_window import WebWindow

# 忽略警告
urllib3.disable_warnings()


# 定义一个统一的获取图片相关信息的函数
def image_info(image_id, headers, proxies):
    image_url = 'https://www.pixiv.net/artworks/' + image_id

    max_attempts = 10
    for attempt in range(max_attempts):
        try:
            image_information = link_url(image_url, headers, proxies).text
            condition_num = re.findall('likeData":.*?,"width":.*?,"height":.*?,"pageCount":(.*?),'
                                       '"bookmarkCount":(.*?),"likeCount":.*?', image_information)[0]
            # 获取收藏数，作品页数
            page_num, bookmark_num = condition_num
            # 获取下载链接
            download_link = re.findall('"original":"(.*?)"', image_information)[0]
            # 判断作品类型
            series_type = re.findall('"seriesNavData":{"seriesType":"(.*?)","seriesId":".*?"', image_information)
            pattern = r'"tags":\[(.+?)\]'
            match = re.search(pattern, image_information)
            if match:
                tags_str = match.group(1)
                tags = [tag.strip('{}') for tag in tags_str.split('},{')]
            tags_only = [tag.split(',')[0].split(':')[1].strip('"') for tag in tags]
            if series_type or any(tag.lower() == '漫画' for tag in tags_only):
                work_type = '漫画'
            else:
                work_type = '插画'
            # 判断作品是否为AI创作
            AI_info = re.findall('"commentOff":.*?,"aiType":(.*?)}}', image_information)[0]
            if AI_info == '2':
                AI_work = True
            else:
                AI_work = False
            # 判断作品是否有R-18标签(通过解析作品的标题数据)
            title_info = re.findall('<meta property="twitter:title" content="(.*?)">', image_information)[0]
            if_R18 = re.search(r'\[(.*?)\]', title_info)
            if not if_R18:
                R_18 = False
            else:
                R_18 = True
            # 赋予通行证
            permit = True
            break
        except (IndexError, Exception):
            print(f"{image_id} 解析失败，已尝试：{attempt}/{max_attempts}")
            # 隔1s后重试（仿检测）
            time.sleep(1)
    else:
        print('经过所有尝试，' + image_id + '解析失败，将跳过后续解析')
        # 不赋予通行证
        permit = False
    if not permit:
        page_num = None
        download_link = None
        work_type = None
        bookmark_num = None
        AI_work = None
        R_18 = None
    return permit, page_num, download_link, work_type, bookmark_num, AI_work, R_18


# 定义一个请求头
def define_headers(account):
    if account == 'n':
        cookies = get_cookies()
        print('登录成功')
    elif account == 'y':
        cookies = switch_account()
        print('切换账号成功')
    elif account == '0':
        cookies = None
        print('您没有账号，会导致获取的图片非常不全！')
    if cookies:
        cookie_str = '; '.join(f'{name}={value[0]}' for name, value in cookies.items())
        # print(cookie_str)
    else:
        cookie_str = None
    headers = {
        'Cookie': cookie_str,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.67',
        'Referer': 'https://www.pixiv.net/'
    }
    return headers, cookie_str


# 判断连接是否成功
def test_link(headers, proxies):
    url = 'https://www.pixiv.net/'
    try:
        test_res = link_url(url, headers, proxies)
        return test_res
    except ProxyError:
        return False


# 保持登录状态获取cookie
def get_cookies():
    app = QtWidgets.QApplication(sys.argv)
    window = WebWindow()
    window.show()
    app.exec_()
    return window.cookies


# 切换账号获取新cookie
def switch_account():
    app = QtWidgets.QApplication(sys.argv)
    window = WebWindow()
    window.delete_cookies()
    window.check_login_status()
    window.show()
    app.exec_()
    return window.cookies


# 一个统一的网页访问
def link_url(url, headers, proxies):
    url_res = requests.get(url=url, headers=headers, proxies=proxies, verify=False)
    return url_res


# 判断文件夹是否创建
def judge_create_folder(folder_name, work_type_name):
    folder_create = 'D:/pixiv/' + folder_name + '/' + work_type_name
    if not os.path.exists(folder_create):
        os.makedirs(folder_create)
    return folder_create


# 判断文件是否重复下载,并用于接受接下来所要用到函数的所有形参
def judge_download_repeat(folder_name, image_page, original_download_link, work_type, headers, proxies):
    # 先判断文件夹是否创建
    folder_path = judge_create_folder(folder_name, work_type)
    for p in range(int(image_page)):
        # 将链接后面的p0根据实际页数进行修改
        download_link = original_download_link.replace('p0', 'p{}'.format(p))
        # 通过链接获取到文件名
        filename = os.path.basename(download_link)
        # 读取文件夹里所有的文件名
        all_filename = os.listdir(folder_path)
        # 判断文件是否已经下载，若下过了，不调用下载函数
        if filename not in all_filename:
            # 将文件名路径自动全
            image_path = os.path.join(folder_path, filename)
            # 调用下载函数
            download_image(download_link, image_path, filename, headers, proxies)
            # build_threading(download_link, headers, proxies, image_path)
            real_down = True
        else:
            print(f'{filename}已经下载过了，略过')
            real_down = False
    return real_down


# 统一的图片下载函数
def download_image(download_link, file_path, image_name, headers, proxies):
    attempts = 0
    print(f'{image_name}正在下载')
    while True:
        try:
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            headers['Range'] = f'bytes={file_size}-'
            image = requests.get(download_link, headers=headers, proxies=proxies, stream=True)
            # print(image)
            with open(file_path, "ab") as f:
                for chunk in image.iter_content(chunk_size=1024):
                    f.write(chunk)
            print(f"{image_name}下载完成")
            # 重置Range
            headers['Range'] = None
            break
        except requests.exceptions.ChunkedEncodingError:
            print(f"{image_name}下载失败，正在接续下载，已接续: {attempts + 1}次")
            attempts += 1
            # 隔0.5s后接续（仿检测）
            time.sleep(0.5)


def filter_condition(bookmark_num, input_bookmark_num, permit, AI, AI_work, want_R_18, R_18):
    down_permit = False
    if int(bookmark_num) >= int(input_bookmark_num) and permit:
        # AI不允许
        if AI == '0':
            # R_18不允许
            if not AI_work:
                if want_R_18 == '0':
                    if not R_18:
                        down_permit = True
                    else:
                        print('作品含有R-18标签')
                # R_18允许
                else:
                    down_permit = True
            else:
                print('作品含有AI标签')
        # AI允许
        else:
            # R_18不允许
            if want_R_18 == '0':
                if not R_18:
                    down_permit = True
                else:
                    print('作品含有R-18标签')
                # R-18允许
            else:
                down_permit = True
    else:
        print(f'{bookmark_num}<{input_bookmark_num}')
    return down_permit
