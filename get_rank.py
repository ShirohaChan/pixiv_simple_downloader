import datetime
import json
import time
from functions import link_url, image_info, judge_download_repeat


def get_rank_image(headers, proxies):
    day = datetime.datetime.now().strftime('%Y-%m-%d')
    folder_name = '每日排行' + day
    down_count = 0
    want_count = input('请输入要下载前多少名的图片(最多500名): ')
    for page in range(1, 11):
        # 日榜的相关数据存于次url
        rank_url = 'https://www.pixiv.net/ranking.php?p=' + str(page) + '&format=json'
        # url传入连接函数获取返还的数据
        rank_info = link_url(rank_url, headers, proxies).text
        # 获取图片的id列表
        image_id_json = json.loads(rank_info)
        image_id_list = [item['illust_id'] for item in image_id_json['contents']]
        for image_id in image_id_list:
            permit, page_num, download_link, work_type, _, _, _ = image_info(str(image_id), headers, proxies)
            if permit:
                judge_download_repeat(folder_name, page_num, download_link, work_type, headers, proxies)
            down_count += 1
            # 先判断是否要继续输出id
            if down_count == int(want_count):
                break
        # 再判断是否要切换页码
        if down_count == int(want_count):
            break


"""headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.67'
}
rank_url = 'https://www.pixiv.net/ranking.php?p=1&format=json'
res = requests.get(rank_url, headers=headers, verify=False).text
res_info = json.loads(res)
image_id = [item['illust_id']for item in res_info['contents']]
print(image_id)
print(len(image_id))"""
