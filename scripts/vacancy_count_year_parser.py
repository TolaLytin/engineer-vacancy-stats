import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from concurrent.futures import ProcessPoolExecutor

file_path = "C:/Users/Daddy/Downloads/vacancies_2024.csv"


def add_year_column(dataframe):
    dataframe['year'] = pd.to_datetime(dataframe['published_at'], utc=True).dt.year.astype(str)
    return dataframe


def analyze_vacancy_data(dataframe):
    dataframe_copy = dataframe.copy()
    dataframe_copy = add_year_column(dataframe_copy)

    # Подсчет общего количества вакансий по годам
    yearly_vacancy_count = dataframe_copy.groupby('year')['name'].count().to_dict()

    return yearly_vacancy_count


def generate_report():
    # Чтение данных целиком
    dataframe = pd.read_csv(file_path, dtype={1: str}, encoding='utf-8-sig')

    keywords = ['engineer', 'инженер программист', 'інженер', 'it инженер', 'инженер разработчик',
                'Инженер-программист']
    dataframe = dataframe[dataframe['name'].str.contains('|'.join(keywords), case=False, na=False, regex=True)]

    # Обработка данных в пуле процессов
    with ProcessPoolExecutor() as executor:
        # Разделяем DataFrame на несколько частей для параллельной обработки
        num_processes = 8  # Количество процессов
        dataframe_splits = np.array_split(dataframe, num_processes)
        futures = [executor.submit(analyze_vacancy_data, split) for split in dataframe_splits]

        # Собираем результаты
        combined_vacancy_count = {}

        for future in futures:
            partial_vacancy_count = future.result()
            for year, count in partial_vacancy_count.items():
                combined_vacancy_count[year] = combined_vacancy_count.get(year, 0) + count

    # Подготовка данных для HTML-таблицы
    summary_table = pd.DataFrame(list(combined_vacancy_count.items()), columns=['Year', 'Vacancy Count'])

    # Сохранение таблицы в HTML
    save_table_as_html(summary_table)

    # Подготовка данных для графиков
    years = list(combined_vacancy_count.keys())
    vacancy_counts = list(combined_vacancy_count.values())

    return years, vacancy_counts


def save_table_as_html(dataframe):
    # Преобразуем DataFrame в HTML-таблицу
    html_content = dataframe.to_html(index=True, border=1, classes='dataframe', header=True)

    with open('./cache/vacancy_report.html', 'w', encoding='utf-8-sig') as file:
        file.write(html_content)

    return html_content


if __name__ == "__main__":
    # Генерация отчета и получение данных для графиков
    years_list, vacancy_counts_list = generate_report()

    # Настройка осей
    x_positions = np.arange(len(years_list))  # Позиции по оси X
    bar_width = 0.35  # Ширина столбцов

    # Создание фигуры и подграфиков
    plt.figure(figsize=(12, 8))

    # График количества вакансий по годам
    plt.bar(x_positions, vacancy_counts_list, bar_width, label='Vacancy Count')

    # Настройка заголовка и меток осей
    plt.title('Vacancy Count by Year', fontsize=16)
    plt.xticks(x_positions, years_list, rotation=90, fontsize=10)  # Установка меток по оси X
    plt.legend(fontsize=10)
    plt.grid(True, axis='y')

    # Сохранение графика в файл
    plt.savefig('./cache/vacancy_report_chart.png')
