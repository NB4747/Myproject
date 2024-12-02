#!/usr/bin/python
# -*- coding:utf-8 -*-
import requests
import csv
import os
import jieba
import pandas as pd
import datetime as dt
from tkinter import _flatten
import matplotlib.pyplot as plt
from wordcloud import WordCloud
file_path = 'E:\数据采集实验课\comment_data.csv'
def pachong():
    fieldnames = ['content', 'creationTime', 'score', 'userClient', 'productSize', 'referenceTime', 'productColor','nickname',
                  'productSales', 'days']
    with open(file_path, mode='a', encoding='utf-8-sig', newline='') as f:
        csv_writer = csv.DictWriter(f, fieldnames=fieldnames)
        if os.path.getsize(file_path) == 0:
            csv_writer.writeheader()
        urls_id = ['100077097741']
        for url_id in urls_id:
            for i in range(0, 3):
                for j in range(1, 150):
                    url = f'https://club.jd.com/comment/productPageComments.action?&productId={url_id}&score={i}&sortType=5&page={j}&pageSize=10&isShadowSku=0&fold=1'
                    res = requests.get(url)
                    res.encoding = 'utf-8'
                    comments = res.json()['comments']
                    for k in comments:
                        data = {
                            'content': k['content'],
                            'creationTime': k['creationTime'],
                            'score': k['score'],
                            'userClient': k['userClient'],
                            'productSize': k['productSize'],
                            'referenceTime': k['referenceTime'],
                            'productColor': k['productColor'],
                            'nickname': k['nickname'],
                            'productSales': k['productSales'],
                            'days': k['days']
                        }
                        print(data)
                        csv_writer.writerow(data)

df = pd.DataFrame()
df = pd.read_csv(file_path,encoding='utf-8-sig')
df['creationTime'] = pd.to_datetime(df['creationTime'])
df['referenceTime'] = pd.to_datetime(df['referenceTime'])
#词云
def ciyun(df):
    data_cut = df['content'].apply(jieba.lcut)
    with open('E:\数据采集实验课\停用词.txt', encoding='utf-8') as f:
        stop_list = f.read()
        stop_list = stop_list + '\t\r\n手机&nbsp'
    data_after_stop = data_cut.apply(lambda x: [i for i in x if i not in stop_list])
    word_fre = pd.Series(_flatten(list(data_after_stop))).value_counts()
    wc = WordCloud(font_path='E:\数据采集实验课\中文字体\\fonts\中易隶书.TTF', background_color='white')
    wc.fit_words(word_fre)
    plt.imshow(wc)
    plt.axis('off')
    plt.show()
#好评词云 好评:5 中评:4 差评: 123
def good_comment():
    index_score5 = (df['score'] == 5)
    ciyun(df.loc[index_score5, :])
#不同颜色比例
def color(df):
    num = df['productColor'].value_counts()
    plt.rcParams['font.sans-serif'] = 'SimHei'
    plt.pie(num,labels=num.index,autopct="%.2f %%",colors=['#FFF5F7','#4F4B53','#465F86','#EAFEE8','#FF5D61'])
    plt.show()
#不同配置
def size(df):
    num = df['productSize'].value_counts()
    plt.pie(num,labels=num.index,autopct='%.2f%%')
    plt.show()

#销售数量和评论数量和日期的关系
def time(df):
    num = df['referenceTime'].dt.date.value_counts().sort_index()
    num2 = df['creationTime'].dt.date.value_counts().sort_index()
    data = pd.concat([num, num2], axis=1).fillna(0)
    plt.style.use('ggplot')
    plt.rcParams['font.sans-serif'] = 'SimHei'
    plt.plot(range(len(data)), data['referenceTime'])
    plt.plot(range(len(data)), data['creationTime'])
    plt.xticks(range(len(data))[::21], data.index[::21], rotation=45)
    plt.legend(['购买数量', '评论数量'])
    plt.xlabel('日期')
    plt.ylabel('数量')
    plt.title('销售数量和评论数量和日期的关系')
    plt.show()

#不同渠道的销售比例
def qudao(df):
    tmp = {21:"WX",2:"JDIPHONE",4:"JIAndroid",0:"JDPC",29:"JDiPad",1:"Phone_QQ"}
    num = df['userClient'].value_counts()
    plt.bar(range(len(num)),num)
    plt.rcParams['font.sans-serif'] = 'SimHei'
    plt.xticks(range(len(num)),[tmp[i] for i in num.index],rotation=45)
    plt.xlabel('渠道')
    plt.ylabel('数量')
    plt.title('不同渠道的销售比例')
    plt.show()