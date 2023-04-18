
import numpy as np
import pandas as pd
import os
from dotenv import load_dotenv
import requests
import time

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset


import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.io as pio
#pio.renderers.default = 'notebook_connected'

from alpha_vantage.timeseries import TimeSeries

print("All libraries loaded")




load_dotenv() 

aplha_vantage_key = os.getenv("ALPHA_VANTAGE_KEY")



config = {
    "alpha_vantage": {
        "key": aplha_vantage_key,
        "symbol": "IBM",
        "outputsize": "full",
        "key_adjusted_close_stock_price": "5. adjusted close",
        "trading_volume": "6. volume",
    },
}




def download_stock_data_raw(config):
    ts = TimeSeries(key=config["alpha_vantage"]["key"])  

    data, meta_data = ts.get_daily_adjusted(config["alpha_vantage"]["symbol"], outputsize=config["alpha_vantage"]["outputsize"])
    
    data_date = [date for date in data.keys()]
    data_date.reverse()

    data_close_price = [float(data[date][config["alpha_vantage"]["key_adjusted_close_stock_price"]]) for date in data.keys()]


    data_close_price.reverse()
    data_close_price = np.array(data_close_price)

    num_data_points = len(data_date)
    display_date_range = "from " + data_date[0] + " to " + data_date[num_data_points-1]
    print("Number data points", num_data_points, display_date_range)

    return data_date, data_close_price, num_data_points, display_date_range


def download_stock_data_df(config):
    ts = TimeSeries(key=config["alpha_vantage"]["key"])  

    data, meta_data = ts.get_daily_adjusted(config["alpha_vantage"]["symbol"], outputsize=config["alpha_vantage"]["outputsize"])
    
    data = pd.DataFrame(data).T

    data.rename(columns = {config["alpha_vantage"]["key_adjusted_close_stock_price"]: "key_adjusted_close_stock_price",
                           config["alpha_vantage"]["trading_volume"]: "trading_volume"},
                           inplace = True)

    data.index = pd.to_datetime(data.index)
    data.index.name = "date"

    data = data.loc[:, ["key_adjusted_close_stock_price", "trading_volume"]]

    return data





def download_stock_data_df(**kwargs):

    key = kwargs.get("key")
    stock_symbol = kwargs.get("symbol")
    outputsize = kwargs.get("outputsize")
    key_adjusted_close_stock_price = kwargs.get("key_adjusted_close_stock_price")
    trading_volume = kwargs.get("trading_volume")

    ts = TimeSeries(key = key)  

    data, meta_data = ts.get_daily_adjusted(stock_symbol, outputsize = outputsize)
    
    data = pd.DataFrame(data).T

    data.rename(columns = {key_adjusted_close_stock_price: "key_adjusted_close_stock_price",
                           trading_volume: "trading_volume"},
                           inplace = True)

    data = data.loc[:, ["key_adjusted_close_stock_price", "trading_volume"]]


    data.index = pd.to_datetime(data.index)
    data.index.name = "trading_date"

    return data




download_stock_data_df(**config["alpha_vantage"])



df_usa_stocks = pd.read_csv("data/usa_stocks.csv")





# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&symbol=IBM&apikey={aplha_vantage_key}'


fundamental_data = ['OVERVIEW', 'INCOME_STATEMENT', 'BALANCE_SHEET', 'CASH_FLOW']
stock_symbol = [
    'AA', 'AAC', 'AACG', 'AACI', 'AACIW', 'AADI', 'AAIC', 'AAIN', 'AAL', 'AAM', 'AAMC', 'AAME', 'AAN',
    'AAOI', 'AAON', 'AAP', 'AAPL', 'AAT', 'AAU', 'AB', 'ABB', 'ABBV', 'ABC', 'ABCB', 'ABCL'
]


raw_data = []

for symbol in stock_symbol:
    url = f'https://www.alphavantage.co/query?function={fundamental_data[0]}&symbol={symbol}&apikey={aplha_vantage_key}'
    r = requests.get(url)
    data = r.json()
    data = list(data.items())
    raw_data.extend(data)

raw_data






stock_symbol = ['IBM', 'AAON']

data3 = []

url = f'https://www.alphavantage.co/query?function={fundamental_data[1]}&symbol={stock_symbol[0]}&apikey={demo}'
r = requests.get(url)
data = r.json()
# Remove elements from all nested levels of dict that are equal to None value






print(data)




# Function to flatten nested dictionaries
def flatten_dict(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)



