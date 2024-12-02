#!/usr/bin/python
# -*- coding:utf-8 -*-
import bag
import requests
import json
from selenium import webdriver

# 初始化Edge浏览器驱动，并设置为不自动关闭浏览器窗口（detach=True）
option = webdriver.EdgeOptions()
option.add_experimental_option("detach", True)
driver = webdriver.Edge(options=option)

def main():
    url = r'https://www.zhipin.com/wapi/zpCommon/data/cityGroup.json'

    # 使用已初始化的Edge浏览器驱动打开网页
    driver.get(url)
    session = requests.Session()
    page_source = driver.page_source
    resp = session.get(url)
    js_data = resp.json().get('zpData')
    group = js_data.get("cityGroup")
    city_dict = {}
    for city_group in group:
        # 遍历每个城市分组中的城市列表
        for city in city_group['cityList']:
            code = city['code']
            name = city['name']
            city_dict[name] = code
    with open('../city_codes.json', 'w', encoding='utf-8') as f:
        json.dump(city_dict,f,ensure_ascii=False)

if __name__ == "__main__":
    main()