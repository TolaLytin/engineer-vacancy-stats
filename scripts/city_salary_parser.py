from multiprocessing import Manager
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from concurrent.futures import ProcessPoolExecutor

input_file = "C:/Users/Daddy/Downloads/vacancies_2024.csv"
currency_data_path = './cache/currency.csv'
currency_rates = pd.read_csv(currency_data_path)


def add_year_and_month(data):
    data['year'] = pd.to_datetime(data['published_at'], utc=True).dt.year.astype(str)
    data['month'] = pd.to_datetime(data['published_at'], utc=True).dt.month.astype(str)
    return data


def fetch_exchange_rate(row):
    date = row['date']
    currency = row['salary_currency']

    if currency in currency_rates.columns:
        rate_row = currency_rates.loc[currency_rates['date'] == date]
        if not rate_row.empty:
            rate_value = rate_row[currency].values[0]
            if pd.isnull(rate_value):
                return None
            return rate_value

    return 1


def process_chunk(data_chunk):
    data_chunk = data_chunk.dropna(subset=['area_name']).copy()
    city_vacancy_counts = {}

    for city in data_chunk['area_name']:
        city_vacancy_counts[city] = city_vacancy_counts.get(city, 0) + 1

    data_chunk = data_chunk.dropna(subset=['salary_currency']).copy()
    data_chunk = add_year_and_month(data_chunk)

    salary_min = data_chunk['salary_from']
    salary_max = data_chunk['salary_to']

    data_chunk['date'] = pd.to_datetime(data_chunk['month'] + '-' + data_chunk['year'], format='%m-%Y', errors='coerce')

    data_chunk['average_salary'] = np.where(
        salary_min.isna() & salary_max.isna(),
        np.nan,
        np.where(
            salary_min.isna(),
            salary_max,
            np.where(
                salary_max.isna(),
                salary_min,
                (salary_min + salary_max) / 2
            )
        )
    )

    data_chunk = data_chunk.dropna(subset=['average_salary'])
    data_chunk['exchange_rate'] = 1
    non_rub_mask = data_chunk['salary_currency'] != 'RUR'

    data_chunk.loc[non_rub_mask, 'exchange_rate'] = data_chunk[non_rub_mask].apply(fetch_exchange_rate, axis=1)
    data_chunk = data_chunk[data_chunk['exchange_rate'].notnull()]
    data_chunk['average_salary'] *= data_chunk['exchange_rate']

    data_chunk = data_chunk[data_chunk['average_salary'] <= 10000000]

    return data_chunk, city_vacancy_counts


def analyze_cities(data, city_counts):
    grouped_data = data.groupby('area_name').agg(mean_salary=('average_salary', 'mean')).reset_index()

    grouped_data = grouped_data[grouped_data['area_name'].apply(
        lambda city: city_counts[city] > 0.01 * sum(city_counts.values())
    )]

    grouped_data['mean_salary'] = grouped_data['mean_salary'].round(0).astype(int)
    top_cities = grouped_data.sort_values('mean_salary', ascending=False).head(10)

    return top_cities[['area_name', 'mean_salary']]


def generate_report():
    data = pd.read_csv(input_file, dtype={1: str}, encoding='utf-8-sig')
    keywords = ['engineer', 'инженер программист', 'інженер', 'it инженер', 'инженер разработчик',
                'Инженер-программист']

    data = data[data['name'].str.contains('|'.join(keywords), case=False, na=False, regex=True)]

    manager = Manager()
    total_city_counts = manager.dict()

    with ProcessPoolExecutor() as executor:
        num_processes = 8
        data_chunks = np.array_split(data, num_processes)
        futures = [executor.submit(process_chunk, chunk) for chunk in data_chunks]

        combined_data = pd.DataFrame()
        for future in futures:
            chunk_data, chunk_city_counts = future.result()
            combined_data = pd.concat([combined_data, chunk_data], ignore_index=True)

            for city, count in chunk_city_counts.items():
                total_city_counts[city] = total_city_counts.get(city, 0) + count

    top_city_data = analyze_cities(combined_data, dict(total_city_counts))
    save_to_html(top_city_data)

    cities = list(top_city_data['area_name'])
    salaries = list(top_city_data['mean_salary'])

    return cities, salaries


def save_to_html(data):
    html_content = data.to_html(index=True, border=1, classes='dataframe', header=True)
    with open('./cache/city_salary_report.html', 'w', encoding='utf-8-sig') as file:
        file.write(html_content)
    return html_content


if __name__ == "__main__":
    city_names, city_salaries = generate_report()

    plt.figure(figsize=(12, 8))
    plt.barh(city_names, city_salaries)
    plt.title('Average Salaries by City', fontsize=20)

    axes = plt.gca()
    for label in axes.get_yticklabels():
        label.set_ha('right')
        label.set_va('center')

    axes.invert_yaxis()
    plt.grid(True, axis='x')
    plt.tick_params(axis='y', labelsize=10)
    plt.tick_params(axis='x', labelsize=12)

    plt.savefig('./cache/city_salary_report.png')
