#!/usr/bin/python
# -*- coding:utf-8 -*-
import os.path

import requests
from lxml import etree

#gif
def gif():
    url = 'https://wimg.588ku.com/gif620/24/09/05/c373794b59f9d20f81df87b0a7d07e8e.gif'
    res = requests.get(url)
    with open('./test.gif', mode='wb') as f:
        f.write(res.content)
#mp4
def mp4():
    url = 'https://bpic.588ku.com/video_listen/588ku_video/23/09/25/18/19/38/video65115eba93d15.mp4'
    res = requests.get(url)
    with open('./test.mp4', mode='wb') as f:
        f.write(res.content)
#爬起整个网页的图片
def all_picture():
    for i in range(2, 5):
        url = f'https://588ku.com/gif/0-0-0-default-{i}/'
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0'
        }
        res = requests.get(url, headers=header)
        dom = etree.HTML(res.text)
        gifurl = dom.xpath('//*[@class="only-imgbox"]/img/@data-original')
        if 'https:' not in gifurl[0]:
            gifurl = ['https:' + i for i in gifurl]
        filepath = './data'
        if not os.path.exists(filepath):
            os.mkdir(filepath)
        for i in gifurl:
            oneurl = i
            name = oneurl.split('/')[-1]
            res1 = requests.get(oneurl)
            with open(f'{filepath}/{name}', mode='wb') as f:
                f.write(res1.content)

