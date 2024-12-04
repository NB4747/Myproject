#!/usr/bin/python
# -*- coding:utf-8 -*-
import pandas as pd
import re
from pyecharts import options as opts
from pyecharts.charts import Map,Bar,HeatMap
import json
import sys
import io
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import seaborn as sns
from wordcloud import WordCloud
import jieba
from tkinter import _flatten
import torch
import torch.nn as nn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from torch.utils.data import Dataset, DataLoader

# 设置显示所有列
pd.set_option('display.max_columns', None)
# 设置显示所有行
pd.set_option('display.max_rows', None)
# 设置显示宽度为一个较大的值
pd.set_option('display.width', 1000)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
#读取数据
df = pd.read_csv('E:\\三创赛资料\\boss_data.csv')
#数据清洗
#去除重复值
df.drop_duplicates(keep='first',inplace=True)
#进行城市分类
#将site列分成 城市，区，具体地点 三列
#规范数据
def format_site_data(data):
    parts = data.split('·')
    if len(parts) == 1:
        return f"{parts[0]} null null"
    elif len(parts) == 2:
        return f"{parts[0]} {parts[1]} null"
    return data
df['地点'] = df['地点'].apply(format_site_data)
df[['city','district','specific_place']] = df['地点'].str.split('·',expand=True)
#进行第一次分类
grouped_by_city = df.groupby('city')
#遍历城市分组
for city,city_group in grouped_by_city:
    grouped_by_district = city_group.groupby('district')
    # print(f"城市:{city}")
    # for district, district_group in grouped_by_district:
    #     print(f"    区: {district}")
    #     print(district_group[['specific_place']])
#将薪资进行拆分，新增最低薪资和最高薪资两列，作为一个岗位的最低值和最高值
df['Lowest_salary']=df['salary'].str.extract('^(\d+).*')
df['Highest_salary']=df['salary'].str.extract('^.*?-(\d+).*')
#额外奖金数
def process_salary_data(salary_str):
    if '·' in salary_str:
        match = re.search('^.*?·(\d{2})薪', salary_str)
        if match:
            return int(match.group(1)) - 12
    return 0
df['extra_salary_times'] = df['salary'].apply(process_salary_data)
#将最低薪资，最高薪资，额外奖金数转换成数值形式
df['Lowest_salary']=df['Lowest_salary'].astype('int64')
df['Highest_salary']=df['Highest_salary'].astype('int64')
df['extra_salary_times']=df['extra_salary_times'].astype('int64')
#平均月薪
df['Avg_salary']=(((df['Lowest_salary']+df['Highest_salary'])/2)*(df['extra_salary_times']+12))/12
#奖金率
df['extra_salary_percent'] = ((df['Lowest_salary'] + df['Highest_salary']) / 2 * df['extra_salary_times']) / (((df['Lowest_salary'] + df['Highest_salary']) / 2) * (df['extra_salary_times'] + 12)) * 100
#异常值处理
df.describe()
#用IQR方法处理异常值
def IQR(df, columns):
    for col in columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        df[col] = df[col].apply(lambda x: lower_bound if x < lower_bound else (upper_bound if x > upper_bound else x))
    return df
columns_IQR = ['Lowest_salary', 'Highest_salary', 'Avg_salary', 'extra_salary_percent']
df = IQR(df, columns_IQR)
#统计工作经验要求
split_year = df['year'].str.split('\n',expand = True)
df['经验'] = split_year[0]
df['学历'] = split_year[1]
df['经验'] = df['经验'].str.replace('\r', '')
df['学历'] = df['学历'].str.replace('\r', '')
# print(df['经验'])
#统计职位名称
job_name_counts = df['职位名称'].value_counts()
job_name_result = {}
for job_name,count in job_name_counts.items():
    job_name_result[job_name] = count
#公司最大规模
df['max_company_size'] = None
for index, row in df.iterrows():
    value = row['company_size']
    numbers = re.findall(r'\d+', value)
    if len(numbers) == 2:
        max_size = max(int(numbers[0]), int(numbers[1]))
    elif len(numbers) == 1:
        max_size = int(numbers[0])
    else:
        max_size = None
    df.at[index,'max_company_size'] = max_size
