from functions import *
from get_rank import get_rank_image
from get_author import get_author_image
from according_tag import down_tag_illustration
from download_user_collect import get_user_collect
from download_by_ALG import download_recommend

# 获取cookie
account_mode = input('是否有账号，有请输入1，没有请输入2: ')
if account_mode == '2':
    account = '0'
else:
    print('若已在本程序中存有账号，请输入n；若想切换账号，请输入y；若是初次登录，输入y或n皆可')
    account = input('请输入对应的内容: ')
headers_info = define_headers(account)
headers = headers_info[0]
# 判断是否使用了代理服务
link_mode = input('是否有使用代理（不包括全局代理），如果有，请输入1，没有则输入2: ')
while True:
    if link_mode == '1':
        print('请输入代理服务器地址：')
        add1 = input('http:')
        add2 = input('https:')
        proxies = {
            'http': add1,
            'https': add2
        }
        res = test_link(headers, proxies)
        if res:
            print('连接成功，进入下一步')
            break
        else:
            link_mode = input('连接失败，请尝试更换连线模式：')
    elif link_mode == '2':
        proxies = None
        res = test_link(headers, proxies)
        if res:
            print('连接成功，进入下一步')
            break
        else:
            link_mode = input('连接失败，请尝试更换连线模式：')
# 功能界面
print('1. 下载日榜图片')
print('2. 下载指定作者的作品')
print('3. 下载指定标签的作品')
print('4. 下载自己或他人收藏的作品')
print('5. 下载根据您的喜好而通过算法推荐给你的作品')
function_mode = input('请输入想要的功能：')
function_list = ['1', '2', '3', '4', '5']
# 检测用户是否误输入
while True:
    if function_mode not in function_list:
        print('请重输！')
        function_mode = input('请输入想要的功能：')
    else:
        break
if function_mode == '1':
    get_rank_image(headers, proxies)
if function_mode == '2':
    get_author_image(headers, proxies)
if function_mode == '3':
    down_tag_illustration(headers, proxies)
if function_mode == '4':
    if account == '0':
        print('您没有账号，该功能无法使用')
    else:
        user_id = input('如果您选择下载您指定用户的公开收藏，请输入该用户id，如果您想下载您自己的收藏，请输入0: ')
        if user_id == '0':
            cookie = headers_info[1]
            # 使用正则获取用户id
            pattern = r'(\d+)_'
            match = re.search(pattern, cookie)
            user_id = match.group(1)
            own_account = True
        else:
            own_account = False
        get_user_collect(user_id, headers, proxies, own_account)
if function_mode == '5':
    if account == '0':
        print('您没有账号，该功能无法使用')
    else:
        cookie = headers_info[1]
        # 使用正则获取用户id
        pattern = r'(\d+)_'
        match = re.search(pattern, cookie)
        user_id = match.group(1)
        download_recommend(user_id, headers, proxies)
