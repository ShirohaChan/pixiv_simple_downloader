import json

from functions import link_url, image_info, filter_condition, judge_download_repeat


def get_user_collect(user_id, headers, proxies, own_account):
    # 判断id是不是自己
    if not own_account:
        original_url = 'https://www.pixiv.net/ajax/user/' + user_id + '/illusts/bookmarks?tag=&offset=0&limit=48&rest' \
                                                                      '=show&lang=zh'
        url_info = link_url(original_url, headers, proxies).text
        bookmark_image_info = json.loads(url_info)
        total_bookmark_num = bookmark_image_info['body']['total']
        print(f'用户{user_id}公开收藏了{total_bookmark_num}份作品')
        if total_bookmark_num:
            whether_filter = input('请问是否需要过滤图片，如果要，请输入1，不用请输入2： ')
            want_down_count = input('请问要下载多少张图片呢: ')
            while True:
                if want_down_count.isdigit() and int(want_down_count) < int(total_bookmark_num):
                    break
                else:
                    print('输入的内容有问题，请重输')
                    want_down_count = input('请问要下载多少张图片呢: ')
            # 让需要的用户输入过滤条件
            if whether_filter == '1':
                input_bookmark_num = input('请输入最低的收藏数')
                want_R_18 = input('是否允许R-18(0:不允许,1:允许)：')
                AI = input('是否允许AI(0:不允许,1:允许)：')
            # 定义文件夹名
            folder_name = f'用户{user_id}收藏的作品'
            # 设置初始页码
            bookmark_page = 0
            # 初始下载数
            down_count = 0
            while True:
                bookmark_url = 'https://www.pixiv.net/ajax/user/' + user_id + '/illusts/bookmarks?tag=&offset=' + \
                               str(bookmark_page) + '&limit=48&rest=show&lang=zh'
                bookmark_image_info = json.loads(link_url(bookmark_url, headers, proxies).text)
                images_id = [item['id'] for item in bookmark_image_info['body']['works']]
                if images_id:
                    for image_id in images_id:

                        total_image_info = image_info(image_id, headers, proxies)
                        permit, image_page_num, download_link, work_type, bookmark_num, AI_work, R_18 = \
                            total_image_info[:7]
                        if whether_filter == '1':
                            down_permit = filter_condition(bookmark_num, input_bookmark_num, permit, AI, AI_work,
                                                           want_R_18, R_18)
                            if down_permit:
                                judge_download_repeat(folder_name, image_page_num, download_link, work_type, headers,
                                                      proxies)
                        else:
                            if permit:
                                judge_download_repeat(folder_name, image_page_num, download_link, work_type, headers,
                                                      proxies)
                        down_count += 1
                        # 判断是否中止内循环
                        if down_count == want_down_count:
                            break
                    # 判断是否中止外循环
                    if down_count == want_down_count:
                        print('已全部下载完成')
                        break
                    else:
                        bookmark_page += 48

    else:
        public_url = 'https://www.pixiv.net/ajax/user/' + user_id + '/illusts/bookmarks?tag=&offset=0&limit=48&rest' \
                                                                    '=show&lang=zh'
        private_url = 'https://www.pixiv.net/ajax/user/' + user_id + '/illusts/bookmarks?tag=&offset=0&limit=48&rest' \
                                                                     '=hide&lang=zh'
        public_url_info = link_url(public_url, headers, proxies).text
        private_url_info = link_url(private_url, headers, proxies).text
        public_bookmark_image_info = json.loads(public_url_info)
        private_bookmark_image_info = json.loads(private_url_info)
        total_public_bookmark_num = public_bookmark_image_info['body']['total']
        total_private_bookmark_num = private_bookmark_image_info['body']['total']
        print(f'您公开收藏了{total_public_bookmark_num}份作品\n您不公开收藏了{total_private_bookmark_num}份作品')
        whether_filter = input('请问是否需要过滤图片，如果要，请输入1，不用请输入2： ')
        if not total_private_bookmark_num and not total_public_bookmark_num:
            print('您没有收藏任何插图或漫画，程序已自动退出')
        else:
            want_public_down_count = input('请问要下载公开收藏中的多少张图片呢: ')
            want_private_down_count = input('请问要下载未公开收藏中的多少张图片呢: ')
            # 先处理公开收藏的内容
            if total_public_bookmark_num:
                while True:
                    if want_public_down_count.isdigit() and int(want_public_down_count) < int(
                            total_public_bookmark_num):
                        break
                    else:
                        print('输入的内容有问题，请重输')
                        want_public_down_count = input('请问要下载多少张图片呢: ')
                # 让需要的用户输入过滤条件
                if whether_filter == '1':
                    input_public_bookmark_num = input('请输入最低的收藏数')
                    want_public_R_18 = input('是否允许R-18(0:不允许,1:允许)：')
                    public_AI = input('是否允许AI(0:不允许,1:允许)：')
                # 定义文件夹名
                folder_name = f'您({user_id})公开收藏的作品'
                # 设置初始页码
                bookmark_page = 0
                # 初始下载数
                down_count = 0
                while True:
                    public_bookmark_url = 'https://www.pixiv.net/ajax/user/' + user_id + '/illusts/bookmarks?tag' \
                                                                                         '=&offset=' + str(
                        bookmark_page) + '&limit=48&rest=show&lang=zh'
                    public_bookmark_image_info = json.loads(link_url(public_bookmark_url, headers, proxies).text)
                    images_id = [item['id'] for item in public_bookmark_image_info['body']['works']]
                    if images_id:
                        for image_id in images_id:

                            total_image_info = image_info(image_id, headers, proxies)
                            permit, image_page_num, download_link,work_type, bookmark_num, AI_work, R_18 = \
                                total_image_info[:7]
                            if whether_filter == '1':
                                down_permit = filter_condition(bookmark_num, input_public_bookmark_num, permit,
                                                               public_AI, AI_work, want_public_R_18, R_18)
                                if down_permit:
                                    judge_download_repeat(folder_name, image_page_num, download_link, work_type,
                                                          headers, proxies)
                            else:
                                if permit:
                                    judge_download_repeat(folder_name, image_page_num, download_link, work_type,
                                                          headers, proxies)
                            down_count += 1
                            # 判断是否中止内循环
                            if down_count == want_public_down_count:
                                break
                        # 判断是否中止外循环
                        if down_count == want_public_down_count:
                            print('已全部下载完成')
                            break
                        else:
                            bookmark_page += 48

            # 处理未公开内容
            if total_private_bookmark_num:
                while True:
                    if want_private_down_count.isdigit() and int(want_private_down_count) > \
                            int(total_private_bookmark_num):
                        break
                    else:
                        print('输入的内容有问题，请重输')
                        want_private_down_count = input('请问要下载多少张图片呢: ')
                # 让需要的用户输入过滤条件
                if whether_filter == '1':
                    input_private_bookmark_num = input('请输入最低的收藏数')
                    want_private_R_18 = input('是否允许R-18(0:不允许,1:允许)：')
                    private_AI = input('是否允许AI(0:不允许,1:允许)：')
                # 定义文件夹名
                folder_name = f'您({user_id})未公开收藏的作品'
                # 设置初始页码
                bookmark_page = 0
                # 初始下载数
                down_count = 0
                while True:
                    private_bookmark_url = 'https://www.pixiv.net/ajax/user/' + user_id + '/illusts/bookmarks?tag' \
                                                                                          '=&offset=' + \
                                           str(bookmark_page) + '&limit=48&rest=hide&lang=zh'
                    private_bookmark_image_info = json.loads(link_url(private_bookmark_url, headers, proxies).text)
                    images_id = [item['id'] for item in private_bookmark_image_info['body']['works']]
                    if images_id:
                        for image_id in images_id:

                            total_image_info = image_info(image_id, headers, proxies)
                            permit, image_page_num, download_link, work_type, bookmark_num, AI_work, R_18 = \
                                total_image_info[:7]
                            if whether_filter == '1':
                                down_permit = filter_condition(bookmark_num, input_private_bookmark_num, permit,
                                                               private_AI, AI_work, want_private_R_18, R_18)
                                if down_permit:
                                    judge_download_repeat(folder_name, image_page_num, download_link, work_type,
                                                          headers, proxies)
                            else:
                                if permit:
                                    judge_download_repeat(folder_name, image_page_num, download_link, work_type,
                                                          headers, proxies)
                            down_count += 1
                            # 判断是否中止内循环
                            if down_count == want_private_down_count:
                                break
                        # 判断是否中止外循环
                        if down_count == want_private_down_count:
                            print('已全部下载完成')
                            break
                        else:
                            bookmark_page += 48
