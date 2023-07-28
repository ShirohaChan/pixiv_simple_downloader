import json
import time
from functions import link_url, image_info, filter_condition, judge_download_repeat


def download_recommend(user_id, headers, proxies):
    # 交互部分
    filter_image = input('请问是否要根据自己的需要对图片进行过滤，如果需要，请键入1，若不用，请键入2: ')
    want_down_illust_count = input('请输入想要下载多少份插画: ')
    want_down_manga_count = input('请输入想要下载多少份漫画: ')
    if filter_image == '1':
        if int(want_down_illust_count) > 0:
            want_bookmark_illust_num = input('请输入插画最低收藏数: ')
            want_illust_R_18 = input('插画是否允许R_18(0:不允许,1:允许): ')
            want_illust_AI = input('插画是否允许AI(0:不允许,1:允许): ')
        if int(want_down_manga_count) > 0:
            want_bookmark_manga_count = input('请输入漫画最低收藏数: ')
            want_manga_R_18 = input('漫画是否允许R_18(0:不允许,1:允许): ')
            want_manga_AI = input('漫画是否允许AI(0:不允许,1:允许): ')
    # 命名文件夹
    folder_name = f'用户{user_id}根据算法推荐的作品'
    # 设置初始量
    down_illust_count = 0
    down_manga_count = 0
    refresh_illust_url = 0
    refresh_manga_url = 0
    print('检索开始')
    # 插图部分
    if int(want_down_illust_count) > 0:
        while True:
            recommend_illust_url = 'https://www.pixiv.net/ajax/top/illust?mode=all&lang=zh'
            recommend_illust_res = link_url(recommend_illust_url, headers, proxies)
            recommend_illust_json = json.loads(recommend_illust_res.text)
            recommend_illust_ids = recommend_illust_json['body']['thumbnails']['illust']
            recommend_illust_id = []
            for item in recommend_illust_ids:
                recommend_illust_id.append(item['id'])
            for illust_id in recommend_illust_id:  # 不知道为什么。前59份插画在一天之内是不会变化的，而且，前11份似乎是固定不变的
                # idx = '74870473'
                illust_info = image_info(illust_id, headers, proxies)
                permit, page_num, download_link, work_type, bookmark_num, AI_work, R_18 = illust_info
                if permit and filter_image == '1':
                    # 判断图片是否满足条件
                    down_permit = filter_condition(bookmark_num, want_bookmark_illust_num, permit, want_illust_AI,
                                                   AI_work, want_illust_R_18, R_18)
                    if down_permit:
                        print(f'{illust_id}符合条件，将下载')
                        real_down = judge_download_repeat(folder_name, page_num, download_link, work_type, headers,
                                                          proxies)
                        if real_down:
                            down_illust_count += 1
                    else:
                        print(f'{illust_id}不符条件，已淘汰')
                else:
                    if permit:
                        real_down = judge_download_repeat(folder_name, page_num, download_link, work_type, headers,
                                                          proxies)
                        if real_down:
                            down_illust_count += 1
                    # 判断内循环是否要结束
                if down_illust_count == int(want_down_illust_count):
                    break
                else:
                    # 每0.5s一个循环
                    time.sleep(0.5)
            # 判断外循环是否要结束
            if down_illust_count == int(want_down_illust_count):
                break
            else:
                refresh_illust_url += 1
                print(f'已完成{refresh_illust_url}次刷新')
    else:
        print('您选择不下载插画')
    # 漫画部分
    if int(want_down_manga_count) > 0:
        # 修改Referer头
        headers['Referer'] = 'https://www.pixiv.net/manga'
        print(headers)
        while True:
            recommend_manga_url = 'https://www.pixiv.net/ajax/top/manga?mode=all&lang=zh'
            recommend_manga_res = link_url(recommend_manga_url, headers, proxies)
            recommend_manga_json = json.loads(recommend_manga_res.text)
            recommend_manga_ids = recommend_manga_json['body']['thumbnails']['illust']
            recommend_manga_id = []
            for item in recommend_manga_ids:
                recommend_manga_id.append(item['id'])
            for manga_id in recommend_manga_id:  # 不知道为什么。前24份漫画似乎是固定的
                manga_info = image_info(manga_id, headers, proxies)
                permit, page_num, download_link, work_type, bookmark_num, AI_work, R_18 = manga_info[:8]
                if filter_image == '1' and permit:
                    down_permit = filter_condition(bookmark_num, want_bookmark_manga_count, permit, want_manga_AI,
                                                   AI_work, want_manga_R_18, R_18)
                    if down_permit:
                        real_down = judge_download_repeat(folder_name, page_num, download_link, work_type, headers,
                                                          proxies)
                        if real_down:
                            down_manga_count += 1
                else:
                    if permit:
                        real_down = judge_download_repeat(folder_name, page_num, download_link, work_type, headers,
                                                          proxies)
                        if real_down:
                            down_manga_count += 1
                if down_manga_count == int(want_down_manga_count):
                    break

            if down_manga_count == int(want_down_manga_count):
                print('已按要求完成所有下载')
                break
            else:
                refresh_manga_url += 1
                print(f'已完成{refresh_manga_url}次刷新')

    else:
        print('您选择不下载漫画')