fundamental_data = ['OVERVIEW', 'INCOME_STATEMENT', 'BALANCE_SHEET', 'CASH_FLOW']
stock_symbols = ['IBM', 'AAON']
api_key = 'demo'  # Replace 'demo' with your API key

# Create an empty DataFrame to store the data
df = pd.DataFrame()

# Iterate over the stock symbols and fundamental data
for symbol in stock_symbols:
    for data_type in fundamental_data:
        url = f'https://www.alphavantage.co/query?function={data_type}&symbol={symbol}&apikey={api_key}'
        r = requests.get(url)
        data = r.json()

        # Flatten the JSON data
        flattened_data = flatten_dict(data)

        # Add the stock symbol and data type to the flattened data
        flattened_data.update({'symbol': symbol, 'data_type': data_type})

        # Append the flattened data to the DataFrame using pandas.concat
        df = pd.concat([df, pd.DataFrame([flattened_data])], ignore_index=True)

print(df)







print(df)


c1 = [{
    'symbol': 'IBM',
    "alpha_vantage1": [{
        "symbol1": "ibm",
        "outputsize1": "full"
    }],
}]

c2 = [{
    'symbol': 'IBM',
    "alpha_vantage2": [{
        "symbol2": "xxx",
        "outputsize2": "zzz"
    }],
}]

c3 = [{
    'symbol': 'IBMXX',
    "alpha_vantage2": [{
        "symbol2": "xxx",
        "outputsize2": "zzz"
    }],
}]

all_lists = [c1, c2, c3]

result = {}
for lst in all_lists:
    for item in lst:
        symbol = item["symbol"]
        if symbol not in result:
            result[symbol] = item
        else:
            result[symbol].update(item)

merged_result = list(result.values())

print(merged_result)





api_key = aplha_vantage_key
#api_key = "demo"

symbols_list = ["AA", "AAC",]

fundamental_data = ["OVERVIEW", "INCOME_STATEMENT", "BALANCE_SHEET", "CASH_FLOW", "EARNINGS", "LISTING_STATUS"]

all_results = []







for stock in symbols_list:
    stock_data = get_fundamental_data(aplha_vantage_key, stock, fundamental_data)
    all_results.append({stock: stock_data})
    print(f"Completed data retrieval for {stock}")

all_results_temp = all_results.copy()







def remove_unwanted_values(item):
    if isinstance(item, list):
        return [remove_unwanted_values(x) for x in item if x not in (0, None, '0', 'None')]
    elif isinstance(item, dict):
        return {k: remove_unwanted_values(v) for k, v in item.items() if v not in (0, None, '0', 'None')}
    else:
        return item


print(remove_unwanted_values(all_results_temp))






def remove_list_with_specific_date(item, key='fiscalDateEnding', threshold_date=datetime.date(2022, 1, 1)):
    if isinstance(item, list):
        new_list = []
        for i in item:
            new_i = remove_list_with_specific_date(i, key, threshold_date)
            if new_i is not None:
                new_list.append(new_i)

        for i in new_list:
            if isinstance(i, dict) and key in i and isinstance(i[key], str):
                date_value = datetime.datetime.strptime(i[key], "%Y-%m-%d").date()
                print(date_value, " ", threshold_date)
                if date_value < threshold_date:
                    return None
        return new_list

    elif isinstance(item, dict):
        return {k: remove_list_with_specific_date(v, key, threshold_date) for k, v in item.items()}

    else:
        return item





all_results
print(all_results)



# Example dictionary with nested levels and unwanted values
example_dict = [{
    'key1': None,
    'key2': 'value2',
    'key3': {
        'fiscalDateEnding': '2021-12-31',
        'key3_2': 'value3_2',
        'key3_3': {
            'key3_3_1': 'None',
            'key3_3_2': None
        },
        'key3_4': 'value3_4'
    },
    'key4': 'value4',
    'key5': {
        'fiscalDateEnding': '2022-01-31',
        'key5_2': 'value3_2',}
}]

example_dict2 = remove_unwanted_values(example_dict)
example_dict2

remove_list_with_specific_date(example_dict2, key='fiscalDateEnding', threshold_date=datetime.date(2022, 1, 1))














# Generate input for GPT-3
input_text = f"Financial analysis: what do you think about company with this stock {symbols_list[0]}?"


# Query GPT-3
response = openai.Completion.create(
    engine="text-davinci-003",
    prompt=input_text,
    max_tokens=100,
    n=1,
    stop=None,
    temperature=0.5,
)

# Print GPT-3's response
print(response.choices[0].text.strip())




