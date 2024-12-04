from bs4 import BeautifulSoup
import bag
import requests
import json
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 基础网页
base_url = 'https://www.zhipin.com/web/geek/job?query={}&city={}'


def generate_url():
    query = input("请输入查询关键词：")
    city_code = input("请输入城市代码：")

    url = base_url.format(query, city_code)

    print(f"生成的网址为：{url}")
    return url


if __name__ == "__main__":
    generate_url()