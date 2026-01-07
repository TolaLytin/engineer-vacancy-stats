import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from concurrent.futures import ProcessPoolExecutor

input_file_path = "C:/Users/Daddy/Downloads/vacancies_2024.csv"
TOTAL_VACANCIES_COUNT = 6915298  # Общее количество вакансий


def process_chunk_data(data_chunk):
    # Подсчет количества вакансий по городам
    city_vacancy_counts = data_chunk.groupby('area_name')['name'].count().reset_index(name='vacancy_count')
    return city_vacancy_counts


def analyze_city_vacancy_data(data):
    # Считаем общее количество вакансий по городам
    total_city_vacancies = data.groupby('area_name')['vacancy_count'].sum().reset_index()

    # Фильтруем города, где количество вакансий больше порога
    filtered_data = total_city_vacancies[total_city_vacancies['vacancy_count'] > 69153].copy()

    # Считаем долю вакансий от общего числа
    filtered_data['vacancy_share'] = filtered_data['vacancy_count'] / TOTAL_VACANCIES_COUNT

    # Учет оставшихся данных в категории "Другие", если сумма долей < 1
    if filtered_data['vacancy_share'].sum() < 1:
        other_share = 1 - filtered_data['vacancy_share'].sum()
        other_row = pd.DataFrame({'area_name': ['Другие'], 'vacancy_share': [other_share]})
        filtered_data = pd.concat([filtered_data, other_row], ignore_index=True)

    # Сортировка по доле вакансий и выбор топ-10 городов
    top_cities_data = filtered_data.sort_values(by='vacancy_share', ascending=False).head(10)

    return top_cities_data[['area_name', 'vacancy_share']]  # Возвращаем только нужные столбцы


def generate_vacancy_report():
    # Чтение данных целиком
    data = pd.read_csv(input_file_path, dtype={1: str}, encoding='utf-8-sig')

    keywords = ['engineer', 'инженер программист', 'інженер', 'it инженер', 'инженер разработчик',
                'Инженер-программист']
    data = data[data['name'].str.contains('|'.join(keywords), case=False, na=False, regex=True)]

    # Обработка данных в пуле процессов
    with ProcessPoolExecutor() as executor:
        # Разделяем DataFrame на несколько частей для параллельной обработки
        num_processes = 8  # Количество процессов
        data_chunks = np.array_split(data, num_processes)
        futures = [executor.submit(process_chunk_data, chunk) for chunk in data_chunks]

        # Собираем результаты
        combined_data = pd.DataFrame()  # Для объединения данных по городам
        for future in futures:
            chunk_result = future.result()
            combined_data = pd.concat([combined_data, chunk_result], ignore_index=True)

    # Анализ данных по городам
    filtered_city_data = analyze_city_vacancy_data(combined_data)

    # Сохранение сгруппированных данных в HTML
    save_grouped_data_to_html(filtered_city_data)

    # Подготовка данных для графиков по городам
    city_names = list(filtered_city_data['area_name'])
    vacancy_shares = list(filtered_city_data['vacancy_share'])

    return city_names, vacancy_shares


def save_grouped_data_to_html(grouped_data):
    # Преобразуем сгруппированный DataFrame в HTML-таблицу
    html_content = grouped_data.to_html(index=True, border=1, classes='dataframe', header=True)

    with open('./cache/city_vacancy_report.html', 'w', encoding='utf-8-sig') as file:
        file.write(html_content)

    return html_content


if __name__ == "__main__":
    # Получение данных для построения графиков
    city_labels, vacancy_shares = generate_vacancy_report()  # Предполагается, что функция возвращает два списка: города и доли вакансий

    # Создание фигуры с заданным размером
    plt.figure(figsize=(12, 8))  # Установка размера фигуры: ширина 12 дюймов, высота 8 дюймов

    # График доли вакансий по городам
    plt.pie(vacancy_shares, labels=city_labels, autopct='%1.1f%%',
            textprops={'fontsize': 14})  # Добавлен параметр autopct для отображения процентов
    plt.title('Доля вакансий по городам', fontsize=24)  # Установка заголовка с размером шрифта

    # Сохранение графика в файл
    plt.savefig('./cache/city_vacancy_report.png')
