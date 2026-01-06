from datetime import datetime

import requests
from bs4 import BeautifulSoup


def strip_html(html_content):
    parsed = BeautifulSoup(html_content, 'html.parser')
    return parsed.get_text()


def format_date(input_date):
    months = [
        "января", "февраля", "марта", "апреля", "мая", "июня",
        "июля", "августа", "сентября", "октября", "ноября", "декабря"
    ]

    dt = datetime.strptime(input_date, "%Y-%m-%dT%H:%M:%S%z")
    return f"{dt.day} {months[dt.month - 1]} {dt.year} года в {dt.strftime('%H:%M')}"


def fetch_exchange_rate(currency_code):
    if currency_code in ['RUR', 'RUB']:
        return 1

    api_url = "https://www.cbr-xml-daily.ru/daily_json.js"
    response = requests.get(api_url)
    data = response.json()

    if currency_code in data['Valute']:
        exchange_rate = data['Valute'][currency_code]['Value'] / data['Valute'][currency_code]['Nominal']
        return exchange_rate

    return None


def convert_currency(value, currency_code):
    rate = fetch_exchange_rate(currency_code)
    if rate:
        return value * rate
    return None


def process_salary(salary_data):
    salary_from = salary_data.get('from')
    salary_to = salary_data.get('to')
    currency_code = salary_data.get('currency')

    salary_from_rub = convert_currency(salary_from, currency_code) if salary_from else None
    salary_to_rub = convert_currency(salary_to, currency_code) if salary_to else None

    return {
        'from': round(salary_from_rub, 2) if salary_from_rub else None,
        'to': round(salary_to_rub, 2) if salary_to_rub else None,
        'currency': 'RUB'
    }
