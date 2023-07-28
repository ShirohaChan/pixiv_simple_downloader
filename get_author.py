import json
import re
from functions import link_url, image_info, judge_download_repeat


def get_author_image(headers, proxies):
    author_id = input('请输入要检索的作者的id: ')
    # 先获取作者的名字
    author_url = 'https://www.pixiv.net/users/' + author_id
    author_info = link_url(author_url, headers, proxies).text
    author_name = re.findall('meta property="og:title" content="(.*?)"', author_info)[0]
    print(f'根据您输入的id，检索到的用户为：{author_name}')
    author_work_url = 'https://www.pixiv.net/ajax/user/' + author_id + '/profile/all?lang=zh'
    author_work_info = link_url(author_work_url, headers, proxies).text
    # 转为字典格式
    author_work_json = json.loads(author_work_info)
    # 获取该作者的插画作品
    illusts_id = author_work_json['body']['illusts'].keys()
    # 获取该作者的漫画作品
    if author_work_json['body']['manga']:
        mangas_id = author_work_json['body']['manga'].keys()
    else:
        mangas_id = []
    print(f'该作者共{len(illusts_id)}份插画，共{len(mangas_id)}份漫画')
    illust_count = input('请问您要下载多少份插画: ')
    manga_count = input('请问您要下载多少份漫画: ')
    # 定义文件夹名字
    folder_name = f'{author_name}的作品'
    # 定义一个初始的下载数
    down_iilust_count = 0
    down_manga_count = 0
    # 先下载插画
    if illust_count != '0' and len(illusts_id) != 0:
        for illust_id in illusts_id:
            res_image_info = image_info(str(illust_id), headers, proxies)
            permit, page_num, download_link, work_type = res_image_info[0:4]
            if permit:
                judge_download_repeat(folder_name, page_num, download_link, work_type, headers, proxies)
                down_iilust_count += 1
            if down_iilust_count == int(illust_count):
                print('您指定数量的插画作品已下载完成')
                break
    else:
        if not illusts_id:
            print('该用户没有插画作品')
        else:
            if illust_count == '0':
                print(f'您选择不下载该作者的插画')
    # 下载漫画
    if manga_count != '0' and len(mangas_id) != 0:
        for manga_id in mangas_id:
            permit, page_num, _, download_link, work_type = image_info(str(manga_id), headers, proxies)
            if permit:
                judge_download_repeat(folder_name, page_num, download_link, work_type, headers, proxies)
                down_manga_count += 1
            if down_manga_count == int(manga_count):
                print('您指定数量的漫画作品已下载完成')
                break
    else:
        if not mangas_id:
            print(f'该用户没有漫画作品')
        else:
            if manga_count == '0':
                print(f'您选择不下载该作者的漫画')
