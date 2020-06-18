#!/usr/bin/python3

import requests
import json

token = 'sYEoLsFpxJ6nu7Rgk9DA8bjCZ1TBkSG9'


class Subs:

    def __init__(self, movie_name):
        self.movie_name = movie_name

    def sub(self):
        url = f'http://api.assrt.net/v1/sub/search?token={token}&q={self.movie_name}'
        g = requests.get(url)
        json_str = g.text
        dic_str = json.loads(json_str)
        subs_list = []
        sub = dic_str.get('sub')
        if sub:
            sub_result = sub.get('result')
            if sub_result:
                # print(sub_result)
                sub_subs = sub.get('subs')  # 列表
                if sub_subs:
                    for sub_subs_list in sub_subs:
                        sub_id = sub_subs_list.get('id')
                        vote_score = sub_subs_list.get('vote_score')
                        lang = sub_subs_list.get('lang')
                        videoname = sub_subs_list.get('videoname')
                        if lang:
                            lang_langlist = lang.get('langlist')
                            if lang_langlist:
                                lang_langlist_langchs = lang_langlist.get(
                                    'langchs')
                                if lang_langlist_langchs:
                                    subs_list.append(
                                        f'sub_id={sub_id},vote_score={vote_score},videoname={videoname}')
            return subs_list
        else:
            return None


class SubUrl:
    def __init__(self, sub_id):
        self.sub_id = sub_id

    def get_url(self):
        url = f'https://api.assrt.net/v1/sub/detail?token={token}&id={self.sub_id}'
        # print(url)
        g = requests.get(url)
        json_str = g.text
        dic = json.loads(json_str)
        sub = dic.get('sub')
        if sub:
            sub_result = sub.get('result')
            if sub_result:
                sub_subs = sub.get('subs')
                if sub_subs:
                    for url in sub_subs:
                        sub_subs_url = url.get('url')
                        if sub_subs_url:
                            return sub_subs_url
        else:
            return None


# main func
while True:
    sub_name = input('Input the movie name:')
    if len(sub_name) <= 3:
        print('error movie name')
    else:
        break

subs = Subs(sub_name).sub()
for index, sub in enumerate(subs, start=1):
    print(index, '<>', sub)

if subs:
    while True:
        sub_choose = input('input download id:')
        try:
            sub_choose = int(sub_choose)
            break
        except ValueError:
            print('input error')

    for index, sub in enumerate(subs, start=1):
        if index == sub_choose:
            sub_id = sub.split(',')[0][7:]
            movie_name = sub.split(',')[2][10:]
            print(f'downloading id: {sub_id}, {movie_name}')
            url = SubUrl(sub_id)
            download_url = url.get_url()
            local_filename = download_url.split('/')[-1]
            local_filename = local_filename.split('?')[0]
            print(download_url, '\n', 'filename:', local_filename)

            with requests.get(download_url, stream=True) as r:
                r.raise_for_status()
                with open(local_filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        f.write(chunk)
                print('', end='.')
        print('download complate')
else:
    print('subs not found')
