
import numpy as np
import pandas as pd
import os
import io
import requests
import time
import pickle
from tqdm import tqdm

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




# Helper functions ======================================================================================================

def save_dataframe_to_csv(dataframe, file_path):
    dataframe.to_csv(file_path, index = False)
    print(f"Data saved to: {file_path}")


def safe_divide(numerator, denominator):
    return float(numerator) / float(denominator) if float(denominator) != 0 else 0


def remove_unwanted_values(item):
    if isinstance(item, list):
        return [remove_unwanted_values(x) for x in item if x not in (None, 'None', '', ' ', '-')]
    elif isinstance(item, dict):
        return {k: remove_unwanted_values(v) for k, v in item.items() if v not in (None, 'None', '', ' ', '-')}
    else:
        return item
    
def to_float(value, default = 0):
    if (value is None) | (value == 'None'):
        return default
    return float(value)



# Main pulling functions =================================================================================================
def get_fundamental_data(**kwargs):
    # Get fundamental data for a list of stocks.

    symbols_list = kwargs.get("symbols_list")
    fundamental_data = kwargs.get("fundamental_data")
    api_key = kwargs.get("api_key")

    base_url = "https://www.alphavantage.co/query?"
    results = []
    start_time = time.time()
    max_attempts = 100

    for stock in tqdm(symbols_list, desc="Fetching data", unit="stock"):
        attempts = 0
        while attempts < max_attempts:
            try:
                url = f"{base_url}function={fundamental_data}&symbol={stock}&apikey={api_key}"
                response = requests.get(url)
                json_data = response.json()
                results.append(json_data)
                break  # Exit the loop if the request is successful
            except Exception as e:
                print(f"Error fetching data for {stock}: {e}. Retrying...")
                attempts += 1
                time.sleep(2)  # Wait before retrying the request

        if attempts == max_attempts:
            print(f"Failed to fetch data for {stock} after {max_attempts} attempts. Skipping...")
        
        time.sleep(1)  # Wait xx seconds between requests to avoid hitting API rate limits

    elapsed_time = time.time() - start_time
    print(f"Total time elapsed: {elapsed_time:.2f} seconds")

    return results


def get_stocks_listing(**kwargs):
    # Get listing status for all stocks.

    api_key = kwargs.get("api_key")
    status = kwargs.get("status", "active")
    assetType = kwargs.get("assetType", "stock")
    exchange1 = kwargs.get("exchange1", "nyse")
    exchange2 = kwargs.get("exchange2", "nasdaq")

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


# Process data ===========================================================================================================

def process_fundamental_data_overview(**kwargs):
    # Process fundamental data for a list of stocks.

    stock_data = kwargs.get("stock_data")
    
    data = stock_data.copy()
    # Remove empty values
    filtered_data = [company_data for company_data in data if company_data]

    relevant_info_list = []
    

    for company_data in filtered_data:

        gross_profit = to_float(company_data.get('GrossProfitTTM', 0))
        revenue = to_float(company_data.get('RevenueTTM', 1))
        gross_profit_margin = safe_divide(gross_profit, revenue)

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
    relevant_info_list = [company for company in relevant_info_list if "Symbol" in company.keys()]


    return relevant_info_list





def process_fundamental_data_income(**kwargs):
    # Process fundamental data for a list of stocks.

    stock_data = kwargs.get("stock_data")
    threshold_date = kwargs.get("threshold_date", '2021-01-01') 
    
    data = stock_data.copy()
    # Remove empty values
    filtered_data = [company_data for company_data in data if company_data]

    relevant_info_list = []


    for company in filtered_data:
        symbol = company.get('symbol', None)
        annual_reports = company.get('annualReports', None)

        if annual_reports:
            for report in annual_reports:

                gross_profit = to_float(report.get('grossProfit', 0))
                total_revenue = to_float(report.get('totalRevenue', 0))
                operating_income = to_float(report.get('operatingIncome', 0))
                net_income = to_float(report.get('netIncome', 0))
                fiscal_date_ending = report.get('fiscalDateEnding', None)

                gross_profit_margin = safe_divide(gross_profit, total_revenue)
                operating_margin = safe_divide(operating_income, total_revenue)
                net_profit_margin = safe_divide(net_income, total_revenue)

                relevant_info = {
                    'Symbol': symbol,
                    'FiscalDateEnding': fiscal_date_ending,
                    'GrossProfit': gross_profit,
                    'OperatingIncome': operating_income,
                    'GrossProfitMargin': gross_profit_margin,
                    'OperatingMargin': operating_margin,
                    'NetProfitMargin': net_profit_margin,
                }
                relevant_info_list.append(relevant_info)


    relevant_info_list = remove_unwanted_values(relevant_info_list)
    relevant_info_list = [company for company in relevant_info_list if (pd.to_datetime(company['FiscalDateEnding']) >= pd.to_datetime(threshold_date)) & ("Symbol" in company.keys())]

    return relevant_info_list