# print(df['max_company_size'])
#公司福利
jieba.load_userdict("E:\三创赛资料\\benefit.txt")
df['benefit'] = df['benefit'].astype(str)
benefit_cut = df['benefit'].apply(jieba.lcut)
with open('E:\数据采集实验课\停用词.txt', 'r', encoding='utf-8') as f:
    stop_words = f.read()
stop_words += '\n'
benefit_after = benefit_cut.apply(lambda x: [i for i in x if i not in stop_words])
def _flatten(lst):
    return [item for sublist in lst for item in sublist]
word_fre = pd.Series(_flatten(list(benefit_after))).value_counts()
# print(word_fre)
# 计算每个城市的平均薪资(从高到低排序)
def every_city_salary(df):
    def clean_city_name(city_name):
        return city_name.split(" ")[0]
    df['city'] = df['city'].apply(clean_city_name)
    city_avg_salary = df.groupby('city')['Avg_salary'].mean()
    city_avg_salary_df = pd.DataFrame(city_avg_salary).reset_index()
    city_avg_salary_df.columns = ['city', 'Avg_salary']
    city_avg_salary_df.sort_values(by='Avg_salary', ascending=False, inplace=True)
    bar_chart = Bar()
    bar_chart.add_xaxis(city_avg_salary_df['city'].tolist())
    bar_chart.add_yaxis("平均薪资", city_avg_salary_df['Avg_salary'].tolist())
    bar_chart.set_global_opts(
        title_opts=opts.TitleOpts(title="各城市平均薪资柱形图"),
        xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-45)),  # 设置x轴标签旋转角度，避免重叠
        yaxis_opts=opts.AxisOpts(name="平均薪资(数值)")
    )
    bar_chart.render(path="E:\三创赛资料\\boss直聘\.venv\My_Project\\flask\static\各城市平均薪资柱形图.html")

# 计算每个区的平均薪资
def every_district_salary(df):
    district_avg_salary = df.groupby(['city', 'district'])['Avg_salary'].mean()
    district_avg_salary_df = pd.DataFrame(district_avg_salary).reset_index()
    district_avg_salary_df.columns = ['city', 'district', 'Avg_salary']
    district_avg_salary_df.sort_values(by='Avg_salary', ascending=False, inplace=True)
    # 绘制柱状图
    # 绘制每个区平均薪资的柱形图，实现同一城市的区分组展示
    bar_chart_district = Bar()
    city_districts_data = {}
    for index, row in district_avg_salary_df.iterrows():
        city = row['city']
        district = row['district']
        avg_salary = row['Avg_salary']
        if city not in city_districts_data:
            city_districts_data[city] = []
        city_districts_data[city].append({"区": district, "平均薪资": avg_salary})
    for city, data in city_districts_data.items():
        district_names = [item['区'] for item in data]
        avg_salary_values = [item['平均薪资'] for item in data]

        bar_chart_district.add_xaxis(district_names)
        bar_chart_district.add_yaxis(city, avg_salary_values)
    bar_chart_district.set_global_opts(
        title_opts=opts.TitleOpts(title="各市区平均薪资柱形图"),
        xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-45)),  # 设置x轴标签旋转角度，避免重叠
        yaxis_opts=opts.AxisOpts(name="平均薪资(数值)"),
        legend_opts=opts.LegendOpts(
            orient='vertical',
            pos_right='0%',
            item_width=10,  # 设置图例项的宽度，可根据需要调整
            item_height=10,  # 设置图例项的高度，可根据需要调整
            textstyle_opts=opts.TextStyleOpts(font_size=5)  # 修改后的设置图例文本样式的方式
        )
    )
    bar_chart_district.render(path="E:\三创赛资料\\boss直聘\.venv\My_Project\\flask\static\各市区平均薪资柱形图.html")
