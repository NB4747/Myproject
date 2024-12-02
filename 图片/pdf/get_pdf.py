#!/usr/bin/python
# -*- coding:utf-8 -*-
import requests
from lxml import etree
import re
import os
import time
import  img2pdf
url = 'https://max.book118.com/html/2021/1211/6023032135004113.shtm'
res = requests.get(url)
dom = etree.HTML(res.text)
pages = dom.xpath('//*[@class="intro-list"]/li[4]/span/text()')
for num in pages:
    page = int(re.findall(r'\d+', num)[0])
filepath = 'data/testpdf'
# if not os.path.exists(filepath):
#     os.makedirs(filepath)
n = 1
for i in range(1,page+1,6):
    pageurl = 'https://openapi.book118.com/getPreview.html'
    params = {
        'project_id': '1',
        'aid': '445591520',
        't': '5cebd87883aecd23fcb18e921474f7a6',
        'view_token': 'IYDJASwFhcbkOUua8aAE41bvSaLLDryF',
        'page': i,
        'callback': 'jQuery18305079713406886095_1642835007746'
    }
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
        'Cookie': 'PHPSESSID=1iun67l40f1kf8vulujlqt7oi4; detail_show_similar=0; Hm_lvt_27fe35f56bdde9c16e63129d678cd236=1732951349; HMACCOUNT=C275985FEF50E448; Hm_lvt_f32e81852cb54f29133561587adb93c1=1732951349; a_6023032135004113=1; s_v=cdh%3D%3Ec865f4f0%7C%7C%7Cvid%3D%3E1732951350382548896%7C%7C%7Cfsts%3D%3E1732951350%7C%7C%7Cdsfs%3D%3E0%7C%7C%7Cnps%3D%3E1; s_rfd=cdh%3D%3Ec865f4f0%7C%7C%7Ctrd%3D%3Emax.book118.com%7C%7C%7Cftrd%3D%3Ebook118.com; s_s=cdh%3D%3Ec865f4f0%7C%7C%7Clast_req%3D%3E1732951350%7C%7C%7Csid%3D%3E1732951350256729727%7C%7C%7Cdsps%3D%3E0; CLIENT_SYS_UN_ID=3rvhcmdKvTdwypoaFNiJAg==; Hm_lpvt_27fe35f56bdde9c16e63129d678cd236=1732951359; Hm_lpvt_f32e81852cb54f29133561587adb93c1=1732951359; PREVIEWHISTORYPAGES=445591520_3; Book118UserFlag=%7B%22445591520%22%3A1732954935%7D; Book118UserFlag__ckMd5=bc0ba861f048a08b'
    }
    onepage = requests.get(pageurl, params=params,headers=header)
    pagedict = eval(re.findall('{.+}', onepage.text)[0])
    imgurl = pagedict['data'].values()
    imgurl = ['https:' + j.replace('\\', '') for j in imgurl]
    for k in imgurl:
        print(f'正在爬取第{n}页')
        imgtext = requests.get(k).content
        with open(f'{filepath}/{n}.jpg', mode='wb') as f:
            f.write(imgtext)
        n = n + 1
    time.sleep(2)
files = os.listdir(filepath)
filefict = {int(i.split('.')[0]):i for i in files}
files = [filefict[i] for i in sorted(filefict)]
files = ['./data/testpdf/'+i for i in files]
with open('data/testpdf.pdf', mode='wb') as f:
    f.write(img2pdf.convert(files))