def process_fundamental_data_balance_sheet(**kwargs):
    # Process fundamental data for a list of stocks.

    stock_data = kwargs.get("stock_data")
    threshold_date = kwargs.get("threshold_date", '2021-01-01')
    
    data = stock_data.copy()
    # Remove empty values
    filtered_data = [company_data for company_data in data if company_data]

    relevant_info_list = []

    for company in filtered_data:
        symbol = company.get('symbol', None)
        annual_reports = company.get('annualReports', None)

        if annual_reports:
            for report in annual_reports:
                total_liabilities = to_float(report.get('totalLiabilities', 0))
                total_shareholder_equity = to_float(report.get('totalShareholderEquity', 0))
                total_current_assets = to_float(report.get('totalCurrentAssets', 0))
                total_current_liabilities = to_float(report.get('totalCurrentLiabilities', 0))
                retained_earnings = to_float(report.get('retainedEarnings', 0))
                common_stock_shares_outstanding = report.get('commonStockSharesOutstanding', 0)
                fiscal_date_ending = report.get('fiscalDateEnding', None)

                debt_to_equity_ratio = safe_divide(total_liabilities, total_shareholder_equity)
                current_ratio = safe_divide(total_current_assets, total_current_liabilities)
                return_on_equity = safe_divide(retained_earnings, total_shareholder_equity)

                relevant_info = {
                    'Symbol': symbol,
                    'FiscalDateEnding': fiscal_date_ending,
                    'DebtToEquityRatio': debt_to_equity_ratio,
                    'CurrentRatio': current_ratio,
                    'ReturnOnEquity': return_on_equity,
                    'commonStockSharesOutstanding': common_stock_shares_outstanding,
                }
                relevant_info_list.append(relevant_info)

    relevant_info_list = remove_unwanted_values(relevant_info_list)
    relevant_info_list = [company for company in relevant_info_list if (pd.to_datetime(company['FiscalDateEnding']) >= pd.to_datetime(threshold_date)) & ("Symbol" in company.keys())]

    return relevant_info_list


def process_fundamental_data_cash_flow(**kwargs):
    # Process fundamental data for a list of stocks.

    stock_data = kwargs.get("stock_data")
    threshold_date = kwargs.get("threshold_date", '2021-01-01')
    
    data = stock_data.copy()
    data = stock_data_cash_flow.copy()
    # Remove empty values
    filtered_data = [company_data for company_data in data if company_data]
    

    relevant_info_list = []

    for company in filtered_data:
        symbol = company.get('symbol', None)
        annual_reports = company.get('annualReports', None)

        if annual_reports:
            for report in annual_reports:
                operating_cashflow = report.get('operatingCashflow', None)
                capital_expenditures = report.get('capitalExpenditures', None)
                dividend_payout = report.get('dividendPayout', None)
                fiscal_date_ending = report.get('fiscalDateEnding', None)

                relevant_info = {
                    'Symbol': symbol,
                    'FiscalDateEnding': fiscal_date_ending,
                    'OperatingCashflow': operating_cashflow,
                    'CapitalExpenditures': capital_expenditures,
                    'DividendPayout': dividend_payout
                }
                relevant_info_list.append(relevant_info)

    relevant_info_list = remove_unwanted_values(relevant_info_list)
    relevant_info_list = [company for company in relevant_info_list if (pd.to_datetime(company['FiscalDateEnding']) >= pd.to_datetime(threshold_date)) & ("Symbol" in company.keys())]

    return relevant_info_list


# Get and fetch data ===========================================================================================

