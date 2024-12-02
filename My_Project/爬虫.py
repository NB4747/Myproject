import math
import re
from selenium import webdriver
import time
from datetime import datetime
import json
import random
import requests
import pandas as pd
from bs4 import BeautifulSoup
# 在这里导入浏览器设置相关的类
from config import *  # 配置文件config.py
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.common.exceptions import TimeoutException


# 无可视化界面设置 #
edge_options = Options()
# 禁用GPU，防止无头模式出现莫名的BUG
edge_options.add_argument('--disable-gpu')
edge_options.add_argument("--no-sandbox")
edge_options.add_argument("--disable-dev-shm-usage")
edge_options.add_argument("--window-size=1920x1080")
edge_options.add_argument("--hide-scrollbars")


def send_qywx_message():  # 需要验证时企业微信出提示
    # 当需要验证时，向企业微信发送提示消息
    proxies = {}
    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    webhook = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=ec928c22-a06e-41d8-928a-e3644968487d'
    header = {"Content-Type": "application/json"}
    message = {
        "msgtype": "markdown",
        "markdown": {
            "content":
                f"#{current_time}\n\n"
                f"Go to verify"
        }}
    message_json = json.dumps(message)
    send_message = requests.post(url=webhook, data=message_json, headers=header, proxies=proxies)  # $#


def wait_for_element(element, url, max_count):
    # 等待指定元素在网页上出现的函数。
    max_attempts = max_count
    # 用于计数
    attempt = 0
    while attempt < max_attempts:
        try:
            element_present = EC.presence_of_element_located((By.CLASS_NAME, f'{element}'))
            # 等待直到元素出现，或者直到达到最大尝试次数
            WebDriverWait(boss, 10).until(element_present)
            # 若元素出现，跳出循环
            break
        except TimeoutException:
            # 如果在指定时间内元素没有出现，重置计数器并等待一段时间
            attempt += 1
            print(f"Attempt {attempt} failed, retrying...")
            # 如果已经达到最大尝试次数，抛出异常
            if attempt == max_attempts:
                raise TimeoutException("Element not found within the maximum number of attempts.")
            # 等待一段时间后重试
            time.sleep(5)
            if ("Click to verify" in boss.page_source or "You are temporarily unable to continue accessing" in boss.page_source):
                print("Verification required")
                send_qywx_message()
                input()
                boss.get(url)
                time.sleep(5)
                break


def start_crawling(url):
    job_names = []
    locations = []
    salaries = []
    job_keywords = []
    education_requirements = []
    job_years = []
    company_names = []
    company_industries = []
    company_sizes = []
    company_links = []
    job_links = []
    count = 0
    boss.get(url)
    time.sleep(0.5)

    # 等待页面加载完成（根据需要调整等待时间）
    wait_for_element('job-name', url, 5)
    job_names.extend([item.text for item in boss.find_elements(By.CLASS_NAME, 'job-name')])
    locations.extend([item_text for item in boss.find_elements(By.CLASS_NAME, 'job-area-wrapper')])
    salaries.extend([item.text for item in boss.find_elements(By.CLASS_NAME, 'salary')])
    job_keywords.extend([','.join([li.text for li in ul.find_elements(By.TAG_NAME, 'li')]) for ul in
                        boss.find_elements(By.CSS_SELECTOR, "div.job-card-footer.clearfix ul")])
    for ul in boss.find_elements(By.CSS_SELECTOR, "div.job-info.clearfix ul"):
        li_texts = [li.text for li in ul.find_elements(By.TAG_NAME, 'li')]
        job_years.append(li_texts[0] if li_texts else None)
        education_requirements.append(li_texts[1] if len(li_texts) > 1 else None)  # 假设学历要求是第二个li元素
    company_names.extend([item.text for item in boss.find_elements(By.CSS_SELECTOR, '.company-info.company-name')])
    ul_elements = boss.find_elements(By.CSS_SELECTOR, "div.company-info ul")
    for ul in ul_elements:
        li_texts = [li.text for li in ul.find_elements(By.TAG_NAME, 'li')]
        company_industries.append(li_texts[0] if li_texts else None)
        company_sizes.append(li_texts[-1] if li_texts else None)
    company_links = [a.get_attribute('href') for a in boss.find_elements(By.CSS_SELECTOR, "div.company-logo a")]
    job_links = [a.get_attribute('href') for a in boss.find_elements(By.XPATH, "//a[@class='job-card-left']")]
    print('Number of jobs',
          len(job_names)
          # len(locations), len(salaries), len(job_keywords), len(education_requirements), len(job_years), len(company_names), len(company_industries), len(company_sizes), len(company_links), len(job_links)
          )
    df1 = pd.DataFrame({
        'job_link': job_links,
        'job_name': job_names,
        'job_years': job_years,
        'education_requirement': education_requirements,
        'salary': salaries,
        'location': locations,
        'job_keyword': job_keywords,
        'company_name': company_names,
        'company_link': company_links,
        'company_size': company_sizes,
        'company_industry': company_industries
    })
    return df1


# start_crawling('https://www.zhipin.com/web/geek/job?query=BI数据分析&city=101250100&areaBusiness=430103&areaBusiness=430103&experience=101,103,104&degree=209,208,206,202,203&page=9')


