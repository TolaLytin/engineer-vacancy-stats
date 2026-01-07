import pandas as pd

TARGET_CURRENCIES = ["BYR", "USD", "EUR", "KZT", "UAH", "AZN", "KGS", "UZS", "GEL"]

start_period = pd.to_datetime('2003-01-01')
end_period = pd.to_datetime('2025-01-01')
date_range_list = pd.date_range(start=start_period, end=end_period, freq='MS').strftime('%d/%m/%Y')

def fetch_currency_data(date_string):
    source_url = f"http://www.cbr.ru/scripts/XML_daily.asp?date_req={date_string}"
    currency_data = pd.read_xml(source_url, xpath=".//Valute", encoding="windows-1251")

    if currency_data is not None and not currency_data.empty:
        currency_data['date'] = pd.to_datetime(date_string, format='%d/%m/%Y').strftime('%Y-%m')
        currency_data = currency_data[currency_data['CharCode'].isin(TARGET_CURRENCIES)]
        currency_data['Value'] = pd.to_numeric(currency_data['Value'].str.replace(',', '.'), errors='coerce')
        currency_data['Nominal'] = pd.to_numeric(currency_data['Nominal'], errors='coerce')
        currency_data['normalized_rate'] = round(currency_data['Value'] / currency_data['Nominal'], 9)

        return currency_data[['date', 'CharCode', 'normalized_rate']]

    return pd.DataFrame(columns=['date', 'CharCode', 'normalized_rate'])

aggregated_data = []
for idx, single_date in enumerate(date_range_list):
    processed_data = fetch_currency_data(single_date)
    if not processed_data.empty:
        aggregated_data.append(processed_data)

final_dataframe = pd.concat(aggregated_data, ignore_index=True)
pivot_table = final_dataframe.pivot(index='date', columns='CharCode', values='normalized_rate')
pivot_table = pivot_table[TARGET_CURRENCIES]
pivot_table.to_csv("./cache/currency_rates.csv")
