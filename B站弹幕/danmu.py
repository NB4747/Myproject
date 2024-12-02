#!/usr/bin/python
# -*- coding:utf-8 -*-
import jieba
from bs4 import BeautifulSoup
import requests
import pandas as pd
import csv
from tkinter import _flatten
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from datetime import datetime
#爬虫
def pachong():
    url = 'https://comment.bilibili.com/1581931988.xml'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
    }
    reponse = requests.get(url, headers=headers)
    reponse.encoding = 'utf-8'
    soup = BeautifulSoup(reponse.text, 'xml')
    tmp = soup.select('d')
    comments = [i.text for i in tmp]
    info_else = [i.get('p').split(',') for i in tmp]
    columns = ['弹幕文本', '出现时间点', '模式', '字体', '颜色', '发送时间', '弹幕池', '用户ID', 'rowID','序号']
    with open('E:\\数据采集实验课\\bilibili_comments.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(columns)

        for i in range(len(comments)):
            writer.writerow([comments[i]] + info_else[i])
#词云
def ciyun():
    comments = pd.read_csv("E:\\数据采集实验课\\bilibili_comments.csv", encoding='utf-8-sig')
    comments['弹幕文本'] = comments['弹幕文本'].astype(str)
    comment_cut = comments['弹幕文本'].apply(jieba.lcut)
    with open('E:\数据采集实验课\停用词.txt', 'r', encoding='utf-8') as f:
        stop_words = f.read()
    stop_words += '\n'
    comment_after = comment_cut.apply(lambda x: [i for i in x if i not in stop_words])
    word_fre = pd.Series(_flatten(list(comment_after))).value_counts()
    word_cloud = WordCloud(background_color='white', font_path='E:\数据采集实验课\中文字体\\fonts\中易隶书.TTF')
    word_cloud.fit_words(word_fre)
    plt.imshow(word_cloud)
    plt.axis('off')
    plt.show()
#弹幕发布数量
def danmu_sum():
    comments = pd.read_csv("E:\\数据采集实验课\\bilibili_comments.csv", encoding='utf-8-sig')
    comments['发送时间'] = comments['发送时间'].apply(lambda x: datetime.fromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S'))
    comments['发送时间'] = pd.to_datetime(comments['发送时间'])
    num = comments['用户ID'].value_counts().value_counts().sort_index()
    num2 = list(num[:6])
    num2.append(num[6:].sum())
    plt.rcParams['font.sans-serif'] = 'SimHei'
    plt.bar(range(7), num2)
    plt.xticks(range(7), num2)
    plt.xlabel('弹幕数量')
    plt.ylabel('用户数量')
    plt.title('弹幕发布数量分布图')
    plt.show()

#弹幕发布数量随日期变化
def danmu_time():
    comments = pd.read_csv("E:\\数据采集实验课\\bilibili_comments.csv", encoding='utf-8-sig')
    comments['发送时间'] = comments['发送时间'].apply(lambda x: datetime.fromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S'))
    comments['发送时间'] = pd.to_datetime(comments['发送时间'])
    num = comments['发送时间'].dt.date.value_counts().sort_index()
    plt.rcParams['font.sans-serif'] = 'SimHei'
    plt.figure(figsize=(16,9))
    plt.plot(range(len(num)),num)
    plt.xticks(range(len(num))[::7],num.index[::7],rotation=45)
    plt.ylabel('弹幕数量')
    plt.title('弹幕发布数量随日期变化图')
    plt.show()
#弹幕发布数量周内分布
def danmu_week():
    comments = pd.read_csv("E:\\数据采集实验课\\bilibili_comments.csv", encoding='utf-8-sig')
    comments['发送时间'] = comments['发送时间'].apply(lambda x: datetime.fromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S'))
    comments['发送时间'] = pd.to_datetime(comments['发送时间'])
    num = comments['发送时间'].dt.dayofweek.map({0: '周一', 1: '周二', 2: '周三', 3: '周四', 4: '周五', 5: '周六', 6: '周日'}).value_counts()
    plt.style.use('ggplot')
    plt.rcParams['font.sans-serif'] = 'SimHei'
    plt.plot(range(len(num)), num)
    plt.xticks(range(len(num)), list(num.index))
    plt.title('弹幕发布数量周内分布')
    plt.ylabel('弹幕数量')
    plt.show()
