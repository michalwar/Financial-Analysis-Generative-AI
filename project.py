
import numpy as np
import pandas as pd
import os
import io
import requests
import time

from dotenv import load_dotenv

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

import openai

print("All libraries loaded")

load_dotenv() 

aplha_vantage_key = os.getenv("ALPHA_VANTAGE_API_KEY")
openai.organization = os.getenv("OPENAI_ORG_ID")

openai.Model.list()





config = {
    "alpha_vantage": {
        "key": aplha_vantage_key,
        "symbol": "IBM",
        "outputsize": "full",
        "key_adjusted_close_stock_price": "5. adjusted close",
        "trading_volume": "6. volume",
    },
}





def save_dataframe_to_csv(dataframe, file_path):
    dataframe.to_csv(file_path, index = False)
    print(f"Data saved to: {file_path}")



def remove_unwanted_values(item):
    if isinstance(item, list):
        return [remove_unwanted_values(x) for x in item if x not in (None, 'None', '', ' ', '-')]
    elif isinstance(item, dict):
        return {k: remove_unwanted_values(v) for k, v in item.items() if v not in (None, 'None', '', ' ', '-')}
    else:
        return item
    


def get_fundamental_data(**kwargs):
    # Get fundamental data for a list of stocks.

    symbols_list = kwargs.get("symbols_list")
    fundamental_data = kwargs.get("fundamental_data")
    api_key = kwargs.get("api_key")

    base_url = "https://www.alphavantage.co/query?"
    results = []

    for stock in symbols_list:
        url = f"{base_url}function={fundamental_data}&symbol={stock}&apikey={api_key}"
        response = requests.get(url)
        json_data = response.json()
        results.append(json_data)
        time.sleep(0.41)  # Wait xx seconds between requests to avoid hitting API rate limits

    return results



def get_stocks_listing(**kwargs):
    # Get listing status for all stocks.

    api_key = kwargs.get("api_key")
    status = kwargs.get("status", "active")
    assetType = kwargs.get("assetType", "stock")
    exchange1 = kwargs.get("exchange", "nyse")
    exchange2 = kwargs.get("exchange", "nasdaq")

    base_url = f'https://www.alphavantage.co/query?function=LISTING_STATUS&apikey={api_key}'

    with requests.Session() as s:
        download = s.get(base_url)
        decoded_content = download.content.decode('utf-8')
        df_temp = pd.read_csv(io.StringIO(decoded_content))

        mask1 = df_temp['status'].str.lower() == status
        mask2 = (df_temp['exchange'].str.lower() == exchange1) | (df_temp['exchange'].str.lower() == exchange2)
        mask3 = df_temp['assetType'].str.lower() == assetType
        mask4 = df_temp['symbol'].str.contains('-') == False
        mask5 = df_temp['name'].str.contains('- Units') == False
        mask6 = df_temp['name'].str.contains('Warrants') == False
        mask7 = df_temp['name'].str.contains('TEST STOCK|LISTED TEST') == False
        mask = mask1 & mask2 & mask3 & mask4 & mask5 & mask6
        df_temp = df_temp.loc[mask]

        df_temp.drop_duplicates(subset = ['symbol'], inplace = True)
        df_temp.drop_duplicates(subset = ['name'], keep = 'first', inplace = True)

        df_temp = df_temp[['symbol', 'name', 'exchange', 'ipoDate']].reset_index(drop = True)


    return df_temp