def fetch_fundamental_data(**kwargs):
                            
    api_key = kwargs.get("api_key")
    symbols_list = kwargs.get("symbols_list")
    fundamental_data = kwargs.get("fundamental_data")
    data_path = kwargs.get("data_path", "data/")

    pickle_file_path = os.path.join(data_path, f"{fundamental_data}_data.pkl")

    if not os.path.exists(pickle_file_path):
        print(f"Pickle file for {fundamental_data} not found. Fetching data...")
        # Get fundamental data
        data = get_fundamental_data(api_key=api_key, symbols_list=symbols_list, fundamental_data=fundamental_data)
        
        print(f"Saving {fundamental_data} data to pickle file...")
        # Save the list to a file
        with open(pickle_file_path, 'wb') as f:
            pickle.dump(data, f)
        print(f"{fundamental_data} data saved to pickle file.")
    else:
        print(f"Pickle file for {fundamental_data} found. Loading data...")
        # Load the list from the file
        with open(pickle_file_path, 'rb') as f:
            data = pickle.load(f)
        print(f"{fundamental_data} data loaded from pickle file.")
    
    return data


def fetch_stocks_listing(**kwargs):
        
    api_key = kwargs.get("api_key")
    data_path = kwargs.get("data_path", "data/")
    file_path_listings = os.path.join(data_path, "listed_stocks.csv")

    if not os.path.exists(file_path_listings):
        print("CSV file for listed stocks not found. Fetching data...")
        df_listed_stocks = get_stocks_listing(api_key=api_key)
        save_dataframe_to_csv(df_listed_stocks, file_path_listings)
        print("Listed stocks data saved to CSV file.")
    else:
        print("CSV file for listed stocks found. Loading data...")
        df_listed_stocks = pd.read_csv(file_path_listings)
        print("Listed stocks data loaded from CSV file.")

    symbols_list = df_listed_stocks['symbol'].tolist()

    return symbols_list, df_listed_stocks


def get_company_data_by_key(**kwargs):
    stock_data = kwargs.get("stock_data")
    key = kwargs.get("key", "symbol")
    company_symbol = kwargs.get("company_symbol")

    output_list = [company for company in stock_data if company[key] == company_symbol]

    return output_list


# Main execution ========================================================================================================

data_path = "data/"
file_path_listings = os.path.join(data_path, "listed_stocks.csv")


symbols_list, df_listed_stocks = fetch_stocks_listing(api_key = aplha_vantage_key, 
                                                      data_path = data_path)


# Companies Overview

stock_data_overview = fetch_fundamental_data(api_key = aplha_vantage_key, 
                                             symbols_list = symbols_list, 
                                             fundamental_data = "OVERVIEW", 
                                             data_path = data_path)


all_results_overview = process_fundamental_data_overview(stock_data = stock_data_overview)



# Companies Income statement

stock_data_income = fetch_fundamental_data(api_key = aplha_vantage_key,
                                           symbols_list = symbols_list,
                                           fundamental_data = "INCOME_STATEMENT",
                                           data_path = data_path)


all_results_income = process_fundamental_data_income(stock_data = stock_data_income)



# Companies Balance sheet

stock_data_balance_sheet = fetch_fundamental_data(api_key = aplha_vantage_key,
                                                  symbols_list = symbols_list,
                                                  fundamental_data = "BALANCE_SHEET",
                                                  data_path = data_path)

all_results_balance_sheet = process_fundamental_data_balance_sheet(stock_data = stock_data_balance_sheet)


# Companies Cash flow

stock_data_cash_flow = fetch_fundamental_data(api_key = aplha_vantage_key,
                                              symbols_list = symbols_list,
                                              fundamental_data = "CASH_FLOW",
                                              data_path = data_path)

all_results_cash_flow = process_fundamental_data_cash_flow(stock_data = stock_data_cash_flow)







get_company_data_by_key(stock_data = all_results_overview, 
                        key = "Symbol", 
                        company_symbol = "NVDA")

get_company_data_by_key(stock_data = all_results_income, 
                        key = "Symbol", 
                        company_symbol = "NVDA")

get_company_data_by_key(stock_data = all_results_balance_sheet, 
                        key = "Symbol", 
                        company_symbol = "NVDA")

get_company_data_by_key(stock_data = all_results_cash_flow,
                        key = "Symbol",
                        company_symbol = "NVDA")






