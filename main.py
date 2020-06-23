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

    _scores = []  # 暂存字幕评分

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
                                        f'sub_id={sub_id},vote_score={color(vote_score)},videoname={videoname}')
                                    Subs._scores.append(vote_score)
            return subs_list
        else:
            return None

    def sub_score(self):
        return Subs._scores


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
            s_filename = s.filename
            # print(filename)
            try:
                _m = re.search('chs&eng|简体|chs|中文', s_filename)
                # print(_m.group(0))
                f_list.append(s_filename)
            except AttributeError:
                print('.', end='', flush=True)

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
    print('写入字幕文件成功')


# main func
while True:
    sub_name = input('Input the movie name:')
    if sub_name == '':
        print('探测当前目录下的视频文件')
        video_name = get_video_name()
        # print(video_name)
        if video_name is not None:  # 如果videoname不是空，那么进行正则判断
            try:
                video_name_s = re.search(
                    '(\w*\.)*\d{4}\.', video_name)  # 获取视频文件的搜索关键字
                sub_name = video_name_s.group(0)[:-1]  # 排除小数点
                print(color('检索到视频关键字为：{}'.format(sub_name)))
                break
            except AttributeError or TypeError:
                print('未搜索到正则关键词，尝试使用视频名称进行搜索')
                sub_name = video_name
                break
        else:
            print('请输入视频名称')
    else:
        video_name = sub_name  # 当前目录下没有找到视频文件时，使用输入的名称作为字幕文件
        break

subs_list = Subs(sub_name)
subs = subs_list.sub()
subs_scores = subs_list.sub_score()
for index, sub in enumerate(subs, start=1):
    print(color(index), '<>', sub)

if subs:
    while True:
        sub_choose = input('选择要下载的字幕id，回车自动选择评分最高字幕：')  # 选择下载的字幕文件，不选择默认第一个
        try:
            if sub_choose == '':
                for sub_id, _i in enumerate(subs_scores, start=1):
                    if _i == max(subs_scores):
                        sub_choose = sub_id
                        break
            if int(sub_choose) >= 1 and int(sub_choose) <= len(subs):
                print('choose id: {}'.format(sub_choose))
                sub_choose = int(sub_choose)
                break
            else:
                print('input error')
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
    print('正在重命名字幕文件')
    unc(local_filename, video_name)
else:
    print('subs not found')