def process_fundamental_data_overview(**kwargs):
    # Process fundamental data for a list of stocks.

    stock_data_overview = kwargs.get("stock_data")
    
    data = stock_data_overview.copy()
    # Remove empty values
    filtered_data = [company_data for company_data in data if company_data]

    relevant_info_list = []
    

    for company_data in filtered_data:
        gross_profit_margin = float(company_data.get('GrossProfitTTM', 0)) / float(company_data.get('RevenueTTM', 1)) if float(company_data.get('GrossProfitTTM', 0)) != 0 else 0

        relevant_info = {
            'Symbol': company_data.get('Symbol', None),
            'Name': company_data.get('Name', None),
            'Sector': company_data.get('Sector', None),
            'Industry': company_data.get('Industry', None),
            'LatestQuarter': company_data.get('LatestQuarter', None),
            'MarketCapitalization': company_data.get('MarketCapitalization', None),
            'PERatio': company_data.get('PERatio', None),
            'ForwardPERatio': company_data.get('ForwardPE', None),
            'PEGRatio': company_data.get('PEGRatio', None),
            'PriceToSalesRatio': company_data.get('PriceToSalesRatioTTM', None),
            'PriceToBookRatio': company_data.get('PriceToBookRatio', None),
            'EPS': company_data.get('EPS', None),
            'GrossProfitMargin': gross_profit_margin,
            'NetProfitMargin': company_data.get('ProfitMargin', None),
            'DividendPerShare': company_data.get('DividendPerShare', None),
            'DividendYield': company_data.get('DividendYield', None),
            'ReturnOnAssets': company_data.get('ReturnOnAssetsTTM', None),
            'ReturnOnEquity': company_data.get('ReturnOnEquityTTM', None),
            'Revenue': company_data.get('RevenueTTM', None),
            'RevenuePerShare': company_data.get('RevenuePerShareTTM', None),
        }
        relevant_info_list.append(relevant_info)

    relevant_info_list = remove_unwanted_values(relevant_info_list)

    return relevant_info_list





def process_fundamental_data_income(**kwargs):
    # Process fundamental data for a list of stocks.

    stock_data_income = kwargs.get("stock_data")
    
    data = stock_data_income.copy()
    # Remove empty values
    filtered_data = [company_data for company_data in data if company_data]

    relevant_info_list = []


    for company in filtered_data:
        symbol = company['symbol']
        annual_reports = company['annualReports']

        for report in annual_reports:
            gross_profit_margin = float(report.get('grossProfit', 0)) / float(report.get('totalRevenue', 0)) if float(report.get('totalRevenue', 0)) != 0 else 0
            operating_margin = float(report.get('operatingIncome', 0)) / float(report.get('totalRevenue', 0)) if float(report.get('totalRevenue', 0)) != 0 else 0
            net_profit_margin = float(report.get('netIncome', 0)) / float(report.get('totalRevenue', 0)) if float(report.get('totalRevenue', 0)) != 0 else 0

            relevant_info = {
                'Symbol': symbol,
                'FiscalDateEnding': report.get('fiscalDateEnding', None),
                'GrossProfit': report.get('grossProfit', None),
                'OperatingIncome': report.get('operatingIncome', None),
                'GrossProfitMargin': gross_profit_margin,
                'OperatingMargin': operating_margin,
                'NetProfitMargin': net_profit_margin,
            }
            relevant_info_list.append(relevant_info)


    relevant_info_list = remove_unwanted_values(relevant_info_list)

    return relevant_info_list











df_listed_stocks = get_stocks_listing(api_key = aplha_vantage_key)

save_dataframe_to_csv(df_listed_stocks, "data/listed_stocks.csv")



symbols_list = df_listed_stocks['symbol'].tolist()[:5]




stock_data_overview = get_fundamental_data(api_key = aplha_vantage_key, symbols_list = symbols_list, fundamental_data = "OVERVIEW")
all_results_overview = process_fundamental_data_overview(stock_data = stock_data_overview)

all_results_overview_clean = remove_unwanted_values(all_results_overview)


stock_data_income = get_fundamental_data(api_key = aplha_vantage_key, symbols_list = symbols_list, fundamental_data = "INCOME_STATEMENT")
all_results_income = process_fundamental_data_income(stock_data = stock_data_income)






[company for company in all_results_overview if company['Symbol'] == 'AAC']








stock_data_listing = get_fundamental_data(api_key = aplha_vantage_key, symbols_list = symbols_list, fundamental_data = "LISTING_STATUS")
