# 设置最大尝试次数和每次尝试的间隔时间
def get_corresponding_job_info(corresponding_page_table, save_folder_path):
    print("Start crawling job information")
    for city_code in keys_as_strings:
        df1 = pd.DataFrame(
            columns=['job_link', 'job_name', 'job_years', 'salary', 'location', 'job_keyword', 'company_name', 'company_link', 'company_size',
                     'education_requirement',
                     'company_industry'])
        page_start = 1
        # 获取页码值，如果没有匹配的行，则默认为None
        page_values = corresponding_page_table[corresponding_page_table['city_code'] == city_code]['page_number'].values
        page_end = page_values[0] if len(page_values) > 0 else None
        if page_end is None or math.isnan(page_end):
            continue
        for i in range(page_start, int(page_end) + 1):
            url = f'https://www.zhipin.com/web/geek/job?query={jobs[0]}&city={city_code}&experience= {experience}&degree={degree}&page={i}'
            print(url)
            df1 = pd.concat([df1, start_crawling(url)], axis=0)
        # 处理数据
        def convert_low(salary_str):
            if '-' in salary_str:
                # 如果包含'-'，取分割后的第一部分
                return salary_str.split('-')[0]
            else:
                # 如果不包含'-'，直接返回
                return salary_str
        def convert_high(salary_str):
            # 使用正则表达式匹配 '-' 后面的字符（直到 'k' 或字符串的结尾）
            match = re.search(r'-(\d+)K', salary_str)
            if match:
                return match.group(1)
            else:
                # 如果没有 匹配，说明格式可能是 '15k'，直接返回数字部分
                return salary_str
        # 应用函数并创建新列
        try:
            df1['lowest_salary'] = df1['salary'].apply(convert_low)
            df1['highest_salary'] = df1['salary'].apply(convert_high)
        except Exception:
            pass
        df1.to_csv(f"{save_folder_path}/{citys[city_code]}_job_info.csv")
        print(f"{save_folder_path}/{citys[city_code]}_job_info.csv", 'Saved successfully')


def get_job_responsibilities(save_folder_path):
    try:
        for city_code in keys_as_strings:
            start_time = datetime.now()  # 获取当前时间
            print('----------------------------------------------------')
            print(f'Start time: {start_time} Start crawling {citys[city_code]} job information')

            try:
                df = pd.read_csv(f"{save_folder_path}/{citys[city_code]}_job_info.csv")
            except Exception:
                df = pd.read_csv(f"{save_folder_path}/{citys[city_code]}_job_info.csv", encoding='gbk')
            count = 0
            amount = len(df['job_link'])
            job_descriptions = []
            total_time_spent = 0
            for i in df['job_link']:
                start_time = datetime.now()  # 获取当前时间
                count = count + 1
                print(f'Link {count}: {i}')
                boss.get(i)
                wait_for_element('job-sec-text', i, 5)
                text = [
                    [elem.text for elem in boss.find_elements(By.CSS_SELECTOR, 'div.job-detail-section.job-sec-text')][
                        0]]
                print(f"Job responsibility {count}: {text}")
                job_descriptions.extend(text)
                end_time = datetime.now()
                single_time_spent = float(f"{(end_time - start_time).total_seconds():.2f}")
                total_time_spent = round(total_time_spent + single_time_spent, 2)
                remaining_count = amount - count
                average_single_time = round(total_time_spent / count, 2)
                estimated_time = round(average_single_time * remaining_count / 60, 2)
                print(f'{count}---Total: {amount}, Progress: {count}, Completion percentage: {(count / amount * 100):.3f}%, Single time spent: {single_time_spent} s, Total time spent: {total_time_spent}s, Estimated time: {estimated_time}m')

            df['job_description'] = job_descriptions
            df.to_csv(f"{save_folder_path}/{citys[city_code]}_job_info_with_description.csv")
    except Exception:
        print('Failed to save to prevent errors')
        df.to_csv(f"{save_folder_path}/{citys[city_code]}_job_info_with_description.csv")


def get_cookie():
    url = 'https://www.zhipin.com/web/geek/job-recommend'
    cookie_file_name = f"{root_directory}\\boss_zhipin_cookie.json"
    boss.get(url)
    input("Wait for login:")
    # 1. 获取cookies
    cookies = boss.get_cookies()
    cookies_json = json.dumps(cookies, indent=4)
    # 2. 登录完成后,将cookies保存到本地文件
    with open(cookie_file_name, "w") as file:
        file.write(cookies_json)
    print("Cookies have been saved to cookies.json file")


if __name__ == "__main__":
    boss = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()), options=edge_options)
    save_folder_path = "your_folder_path"
    keys_as_strings = ["101010000", "101020000", "101030000"]  # 示例，需根据实际情况替换
    jobs = ["软件工程师", "数据分析师", "产品经理"]  # 示例，需根据实际情况替换
    experience = "101,103,104"  # 示例，需根据实际情况替换
    degree = "209,208,206,202,203"  # 示例，需根据实际情况替换
    citys = {"101010000": "北京", "101020000": "上海", "101030000": "广州"}  # 示例，需根据实际情况替换
    root_directory = "your_root_directory"  # 示例，需根据实际情况替换

    # 获取对应页码表，这里假设已经有获取对应页码表的逻辑，示例中暂未给出具体实现
    corresponding_page_table = pd.DataFrame({
        'city_code': ["101010000", "101020000", "101030000"],
        'page_number': ["10", "8", "6"]
    })

    get_corresponding_job_info(corresponding_page_table, save_folder_path)
    get_job_responsibilities(save_folder_path)
    get_cookie()