# 计算每个具体地点的平均薪资
def every_specific_place_salary(df):
    specific_place_avg_salary = df.groupby(['city', 'district', 'specific_place'])['Avg_salary'].mean()
    specific_place_avg_salary_df = pd.DataFrame(specific_place_avg_salary).reset_index()
    specific_place_avg_salary_df.columns = ['city', 'district', 'specific_place', 'Avg_salary']
    specific_place_avg_salary_df.sort_values(by='Avg_salary', ascending=False, inplace=True)
    print("每个具体地点的平均薪资:")
    print(specific_place_avg_salary_df)
#绘制热力图
def avg_salary_map(df):
    # 城市与省份对应字典
    with open('E:\三创赛资料\\boss直聘\.venv\My_Project\city_province.json', 'r', encoding='utf-8') as file:
        city_province_dict = json.load(file)
    # 将城市映射到对应省份并生成新的数据格式
    def clean_city_name(city_name):
        return city_name.split(" ")[0]
    df['city'] = df['city'].apply(clean_city_name)
    city_avg_salary = df.groupby('city')['Avg_salary'].mean()
    city_avg_salary_df = pd.DataFrame(city_avg_salary).reset_index()
    city_avg_salary_df.columns = ['city', 'Avg_salary']
    city_avg_salary_df.sort_values(by='Avg_salary', ascending=False, inplace=True)
    mapped_data = [(city_province_dict[city], salary) for city, salary in
                   zip(city_avg_salary_df['city'], city_avg_salary_df['Avg_salary'])]
    province_distribution = {}
    for province, salary in mapped_data:
        if province in province_distribution:
            province_distribution[province] += salary
        else:
            province_distribution[province] = salary
    provice = list(province_distribution.keys())
    values = list(province_distribution.values())
    map = Map()
    map.add(
        series_name="",
        data_pair=list(zip(provice, values)),
        maptype='china'
    )
    map.set_global_opts(
        title_opts=opts.TitleOpts(title="中国地图"),
        visualmap_opts=opts.VisualMapOpts(min_=0, max_=75)
    )
    map.render(path="E:\三创赛资料\\boss直聘\.venv\My_Project\\flask\static\平均薪资.html")
#岗位数量分析
#合并major_1和major_2
df['combined_major'] = df['major_1'] + "/" + df['major_2']
#转换成字符串
df['职位名称'] = df['职位名称'].astype(str)
df['combined_major'] = df['combined_major'].astype(str)
#要统计的关键字列表
keywords = ['数据分析', 'python', 'java', 'SQL', '数据仓库', '数据挖掘', '计算机', 'Excel', 'SPSS', '统计', '大数据', '数学']
def job_sum(df):
    keyword_count = {keyword: 0 for keyword in keywords}
    for index, row in df.iterrows():
        for keyword in keywords:
            if keyword in row['职位名称'] or keyword in row['combined_major']:
                keyword_count[keyword] += 1
    # 将统计结果转换为数据框形式以便更好地查看
    result_df = pd.DataFrame.from_dict(keyword_count, orient='index', columns=['出现次数'])
    #绘制柱形图
    plt.rcParams['font.sans-serif'] = 'SimHei'
    plt.bar(result_df.index, result_df['出现次数'])
    plt.title('各关键字在职位相关列中出现次数统计')
    plt.xlabel('关键字')
    plt.ylabel('出现次数')
    plt.xticks(rotation=45)
    plt.savefig('E:\三创赛资料\\boss直聘\.venv\My_Project\\flask\static\statickeyword_count_chart.png')
    plt.show()
# 城市与省份对应字典
with open('E:\三创赛资料\\boss直聘\.venv\My_Project\city_province.json', 'r', encoding='utf-8') as file:
    city_province_dict = json.load(file)
