#!/usr/bin/python
# -*- coding:utf-8 -*-
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from config import *  # 配置文件config.py
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.common.exceptions import TimeoutException
import csv
import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Map,Bar,HeatMap
import matplotlib.pyplot as plt
def get_page_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        html_content = response.text
        soup_obj = BeautifulSoup(html_content, 'html.parser')
        data_div = soup_obj.find('div', "data_div")
        table = data_div.find('table')
        data_dict = {}
        for row in table.find_all('tr'):
            cells = row.find_all(['td'])
            if len(cells) == 2:
                data_name = cells[1].text.strip()
                data_value = cells[0].text.strip()
                data_dict[data_name] = data_value
        return data_dict
    except requests.exceptions.RequestException as e:
        print(f"请求出错: {e}")
        return {}
def get_country_data(base_url):
    all_countries_data = {}
    response = requests.get(f"{base_url}/cn/World")
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    select_tag = soup.find('select', id='selector_list')
    country_data = {}
    for option in select_tag.find_all('option')[1:]:
        country_data[option.text] = option['value']
    for country_name, country_url_suffix in list(country_data.items())[1:]:
        full_url = f"{base_url}{country_url_suffix}"
        country_data_dict = get_page_data(full_url)
        all_countries_data[country_name] = country_data_dict
    return all_countries_data
def get_country_name():
    url = "https://countrymeters.info/cn/China"
    response = requests.get(url)
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    select_tag = soup.find('select', id='selector_list')
    country_names = []
    for option in select_tag.find_all('option')[1:]:
        country_names.append(option.text)
    print(country_names)
if __name__ == '__main__':
    # base_url = 'https://countrymeters.info'
    # all_countries_data = get_country_data(base_url)
    # get_country_name()
    # all_keys = set()
    # for country_data in all_countries_data.values():
    #     all_keys.update(country_data.keys())
    # fieldnames = list(all_keys)
    # with open('E:\数据采集实验课\country.csv', 'w', newline='', encoding='utf-8') as csvfile:
    #     writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    #     writer.writeheader()
    #     for country_name, country_data in all_countries_data.items():
    #         writer.writerow(country_data)
    df = pd.read_csv('E:\数据采集实验课\人口.csv', encoding='GBK')
#     df.drop_duplicates(keep='first', inplace=True)
    df['目前的人口'] = df['目前的人口'].str.replace(" ", "").fillna(0).astype(int)
    df['目前的男性人口'] = df['目前的男性人口'].str.replace(" ", "").fillna(0).astype(int)
    df['当前女性人口'] = df['当前女性人口'].str.replace(" ", "").fillna(0).astype(int)
    df['今年出生的人口'] = df['今年出生的人口'].str.replace(" ", "").fillna(0).astype(int)
    df['今天出生的人口'] = df['今天出生的人口'].str.replace(" ", "").fillna(0).astype(int)
    df['今年死亡的人数'] = df['今年死亡的人数'].str.replace(" ", "").fillna(0).astype(int)
    df['今天死亡的人数'] = df['今天死亡的人数'].str.replace(" ", "").fillna(0).astype(int)
    df['净迁移今年'] = df['净迁移今年'].str.replace(" ", "").fillna(0).astype(int)
    df['今天的净迁移'] = df['今天的净迁移'].str.replace(" ", "").fillna(0).astype(int)
    df['人口增长今年'] = df['人口增长今年'].str.replace(" ", "").fillna(0).astype(int)
    df['人口增长的今天'] = df['人口增长的今天'].str.replace(" ", "").fillna(0).astype(int)
