# main.py

import os
import openai

from data_fetcher import DataFetcher
from data_processing import DataProcessor




def main():
    data_path = "data/"
    alpha_vantage_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    openai.organization = os.getenv("OPENAI_ORG_ID")

    if not alpha_vantage_key:
        raise ValueError("Alpha Vantage API key is not set.")

    data_fetcher = DataFetcher(api_key=alpha_vantage_key, data_path=data_path)
    data_processor = DataProcessor()

    try:
        symbols_list, df_listed_stocks = data_fetcher.fetch_stocks_listing(status="active", assetType="stock")
    except Exception as e:
        print(f"Error fetching stocks listing: {e}")
        

    try:
        stock_data_overview = data_fetcher.fetch_fundamental_data(symbols_list=symbols_list, fundamental_data="OVERVIEW")
        all_results_overview = data_processor.process_fundamental_data_overview(stock_data=stock_data_overview)
    except Exception as e:
        print(f"Error fetching and processing overview data: {e}")
        

    try:
        stock_data_income_statement = data_fetcher.fetch_fundamental_data(symbols_list=symbols_list, fundamental_data="INCOME_STATEMENT")
        all_results_income_statement = data_processor.process_fundamental_data_income(stock_data=stock_data_income_statement)
    except Exception as e:
        print(f"Error fetching and processing income statement data: {e}")
        

    try:
        stock_data_balance_sheet = data_fetcher.fetch_fundamental_data(symbols_list=symbols_list, fundamental_data="BALANCE_SHEET")
        all_results_balance_sheet = data_processor.process_fundamental_data_balance_sheet(stock_data=stock_data_balance_sheet)
    except Exception as e:
        print(f"Error fetching and processing balance sheet data: {e}")
        

    try:
        stock_data_cash_flow = data_fetcher.fetch_fundamental_data(symbols_list=symbols_list, fundamental_data="CASH_FLOW")
        all_results_cash_flow = data_processor.process_fundamental_data_cash_flow(stock_data=stock_data_cash_flow)
    except Exception as e:
        print(f"Error fetching and processing cash flow data: {e}")
        


    company_symbol_key = "Symbol"
    company_symbol_stock = "NVDA"
    
    company_analyze_temp = []
    company_analyze = []


    company_analyze_temp = data_fetcher.fetch_company_data_by_key(stock_data = all_results_overview, 
                                                                  key = company_symbol_key,
                                                                  company_symbol = company_symbol_stock)

    company_analyze.append(company_analyze_temp)

    company_analyze_temp = data_fetcher.fetch_company_data_by_key(stock_data = all_results_income_statement, 
                                                                  key = company_symbol_key, 
                                                                  company_symbol = company_symbol_stock)

    company_analyze.append(company_analyze_temp)

    company_analyze_temp = data_fetcher.fetch_company_data_by_key(stock_data = all_results_balance_sheet,
                                                                  key = company_symbol_key,
                                                                  company_symbol = company_symbol_stock)
    
    company_analyze.append(company_analyze_temp)
    

    company_analyze_temp = data_fetcher.fetch_company_data_by_key(stock_data = all_results_cash_flow,
                                                                  key = company_symbol_key,
                                                                  company_symbol = company_symbol_stock)

    company_analyze.append(company_analyze_temp)
    

if __name__ == '__main__':
    main()







