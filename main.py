#!/usr/bin/python3

import requests
import json
import os
import re
import rarfile
import zipfile
import shutil

token = 'sYEoLsFpxJ6nu7Rgk9DA8bjCZ1TBkSG9'


def color(strings, option=True):
    if option is False:
        return "\033[31m{}\033[0m".format(strings)
    else:
        return "\033[4;33m{}\033[0m".format(strings)


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
                                        f'sub_id={sub_id},
                                        vote_score={color(vote_score)},
                                        videoname={videoname}')
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


def get_video_name():
    # 获取当前目录视频文件的名称
    ls = os.walk('.')
    try:
        while True:
            file_list = next(ls)
            file_list_3 = file_list[2]
            for file in file_list_3:
                m = re.search('.mp4|.mkv', file)
                try:
                    print(m.group(0), 'found', file)
                    video_name = file.split(m.group(0))[0]
                    return video_name
                except AttributeError:
                    print('.', end='')
    except StopIteration:
        return None


def unc(file, sub_name):
    # file是下载后的文件。sub_name视频文件名称，保存为sub_name.the_file_ext。
    # ext = file.split('.')[-1]
    try:  # 字幕压缩包有时是zip但实际是rar压缩格式，此处为了防止错误的扩展名压缩包
        f = rarfile.RarFile(file)
    except rarfile.BadRarFile:
        f = zipfile.ZipFile(file)
    f_list = []  # 字幕列表
    if len(f.infolist()) == 1:  # 当压缩包内只有一个文件时，那么就把该文件作为中文字幕文件
        f_list.append(f.infolist()[0].filename)
    else:
        for s in f.infolist():
            filename = s.filename
            # print(filename)
            if 'chs&eng' or '简体' or 'chs' or 'eng&chs' in filename:
                f_list.append(filename)

    try:
        the_file = f_list[0]  # 从字幕列表里抓取第一个文件名作为字幕
    except IndexError:
        print('No chs subs found')
        return None
    the_file_ext = f_list[0].split('.')[-1]  # 字幕扩展后缀名.srt
    print(color('{} >> {}.{}'.format(the_file, sub_name, the_file_ext)))
    f.extract(the_file)
    try:
        shutil.move(the_file, '{}.{}'.format(
            sub_name, the_file_ext))  # 移动文件到当前目录并重命名为影片名称
    except IndexError:
        print(color('rename file error', False))
    print('write sub file complate')


# main func
while True:
    sub_name = input('Input the movie name:')
    if len(sub_name) <= 3:
        print('error movie name')
    else:
        break

subs = Subs(sub_name).sub()
for index, sub in enumerate(subs, start=1):
    print(color(index), '<>', sub)

if subs:
    while True:
        sub_choose = input('Input download id:')  # 选择下载的字幕文件，不选择默认第一个
        try:
            if sub_choose == '':
                sub_choose = 1
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
                        print('', end='.', flush=True)
    print(color('download complate'))
    file = get_video_name()
    print('change to the same name as the sub')
    unc(local_filename, file)
else:
    print('subs not found')
