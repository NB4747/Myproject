from flask import Flask, render_template, request
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import json
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/图片展示')
def pic_show():
    return render_template('pic_show.html')

@app.route('/推荐系统', methods=['GET', 'POST'])
def recommend_system():
    if request.method == 'POST':
        user_preferences = {
            "city": request.form.get('city'),
            "degree": request.form.get('degree'),
            "experience": request.form.get('experience'),
            "keywords": request.form.get('keywords').split(',')
        }
        recommended_jobs, company_median_salary, company_max_salary, company_min_salary = job_recommendation(df, user_preferences)
        # 对company_max_salary进行处理，如果它不为空（不是None），则将其转换为字典，方便在模板中判断和取值
        if company_max_salary is not None:
            company_max_salary = company_max_salary.to_dict()
        # 同样对company_median_salary和company_min_salary进行类似处理
        if company_median_salary is not None:
            company_median_salary = company_median_salary.to_dict()
        if company_min_salary is not None:
            company_min_salary = company_min_salary.to_dict()
        return render_template('recommendation.html',
                               recommended_jobs=recommended_jobs[['职位名称', 'company_name', 'city', 'Avg_salary']],
                               company_median_salary=company_median_salary,
                               company_max_salary=company_max_salary,
                               company_min_salary=company_min_salary)
    return render_template('recommand_system.html')
def job_recommendation(df, user_preferences):
    if 'city' in user_preferences:
        df_filtered_city = df[df['city'] == user_preferences['city']]
    else:
        df_filtered_city = df
    if 'degree' in user_preferences:
        df_filtered_degree = df_filtered_city[df_filtered_city['学历'] == user_preferences['degree']]
    else:
        df_filtered_degree = df_filtered_city
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
    df_filtered_keywords.loc[:, 'combined_score'] = df_filtered_keywords['similarity'] + df_filtered_keywords[
        'Avg_salary'] / 10000
    recommended_jobs = df_filtered_keywords.sort_values(by='combined_score', ascending=False)
    recommended_jobs = recommended_jobs.drop_duplicates()
    print(recommended_jobs)
    # 计算筛选出的公司薪资的统计信息
    salary_stats = df_filtered_keywords['Avg_salary'].describe()
    median_salary = salary_stats['50%']
    max_salary = salary_stats['max']
    min_salary = salary_stats['min']
    # 根据中位数挑选一个公司
    try:
        company_median_salary = df_filtered_keywords.loc[df_filtered_keywords['Avg_salary'] == median_salary].iloc[0]
    except IndexError:
        print("根据中位数挑选公司时，未找到符合条件的公司，可能是数据为空或索引超出范围。")
        company_median_salary = None
    try:
        company_max_salary = df_filtered_keywords.loc[df_filtered_keywords['Avg_salary'] == max_salary].iloc[0]
    except IndexError:
        print("根据最大值挑选公司时，未找到符合条件的公司，可能是数据为空或索引超出范围。")
        company_max_salary = None
    try:
        company_min_salary = df_filtered_keywords.loc[df_filtered_keywords['Avg_salary'] == min_salary].iloc[0]
    except IndexError:
        print("根据最小值挑选公司时，未找到符合条件的公司，可能是数据为空或索引超出范围。")
        company_min_salary = None
    return recommended_jobs, company_median_salary, company_max_salary, company_min_salary


if __name__ == '__main__':
    df = pd.read_csv('E:\\三创赛资料\\boss_data.csv')
    df.drop_duplicates(keep='first', inplace=True)
    def format_site_data(data):
        parts = data.split('·')
        if len(parts) == 1:
            return f"{parts[0]} null null"
        elif len(parts) == 2:
            return f"{parts[0]} {parts[1]} null"
        return data
    df['地点'] = df['地点'].apply(format_site_data)
    df[['city', 'district', 'specific_place']] = df['地点'].str.split('·', expand=True)
    grouped_by_city = df.groupby('city')
    for city, city_group in grouped_by_city:
        grouped_by_district = city_group.groupby('district')
    df['Lowest_salary'] = df['salary'].str.extract('^(\d+).*')
    df['Highest_salary'] = df['salary'].str.extract('^.*?-(\d+).*')
    def process_salary_data(salary_str):
        if '·' in salary_str:
            match = re.search('^.*?·(\d{2})薪', salary_str)
            if match:
                return int(match.group(1)) - 12
        return 0
    df['extra_salary_times'] = df['salary'].apply(process_salary_data)
    # 将最低薪资，最高薪资，额外奖金数转换成数值形式
    df['Lowest_salary'] = df['Lowest_salary'].astype('int64')
    df['Highest_salary'] = df['Highest_salary'].astype('int64')
    df['extra_salary_times'] = df['extra_salary_times'].astype('int64')
    # 平均月薪
    df['Avg_salary'] = (((df['Lowest_salary'] + df['Highest_salary']) / 2) * (df['extra_salary_times'] + 12)) / 12
    # 奖金率
    df['extra_salary_percent'] = ((df['Lowest_salary'] + df['Highest_salary']) / 2 * df['extra_salary_times']) / (
                ((df['Lowest_salary'] + df['Highest_salary']) / 2) * (df['extra_salary_times'] + 12)) * 100
    df.describe()
    def IQR(df, columns):
        for col in columns:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            df[col] = df[col].apply(
                lambda x: lower_bound if x < lower_bound else (upper_bound if x > upper_bound else x))
        return df
    columns_IQR = ['Lowest_salary', 'Highest_salary', 'Avg_salary', 'extra_salary_percent']
    df = IQR(df, columns_IQR)
    split_year = df['year'].str.split('\n', expand=True)
    df['经验'] = split_year[0]
    df['学历'] = split_year[1]
    df['经验'] = df['经验'].str.replace('\r', '')
    df['学历'] = df['学历'].str.replace('\r', '')
    job_name_counts = df['职位名称'].value_counts()
    job_name_result = {}
    for job_name, count in job_name_counts.items():
        job_name_result[job_name] = count
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
        df.at[index, 'max_company_size'] = max_size
    df['combined_major'] = df['major_1'] + "/" + df['major_2']
    df['职位名称'] = df['职位名称'].astype(str)
    df['combined_major'] = df['combined_major'].astype(str)
    keywords = ['数据分析', 'python', 'java', 'SQL', '数据仓库', '数据挖掘', '计算机', 'Excel', 'SPSS', '统计',
                '大数据', '数学']
    with open('E:\三创赛资料\\boss直聘\.venv\My_Project\city_province.json', 'r', encoding='utf-8') as file:
        city_province_dict = json.load(file)
    app.run()