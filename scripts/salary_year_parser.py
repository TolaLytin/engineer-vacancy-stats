import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from concurrent.futures import ProcessPoolExecutor

file_path = "C:/Users/Daddy/Downloads/vacancies_2024.csv"
currency_data_path = './cache/currency.csv'
currency_data = pd.read_csv(currency_data_path)


def add_year_month_columns(dataframe):
    dataframe['year'] = pd.to_datetime(dataframe['published_at'], utc=True).dt.year.astype(str)
    dataframe['month'] = pd.to_datetime(dataframe['published_at'], utc=True).dt.month.astype(str)
    return dataframe


def process_vacancy_data(dataframe):
    # Удаляем строки с отсутствующей валютой зарплаты
    dataframe = dataframe.dropna(subset=['salary_currency']).copy()

    # Добавляем столбцы с годом и месяцем
    dataframe = add_year_month_columns(dataframe)

    # Вычисляем среднюю зарплату
    salary_min = dataframe['salary_from']
    salary_max = dataframe['salary_to']

    dataframe['average_salary'] = np.where(
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

    dataframe = dataframe.dropna(subset=['average_salary'])

    # Добавляем столбец даты для конвертации валюты
    dataframe['conversion_date'] = pd.to_datetime(
        dataframe['month'] + '-' + dataframe['year'],
        format='%m-%Y',
        errors='coerce'
    )

    dataframe['conversion_rate'] = 1
    non_rur_filter = dataframe['salary_currency'] != 'RUR'

    dataframe.loc[non_rur_filter, 'conversion_rate'] = dataframe.loc[non_rur_filter, 'conversion_date'].apply(
        lambda date: (
            currency_data.loc[currency_data['date'] == date, dataframe.loc[non_rur_filter, 'salary_currency']].values[0]
            if not currency_data.loc[currency_data['date'] == date].empty and
               dataframe.loc[non_rur_filter, 'salary_currency'].iloc[0] in currency_data.columns
            else 1
        )
    )

    dataframe['average_salary'] *= dataframe['conversion_rate']
    dataframe = dataframe[dataframe['average_salary'] <= 10000000]

    return dataframe.groupby('year')['average_salary'].mean().round(0).astype(int).to_dict()


def generate_salary_report():
    dataframe = pd.read_csv(file_path, encoding='utf-8-sig')

    keywords = ['engineer', 'инженер программист', 'інженер', 'it инженер', 'инженер разработчик',
                'Инженер-программист']
    dataframe = dataframe[dataframe['name'].str.contains('|'.join(keywords), case=False, na=False, regex=True)]

    with ProcessPoolExecutor() as executor:
        num_processes = 8
        dataframe_chunks = np.array_split(dataframe, num_processes)
        futures = [executor.submit(process_vacancy_data, chunk) for chunk in dataframe_chunks]

        aggregated_data = {}
        for future in futures:
            chunk_result = future.result()
            if chunk_result:
                for year, avg_salary in chunk_result.items():
                    if year in aggregated_data:
                        aggregated_data[year].append(avg_salary)
                    else:
                        aggregated_data[year] = [avg_salary]

    average_salaries = {year: np.mean(salaries) for year, salaries in aggregated_data.items()}
    result_table = pd.DataFrame(list(average_salaries.items()), columns=['Year', 'Average Salary'])

    save_html_report(result_table)

    return list(average_salaries.keys()), list(average_salaries.values())


def save_html_report(dataframe):
    html_content = dataframe.to_html(index=False, border=1, classes='dataframe', header=True)
    with open('./cache/salary_report.html', 'w', encoding='utf-8') as file:
        file.write(html_content)


if __name__ == "__main__":
    years, salaries = generate_salary_report()

    x_positions = np.arange(len(years))
    bar_width = 0.35

    plt.figure(figsize=(12, 8))
    plt.bar(x_positions, salaries, bar_width, label='Average Salary')

    ax = plt.gca()
    ax.set_title('Average Salaries by Year', fontsize=20)
    ax.tick_params(axis='y', labelsize=12)
    ax.set_xticks(x_positions)
    ax.set_xticklabels(years, rotation=90, fontsize=12)
    ax.legend(fontsize=12)
    ax.grid(True, axis='y')

    plt.savefig('./cache/average_salaries_chart.png')