#关键字在各城市的比重
def key_city_pro(df):
    result_df = pd.DataFrame(columns=['province', 'keyword', 'count'])
    for province in set(city_province_dict.values()):
        province_cities = [city for city, prov in city_province_dict.items() if prov == province]
        province_data = df[df['city'].isin(province_cities)]
        for keyword in keywords:
            count = ((province_data['职位名称'].str.contains(keyword)) | (
                province_data['combined_major'].str.contains(keyword))).sum()
            new_row = pd.DataFrame([[province, keyword, count]], columns=['province', 'keyword', 'count'])
            result_df = pd.concat([result_df, new_row], ignore_index=True)
    # 统计每个城市的所有关键字之和
    province_keyword_sum = result_df.groupby('province')[['count']].sum()
    province_keyword_sum = province_keyword_sum.reset_index()
    province_keyword_sum.rename(columns={'count': 'keyword_sum'}, inplace=True)
    #画出各城市的比重饼图
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.pie(province_keyword_sum['keyword_sum'], labels=province_keyword_sum['province'], autopct='%1.1f%%')
    plt.title('各省份关键字总和占比情况')
    plt.savefig('E:\三创赛资料\\boss直聘\.venv\My_Project\\flask\static\key_city_pro')
    plt.show()
#关键字的词云
def key_ciyun(df):
    result_df = pd.DataFrame(columns=['keyword', 'count_sum'])
    for keyword in keywords:
        count_sum = 0
        for province in set(city_province_dict.values()):
            province_cities = [city for city, prov in city_province_dict.items() if prov == province]
            province_data = df[df['city'].isin(province_cities)]
            count = ((province_data['职位名称'].str.contains(keyword)) | (
                province_data['combined_major'].str.contains(keyword))).sum()
            count_sum += count
        new_row = pd.DataFrame([[keyword, count_sum]], columns=['keyword', 'count_sum'])
        result_df = pd.concat([result_df, new_row], ignore_index=True)
    # 绘制词云
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    text = " ".join([f"{keyword} {count_sum}" for keyword, count_sum in zip(result_df['keyword'], result_df['count_sum'])])
    wordcloud = WordCloud(font_path='msyh.ttc',width=800, height=600, background_color='white', collocations=False).generate(text)
    plt.figure(figsize=(10, 8))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('各关键字在各省份出现次数之和词云')
    plt.savefig('E:\三创赛资料\\boss直聘\.venv\My_Project\\flask\static\key_ciyun')
    plt.show()
#统计不同关键字的平均薪资
def key_salary(df):
    result_df = pd.DataFrame(columns=['keyword', 'key_average_salary'])
    for keyword in keywords:
        keyword_data = df[((df['职位名称'].str.contains(keyword)) | (df['combined_major'].str.contains(keyword)))]
        key_average_salary = keyword_data['Avg_salary'].mean()
        result_df = result_df._append({
            'keyword': keyword,
            'key_average_salary': key_average_salary
        }, ignore_index=True)
    # 绘制柱状图
    plt.figure(figsize=(10, 6))
    plt.rcParams['font.sans-serif'] = 'SimHei'
    plt.bar(result_df['keyword'], result_df['key_average_salary'])
    plt.xlabel('关键字')
    plt.ylabel('平均薪资')
    plt.title('各关键字平均薪资柱状图')
    plt.xticks(rotation=45)
    plt.savefig('E:\三创赛资料\\boss直聘\.venv\My_Project\\flask\static\key_salary')
    plt.show()
#公司规模与薪资关系
def city_size_salary(df):
    df = df.dropna(subset=['max_company_size', 'Avg_salary'])
    df['max_company_size'] = df['max_company_size'].astype('category')
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    g = sns.boxplot(data=df, x='max_company_size', y='Avg_salary')
    g.set_title('公司规模与平均薪资关系箱线图')
    g.set_xlabel('公司规模')
    g.set_ylabel('平均薪资')
    plt.savefig('E:\三创赛资料\\boss直聘\.venv\My_Project\\flask\static\city_size_salary')
    plt.show()
#公司福利
#有无福利的公司比例
def if_have_benefit(df):
    df = pd.read_csv('E:\\三创赛资料\\boss_data.csv')
    df['is_benefit'] = df['benefit'].notna()
    benefit_count = df['is_benefit'].value_counts()
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.pie(benefit_count, labels=benefit_count.index, autopct='%1.1f%%', startangle=90)
    plt.title('有福利和无福利的公司占比')
    plt.savefig('E:\三创赛资料\\boss直聘\.venv\My_Project\\flask\static\if_have_benefit')
    plt.show()