#     #世界人口分布热力图
#     country_population = df['目前的人口']
    country_name = [
"Bhutan",
"Timor-Leste",
"China",
"Central African Republic",
"Denmark",
"Ukraine",
"Uzbekistan",
"Uganda",
"Uruguay",
"Chad",
"Yemen",
"Armenia",
"Israel",
"Iraq",
"Iran",
"Belize",
"Cape Verde",
"Russia",
"Bulgaria",
"Croatia",
"Guam",
"Gambia",
"Iceland",
"Guinea",
"Guinea-Bissau",
"Liechtenstein",
"Congo",
"Democratic Republic of the Congo",
"Libya",
"Liberia",
"Canada",
"Ghana",
"Gabon",
"Hungary",
"North Macedonia",
"Northern Mariana Islands",
"South Sudan",
"South Africa",
"Botswana",
"Qatar",
"Rwanda",
"Luxembourg",
"Indonesia",
"India",
"Guatemala",
"Ecuador",
"Eritrea",
"Syria",
"Cuba",
"Taiwan, China",
"Kyrgyzstan",
"Djibouti",
"Kazakhstan",
"Colombia",
"Costa Rica",
"Cameroon",
"Reunion",
"Tuvalu",
"Turkmenistan",
"Turkey",
"Saint Lucia",
"Saint Kitts and Nevis",
"Saint Vincent and the Grenadines",
"Saint Pierre and Miquelon",
"Saint Helena",
"Saint Martin",
"San Marino",
"Guyana",
"United Republic of Tanzania",
"Egypt",
"Ethiopia",
"Kiribati",
"Tajikistan",
"Senegal",
"Serbia",
"Sierra Leone",
"Cyprus",
"Seychelles",
"Mexico",
"Togo",
"Dominica",
"Dominican Republic",
"Austria",
"Venezuela",
"Bangladesh",
"Angola",
"Anguilla",
"Antigua and Barbuda",
"Andorra",
"Federated States of Micronesia",
"Nicaragua",
"Nigeria",
"Niger",
"Nepal",
"Palestinian National Authority",
"Bahamas",
"Pakistan",
"Barbados",
"Papua New Guinea",
"Paraguay",
"Panama",
"Bahrain",
"Brazil",
"Burkina Faso",
"Burundi",
"Greece",
"Palau",
"Cook Islands",
"Curaçao",
"Cayman Islands",
"Germany",
"Germany",
"Italy",
"Solomon Islands",
"Latvia",
"Norway",
"Czech Republic",
"Republic of Moldova",
"Morocco",
"Monaco",
"Brunei",
"Fiji",
"Swaziland",
"Slovakia",
"Slovenia",
"Sri Lanka",
"Singapore",
"New Caledonia",
"New Zealand",
"Japan",
"Chile",
"Democratic People's Republic of Korea",
"Cambodia",
"Grenada",
"Greenland",
"Georgia",
"Belgium",
"Mauritania",
"Mauritius",
"Tonga",
"Saudi Arabia",
"France",
"French Guiana",
"French Polynesia",
"Faroe Islands",
"Poland",
"Puerto Rico",
"Bosnia and Herzegovina",
"Thailand",
"Zimbabwe",
"Honduras",
"Haiti",
"Channel Islands",
"Australia",
"Macau, China",
"Ireland",
"Estonia",
"Jamaica",
"Turks and Caicos Islands",
"Trinidad and Tobago",
"Bolivia",
"Nauru",
"Sweden",
"Switzerland",
"Guadeloupe",
"Wallis and Futuna Islands",
"Vanuatu",
"Belarus",
"Bermuda",
"Gibraltar",
"Kuwait",
"Comoros",
"Côte d'Ivoire",
"Kosovo",
"Peru",
"Tunisia",
"Lithuania",
"Somalia",
"Jordan",
"Namibia",
"Myanmar",
"Romania",
"United States",
"United States Virgin Islands",
"American Samoa",
"Laos",
"United Kingdom",
"Kenya",
"Finland",
"Sudan",
"Suriname",
"British Virgin Islands",
"Netherlands",
"Mozambique",
"Lesotho",
"Philippines",
"El Salvador",
"Samoa",
"Portugal",
"Mongolia",
"Montserrat",
"Western Sahara",
"Spain",
"Benin",
"Zambia",
"Equatorial Guinea",
"Vietnam",
"Azerbaijan",
"Afghanistan",
"Algeria",
"Albania",
"United Arab Emirates",
"Oman",
"Argentina",
"Aruba",
"South Korea",
"Hong Kong, China",
"Maldives",
"Isle of Man",
"Malawi",
"Martinique",
"Malaysia",
"Mayotte",
"Marshall Islands",
"Malta",
"Madagascar",
"Mali",
"Lebanon",
"Montenegro"
]
    df['国家名称'] = country_name
    # map_obj = Map(init_opts=opts.InitOpts(page_title="世界人口分布热力图", width="1000px", height="600px"))
    # cleaned_population = []
    # for population in list(df['目前的人口']):
    #     if isinstance(population, str):
    #         cleaned_population.append(int(population.replace(" ", "")))
    #     elif isinstance(population, float):
    #         cleaned_population.append(population)
    # data = [(str(name), population) for name, population in zip(list(df['国家名称']), cleaned_population)]
    # map_obj.add("World", data,"world")
    # map_obj.set_global_opts(
    #     title_opts=opts.TitleOpts(title="世界人口分布热力图"),
    #     visualmap_opts=opts.VisualMapOpts(
    #         is_show=True,
    #         min_=min(cleaned_population),
    #         max_=max(cleaned_population),
    #         textstyle_opts=opts.TextStyleOpts(color='#000')
    #     )
    # )
    # map_obj.render(path="世界人口.html")


    # #男女比例
    # male_sum = df['目前的男性人口'].sum()
    # female_sum = df['当前女性人口'].sum()
    # male_precent = male_sum/(male_sum+female_sum)
    # female_percent = female_sum/(male_sum+female_sum)
    # labels = ['man','woman']
    # sizes = [male_sum,female_sum]
    # plt.pie(sizes, labels=labels, autopct='%1.1f%%')
    # plt.axis('equal')
    # plt.title('男女比例',fontproperties='SimSun')
    # plt.show()
    #人口数前十的国家柱状图

    # population_sorted = df.sort_values(by='目前的人口',ascending=False)
    # top_ten_countries = population_sorted.head(10)
    # plt.bar(top_ten_countries['国家名称'], top_ten_countries['目前的人口'])
    # plt.xlabel('国家',fontproperties='SimSun')
    # plt.ylabel('人口数',fontproperties='SimSun')
    # plt.title('人口数排名前十的国家',fontproperties='SimSun')
    # plt.xticks(rotation=45)
    # plt.show()
    #前十国家的人口增长情况
    # population_sorted = df.sort_values(by='人口增长今年', ascending=False)
    # top_ten_countries = population_sorted.head(10)
    # plt.plot(top_ten_countries['国家名称'], top_ten_countries['人口增长今年'])
    # plt.xlabel('国家',fontproperties='SimSun')
    # plt.ylabel('人口增长数',fontproperties='SimSun')
    # plt.title('排名前十的国家人口增长情况',fontproperties='SimSun')
    # plt.xticks(rotation=45)
    # plt.show()
    # #死亡率最高的前十个国家的热力图
    # 计算死亡率
    # 计算死亡率
    df['死亡率'] = (df['今年死亡的人数'] / df['目前的人口']) * 1000

    # 找出死亡率排名前十的国家
    death_top_ten = df.sort_values(by='死亡率', ascending=False).head(10)

    # 提取死亡率排名前十的国家名称和死亡率数据
    death_top_ten_countries = death_top_ten[['国家名称', '死亡率']]

    # 创建地图对象并指定相关初始化选项
    map_obj = Map(
        init_opts=opts.InitOpts(page_title="世界前十死亡率分布", width="1000px", height="600px"))

    # 将死亡率数据转换为浮点数格式
    cleaned_death_rate = [float(death_rate) for death_rate in list(death_top_ten_countries['死亡率'])]

    # 组合数据为符合要求的格式
    data = [(str(name), death_rate) for name, death_rate in
            zip(list(death_top_ten_countries['国家名称']), cleaned_death_rate)]

    # 调用add方法添加数据
    map_obj.add("世界前十死亡率", data,"world")

    # 设置全局选项，包括可视化相关属性
    map_obj.set_global_opts(
        title_opts=opts.TitleOpts(title="世界前十死亡率分布"),
        visualmap_opts=opts.VisualMapOpts(
            is_show=True,
            min_=min(cleaned_death_rate),
            max_=max(cleaned_death_rate),
            textstyle_opts=opts.TextStyleOpts(color='#000')
        )
    )

    # 渲染地图并保存为html文件
    map_obj.render(path="../世界前十死亡率.html")
