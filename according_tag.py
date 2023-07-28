import math
import re
import time

from functions import link_url, image_info, judge_download_repeat, filter_condition


def down_tag_illustration(headers, proxies):
    tag = input('请问您想要检索哪个标签的图片？: ')
    original_tag_url = 'https://www.pixiv.net/ajax/search/artworks/' + tag + '?word=' + tag + \
                       '&order=date_d&mode=all&p=1&s_mode=s_tag_full&type=all&lang=zh'
    tag_total_info = link_url(original_tag_url, headers, proxies).text
    # print(total_info)
    total_num = re.findall('"total":(.*?),"bookmarkRanges":.*?', tag_total_info)[0]
    # 得出该标签最多能有多少页
    total_page = math.ceil(int(total_num) / 60)
    max_page = 1000
    # 判断是否超过1000页
    if total_page > max_page:
        total_page = max_page
    print('该标签下共搜到：' + total_num + '张图，最多能下载：' + str(total_page) + '页图(pixiv最多能展示至1000页)')
    # 输入过滤条件
    print(
        '请注意：默认情况下，R-18标签是关闭的，而AI标签是默认开启的，所以以下过滤条件对于部分用户可能没有用且会对搜索出来的图片总数产生影响')
    input_bookmark_num = input('请输入最低的收藏数：')
    want_R_18 = input('是否允许R-18(0:不允许,1:允许)：')
    AI = input('是否允许AI(0:不允许,1:允许)：')
    search_page = input('请输入要检索多少页，每页最多包含60张图(输入0可以全部下载)：')
    # 定义文件夹名
    folder_name = f'#{tag}的作品'
    # 展示提示
    print('————————————————————————————————开始检索——————————————————————————————————————')
    print('提示1：如果遇到上一页的图片id出现在了下一页，属于正常现象，说明该标签内有新图出现，将旧图挤下来了')
    print('提示2：有时，一个页面的图片可能只有59张，此时，第60张图就会变成热榜里的图')
    # 开始检索
    for i in range(1, max_page + 1):
        tag_url = 'https://www.pixiv.net/ajax/search/artworks/' + tag + '?word=' + tag + '&order=date_d&mode=all&p=' + \
                  str(i) + '&s_mode=s_tag_full&type=all&lang=zh'
        # 获取每页图片的id列表
        images_id_info = link_url(tag_url, headers, proxies).text
        images_id = re.findall('"id":"(.*?)"', images_id_info)[:60]
        if int(search_page) != 0 and i > int(search_page):
            break
        if not images_id:
            break
        else:
            for image_id in images_id:
                all_image_info = image_info(image_id, headers, proxies)
                permit, page_num, download_link, work_type, bookmark_num, AI_work, R_18 = all_image_info[:7]
                # 判断是否符合过滤的条件
                down_permit = filter_condition(bookmark_num, input_bookmark_num, permit, AI, AI_work, want_R_18, R_18)
                # 符合调用下载函数
                if down_permit:
                    print(f'{image_id}符合条件，将下载')
                    judge_download_repeat(folder_name, page_num, download_link, work_type, headers, proxies)
                else:
                    print(f'{image_id}不符合条件，已淘汰')
                # 每隔0.5s解析一次
                time.sleep(0.5)
            print('第' + str(i) + '页已经检索完成')