#出现次数大于8000的福利词汇分布
def company_benefit(df):
    words_more_than_2000 = word_fre[word_fre > 8000]
    # print(words_more_than_2000)
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.bar(words_more_than_2000.index, words_more_than_2000.values)
    plt.title('出现次数大于8000的福利词汇分布')
    plt.xlabel('福利词汇')
    plt.ylabel('出现次数')
    plt.xticks(rotation=45)
    plt.savefig('E:\三创赛资料\\boss直聘\.venv\My_Project\\flask\static\company_benefit')
    plt.show()
#职位学历情况
def job_degree(df):
    degree_count = df['学历'].value_counts()
    target_degrees = ['本科', '大专', '硕士', '学历不限', '中专/中技', '高中', '博士']
    filtered_degree_frequencies = degree_count[degree_count.index.isin(target_degrees)]
    total_count = filtered_degree_frequencies.sum()
    average_salary_dict = {}
    for degree in target_degrees:
        degree_salary_data = df[df['学历'] == degree]['Avg_salary']
        if not degree_salary_data.empty:
            average_salary = degree_salary_data.mean()
            average_salary_dict[degree] = average_salary
        else:
            average_salary_dict[degree] = 0
    # print(average_salary_dict)
    degree_percentage_ratios = (filtered_degree_frequencies / total_count) * 100
    wedges, texts, autotexts = plt.pie(degree_percentage_ratios, labels=[''] * len(degree_percentage_ratios),autopct='%1.1f%%',startangle=90)
    legend_labels = [f"{degree} ({count:.1f}%)" for degree, count in zip(degree_percentage_ratios.index,degree_percentage_ratios.values)]
    plt.legend(wedges, legend_labels, loc='best')
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.title('各学历在职位中的占比情况')
    plt.savefig('E:\三创赛资料\\boss直聘\.venv\My_Project\\flask\static\job_degree_pie')
    # 柱状图 不同学历薪资情况
    plt.figure(figsize=(10, 6))
    bar_positions = range(len(target_degrees))
    plt.bar(bar_positions, [average_salary_dict[degree] for degree in target_degrees], tick_label=target_degrees)
    plt.xlabel('学历')
    plt.ylabel('平均工资')
    plt.xticks(rotation=45)
    plt.savefig('E:\三创赛资料\\boss直聘\.venv\My_Project\\flask\static\job_degree_bar')
    plt.show()
#职位经验情况
def job_exp(df):
    exp_count = df['经验'].value_counts()
    target_exp = ['1-3年', '3-5年', '经验不限', '5-10年', '1年以内', '在校/应届', '10年以上']
    filtered_exp_frequencies = exp_count[exp_count.index.isin(target_exp)]
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.figure(figsize=(10, 6))
    bar_positions = range(len(target_exp))
    plt.bar(bar_positions, filtered_exp_frequencies, tick_label=target_exp)
    plt.xlabel('工作经验')
    plt.ylabel('出现次数')
    plt.xticks(rotation=45)
    plt.title('各工作经验在职位中的出现次数')
    plt.savefig('E:\三创赛资料\\boss直聘\.venv\My_Project\\flask\static\job_exp')
    plt.show()
