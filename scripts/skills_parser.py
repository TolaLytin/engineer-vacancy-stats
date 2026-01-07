import numpy as np
import pandas as pd
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from matplotlib import pyplot as plt

# Путь к файлу с данными
CSV_FILE_PATH = "C:/Users/Daddy/Downloads/vacancies_2024.csv"

def analyze_skills(data_chunk):
    """Обрабатывает часть данных для подсчета навыков."""
    data_chunk = data_chunk.copy()

    # Удаляем строки, где 'key_skills' отсутствуют
    data_chunk = data_chunk.dropna(subset=['key_skills'])

    # Считаем упоминания навыков
    skill_counter = Counter()
    data_chunk['key_skills'].str.split('\n').apply(skill_counter.update)

    return skill_counter

def generate_report():
    """Генерирует отчет о наиболее частых навыках."""
    # Читаем данные из файла
    vacancy_data = pd.read_csv(CSV_FILE_PATH, dtype={1: str}, encoding='utf-8-sig')

    # Фильтруем вакансии по ключевым словам
    search_keywords = ['engineer', 'инженер программист', 'інженер', 'it инженер',
                       'инженер разработчик', 'Инженер-программист']
    filtered_data = vacancy_data[vacancy_data['name'].str.contains('|'.join(search_keywords),
                                                                  case=False, na=False, regex=True)]

    # Разделяем данные для параллельной обработки
    with ProcessPoolExecutor() as executor:
        num_processes = 8
        data_chunks = np.array_split(filtered_data, num_processes)
        future_results = [executor.submit(analyze_skills, chunk) for chunk in data_chunks]

        # Суммируем результаты всех процессов
        aggregated_skill_counter = Counter()
        for future in future_results:
            aggregated_skill_counter.update(future.result())

    # Выбираем топ-20 навыков
    top_skills = aggregated_skill_counter.most_common(20)

    # Формируем DataFrame с результатами
    skills_table = pd.DataFrame(top_skills, columns=['Skill', 'Frequency'])

    # Сохраняем таблицу в HTML
    save_table_to_html(skills_table)

    return skills_table

def save_table_to_html(table_df):
    """Сохраняет таблицу навыков в HTML файл."""
    html_content = table_df.to_html(index=False, border=1, classes='dataframe', header=True)

    with open('./cache/top20_skills.html', 'w', encoding='utf-8-sig') as file:
        file.write(html_content)

    return html_content

if __name__ == "__main__":
    # Генерируем отчет о навыках
    skills_df = generate_report()

    # Построение графика
    plt.figure(figsize=(16, 10))
    plt.barh(skills_df['Skill'], skills_df['Frequency'], color='skyblue')

    # Добавляем заголовки и подписи
    plt.title('Top-20 Skills', fontsize=24)
    plt.xlabel('Frequency of Mention', fontsize=14)
    plt.ylabel('Skill', fontsize=14)

    # Инвертируем ось Y, чтобы самый частый навык был сверху
    plt.gca().invert_yaxis()

    plt.tight_layout()
    plt.savefig('./cache/top20_skills.png')