def job_recommendation(df, user_preferences):
    """
    根据用户偏好对岗位数据进行筛选，并结合机器学习技术（文本向量化和余弦相似度计算）找到与用户偏好最相似的岗位，
    最后按照综合得分（相似度和平均薪资）从高到低排序返回推荐岗位列表，同时根据筛选出的公司薪资的平均数、中位数、
    最大数、最小数，各挑选出一个对应的公司。

    :param df: 包含岗位信息的原始数据框，已经过数据清洗
    :param user_preferences: 用户偏好字典，包含期望的工作地点、学历、经验、关键字等信息
    :return: 按照综合得分降序排序后的推荐岗位列表，以及根据薪资统计信息挑选出的四个公司信息
    """
    # 按照用户期望的工作地点筛选岗位
    if 'city' in user_preferences:
        df_filtered_city = df[df['city'] == user_preferences['city']]
    else:
        df_filtered_city = df
    #按照用户期望的学历筛选岗位
    if 'degree' in user_preferences:
        df_filtered_degree = df_filtered_city[df_filtered_city['学历'] == user_preferences['degree']]
    else:
        df_filtered_degree = df_filtered_city
    #按照用户期望的经验筛选岗位
    if 'experience' in user_preferences:
        df_filtered_experience = df_filtered_degree[df_filtered_degree['经验'] == user_preferences['experience']]
    else:
        df_filtered_experience = df_filtered_degree
    job_text_features = df_filtered_experience[['职位名称', 'combined_major']].astype(str)
    job_text = job_text_features.apply(lambda x: " ".join(x), axis=1)
    vectorizer = TfidfVectorizer()
    job_text_vectors = vectorizer.fit_transform(job_text)
    user_keywords = user_preferences.get('keywords', [])
    user_text = " ".join(user_keywords)
    user_text_vector = vectorizer.transform([user_text])
    similarity_scores = cosine_similarity(job_text_vectors, user_text_vector)
    df_filtered_experience.loc[:, 'similarity'] = similarity_scores.flatten()
    if user_keywords:
        df_filtered_keywords = df_filtered_experience[df_filtered_experience['similarity'] > 0]
    else:
        df_filtered_keywords = df_filtered_experience
    df_filtered_keywords.loc[:, 'combined_score'] = df_filtered_keywords['similarity'] + df_filtered_keywords['Avg_salary'] / 10000
    recommended_jobs = df_filtered_keywords.sort_values(by='combined_score', ascending=False)
    recommended_jobs = recommended_jobs.drop_duplicates()
    print(recommended_jobs)
    # 计算筛选出的公司薪资的统计信息
    salary_stats = df_filtered_keywords['Avg_salary'].describe()
    average_salary = salary_stats['mean']
    median_salary = salary_stats['50%']
    max_salary = salary_stats['max']
    min_salary = salary_stats['min']
    # 根据中位数挑选一个公司
    try:
        company_median_salary = df_filtered_keywords.loc[df_filtered_keywords['Avg_salary'] == median_salary].iloc[0]
    except IndexError:
        print("根据中位数挑选公司时，未找到符合条件的公司，可能是数据为空或索引超出范围。")
        company_median_salary = None
    # 根据最大值挑选一个公司
    try:
        company_max_salary = df_filtered_keywords.loc[df_filtered_keywords['Avg_salary'] == max_salary].iloc[0]
    except IndexError:
        print("根据最大值挑选公司时，未找到符合条件的公司，可能是数据为空或索引超出范围。")
        company_max_salary = None
    # 根据最小值挑选一个公司
    try:
        company_min_salary = df_filtered_keywords.loc[df_filtered_keywords['Avg_salary'] == min_salary].iloc[0]
    except IndexError:
        print("根据最小值挑选公司时，未找到符合条件的公司，可能是数据为空或索引超出范围。")
        company_min_salary = None

    return recommended_jobs, company_median_salary, company_max_salary, company_min_salary
# 用户
user_preferences = {
    "city": "北京",
    "degree": "本科",
    "experience": "1-3年",
    "keywords": ["数据分析", "python"]
}
recommended_jobs, company_median_salary, company_max_salary, company_min_salary = job_recommendation(df, user_preferences)

print("推荐岗位列表：")
print(recommended_jobs[['职位名称', 'company_name', 'city', 'Avg_salary']])
if company_median_salary is not None:
    print("根据中位数挑选的公司：")
    print(company_median_salary[['职位名称', 'company_name', 'city', 'Avg_salary']])
if company_max_salary is not None:
    print("根据最大值挑选的公司：")
    print(company_max_salary[['职位名称', 'company_name', 'city', 'Avg_salary']])
if company_min_salary is not None:
    print("根据最小值挑选的公司：")
    print(company_min_salary[['职位名称', 'company_name', 'city', 'Avg_salary']])