# data_fetcher.py

import requests
import time
import pandas as pd
import numpy as np
import os
import io
import pickle
from tqdm import tqdm
from helpers import save_dataframe_to_csv

from alpha_vantage.timeseries import TimeSeries

class DataFetcher:
    """
    DataFetcher class for fetching stock data from Alpha Vantage API.
    """
    def __init__(self, api_key, 
                 base_url = "https://www.alphavantage.co/query?",
                 data_path = "data/"):
        
        self.api_key = api_key
        self.base_url = base_url
        self.data_path = data_path
        self.listed_stocks_file_name = "listed_stocks.csv"
        self.outputsize = "full"
        self.stock_price_close = "5. adjusted close"
        self.trading_volume = "6. volume"

    def _get_fundamental_data(self, **kwargs):
        # Uses the input API key and fundamental data type.
        # Loops through each stock symbol in the input list.
        # Makes requests to the API, retrying up to 100 times if unsuccessful.
        # Appends the response data to a results list if the request is successful.
        # Prints error messages and skips to the next stock if unsuccessful after 100 attempts.
        # Waits for 1 second between requests to avoid hitting API rate limits.
        # Returns the list of fetched data.

        
        symbols_list = kwargs.get("symbols_list")
        fundamental_data = kwargs.get("fundamental_data")
        
        results = []
        start_time = time.time()
        max_attempts = 100

        for stock in tqdm(symbols_list, desc="Fetching data", unit="stock"):
            attempts = 0
            while attempts < max_attempts:
                try:
                    url = f"{self.base_url}function={fundamental_data}&symbol={stock}&apikey={self.api_key}"
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
    
    
    def _get_fundamental_data(self, **kwargs):
        """
        Fetches fundamental data for a list of stocks from an API and returns the data in JSON format.
        :param kwargs: A dictionary of keyword arguments.
            - symbols_list: A list of stock symbols to fetch data for.
            - fundamental_data: The type of fundamental data to fetch (e.g. income statement, balance sheet).
        :return: A list of JSON objects containing the fetched data for each stock.
        """
        symbols_list = kwargs.get("symbols_list")
        fundamental_data = kwargs.get("fundamental_data")
        
        results = []
        start_time = time.time()
        max_attempts = 100

        for stock in tqdm(symbols_list, desc="Fetching data", unit="stock"):
            attempts = 0
            while attempts < max_attempts:
                try:
                    url = f"{self.base_url}function={fundamental_data}&symbol={stock}&apikey={self.api_key}"
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
    

    def _get_stocks_listing(self, **kwargs):
        """
        The function retrieves the listing status of all stocks and returns a pandas DataFrame containing the symbols, names, exchanges, 
        and IPO dates of the stocks that meet the specified criteria. The function takes in the following arguments:
        status (default: 'active'): The listing status of the stocks to retrieve.
        assetType (default: 'stock'): The type of asset to retrieve.
        exchange1 (default: 'nyse'): The primary exchange for the stocks to retrieve.
        exchange2 (default: 'nasdaq'): The secondary exchange for the stocks to retrieve.
        fundamental_data (default: 'LISTING_STATUS'): The type of fundamental data to retrieve.
        The function first retrieves the data from the API and then filters the data to meet the specified criteria. 
        It drops any duplicate symbols and names, and returns the resulting DataFrame.
        """

        status = kwargs.get("status", "active")
        assetType = kwargs.get("assetType", "stock")
        exchange1 = kwargs.get("exchange1", "nyse")
        exchange2 = kwargs.get("exchange2", "nasdaq")
        fundamental_data = kwargs.get("fundamental_data", "LISTING_STATUS")

        base_url = f'{self.base_url}function={fundamental_data}&apikey={self.api_key}'

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
            mask = mask1 & mask2 & mask3 & mask4 & mask5 & mask6 & mask7
            df_temp = df_temp.loc[mask]

            df_temp.drop_duplicates(subset = ['symbol'], inplace = True)
            df_temp.drop_duplicates(subset = ['name'], keep = 'first', inplace = True)

            df_temp = df_temp[['symbol', 'name', 'exchange', 'ipoDate']].reset_index(drop = True)


        return df_temp
    
    def _get_stock_price_vol(self,**kwargs):
        """
        Fetches stock price and volume data for a list of stock symbols over a specified time period.

        Args:
        - symbols_list (list of str): List of stock symbols to fetch data for.
        - period (str): Time period to fetch data for. Must be either "daily", "weekly", or "monthly".

        Returns:
        - results (pandas DataFrame): DataFrame containing stock price and volume data for each company in symbols_list.
        """
        symbols_list = kwargs.get("symbols_list")
        period = kwargs.get("period")

        ts = TimeSeries(key = self.api_key)  
        
        results = pd.DataFrame()
        start_time = time.time()
        max_attempts = 100

        for stock in tqdm(symbols_list, desc="Fetching data", unit="stock"):
            attempts = 0
            while attempts < max_attempts:
                try:
                    data = pd.DataFrame()
                    
                    if period == "daily":
                        data, _ = ts.get_daily_adjusted(stock, outputsize = self.outputsize)
                    elif period == "weekly":
                        data, _ = ts.get_weekly_adjusted(stock)
                    elif period == "monthly":
                        data, _ = ts.get_monthly_adjusted(stock)
                    else:
                        raise ValueError("period must be either daily, weekly, or monthly")

                    data = pd.DataFrame(data).T

                    data.rename(columns = {self.stock_price_close: "stock_price_close",
                                        self.trading_volume: "trading_volume"},
                                        inplace = True)
                    data = data.loc[:, ["stock_price_close", "trading_volume"]]

                    data.loc[:, "trading_date"] = pd.to_datetime(data.index)
                    data.loc[:, "company"] = stock
                    data.reset_index(drop = True, inplace = True)
                    results = pd.concat([results, data], axis = 0)
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
    

    def fetch_stocks_listing(self, **kwargs):
        """
        Fetches a list of all currently listed stocks.

        Args:
        - status (str): Listing status to filter stocks by. Default is "active".
        - assetType (str): Asset type to filter stocks by. Default is "stock".
        - exchange1 (str): First exchange to filter stocks by. Default is "nyse".
        - exchange2 (str): Second exchange to filter stocks by. Default is "nasdaq".
        - fundamental_data (str): API function to use to fetch stock data. Default is "LISTING_STATUS".

        Returns:
        - symbols_list (list of str): List of all currently listed stocks.
        - df_listed_stocks (pandas DataFrame): DataFrame containing information about all listed stocks.
        """
        file_path_listings = os.path.join(self.data_path, self.listed_stocks_file_name)

        if not os.path.exists(file_path_listings):
            print("CSV file for listed stocks not found. Fetching data...")
            df_listed_stocks = self._get_stocks_listing(api_key = self.api_key, **kwargs)
            save_dataframe_to_csv(df_listed_stocks, file_path_listings)
            print("Listed stocks data saved to CSV file.")
        else:
            print("CSV file for listed stocks found. Loading data...")
            df_listed_stocks = pd.read_csv(file_path_listings)
            print("Listed stocks data loaded from CSV file.")

        symbols_list = df_listed_stocks['symbol'].tolist()

        return symbols_list, df_listed_stocks
    

    def fetch_fundamental_data(self, **kwargs):
        """
        Fetches fundamental data for a list of symbols and saves/loads it to/from a pickle file.

        Args:
            symbols_list (list): A list of stock symbols.
            fundamental_data (str): The type of fundamental data to fetch.
        
        Returns:
            data (list): A list of dictionaries containing the fundamental data for each symbol.
        """
        symbols_list = kwargs.get("symbols_list")
        fundamental_data = kwargs.get("fundamental_data")

        pickle_file_path = os.path.join(self.data_path, f"{fundamental_data}_data.pkl")

        if not os.path.exists(pickle_file_path):
            print(f"Pickle file for {fundamental_data} not found. Fetching data...")
            # Get fundamental data
            data = self._get_fundamental_data(api_key = self.api_key, symbols_list=symbols_list, fundamental_data=fundamental_data)
            
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
    
    def fetch_company_data_by_key(self, **kwargs):
        """
        Fetches fundamental data for a list of symbols and saves/loads it to/from a pickle file.

        Args:
            symbols_list (list): A list of stock symbols.
            fundamental_data (str): The type of fundamental data to fetch.
        
        Returns:
            data (list): A list of dictionaries containing the fundamental data for each symbol.
        """
        stock_data = kwargs.get("stock_data")
        key = kwargs.get("key", "symbol")
        company_symbol = kwargs.get("company_symbol")

        output_list = [company for company in stock_data if company[key] == company_symbol]

        if not output_list:
            print(f"No data found for {company_symbol}")

        return output_list

    def fetch_latest_stock_price_vol(self, **kwargs):
        """
        Fetches fundamental data for a list of symbols and saves/loads it to/from a pickle file.

        Args:
            symbols_list (list): A list of stock symbols.
            fundamental_data (str): The type of fundamental data to fetch.
        
        Returns:
            data (list): A list of dictionaries containing the fundamental data for each symbol.
        """
        symbols_list = kwargs.get("symbols_list")
        period = kwargs.get("period", "monthly")
        max_stock_price = kwargs.get("max_stock_price", 10)

        if period not in ["daily", "weekly", "monthly"]:
            raise ValueError("period must be either 'daily', 'weekly', or 'monthly'")

        df_stocks = self._get_stock_price_vol(symbols_list = symbols_list, period = period)

        df_stocks['stock_price_close'] = df_stocks['stock_price_close'].astype(int)
        df_stocks['trading_volume'] = df_stocks['trading_volume'].astype(int)

        mask = (df_stocks["stock_price_close"] > 0) & (df_stocks["stock_price_close"] < max_stock_price) & (df_stocks["trading_volume"] > 0) 
        df_stocks = df_stocks.loc[mask].groupby("company").apply(lambda x: x[x["trading_date"] == x["trading_date"].max()]).reset_index(drop = True)

        if len(df_stocks["company"].unique()) != len(symbols_list):
            missing_symbols = list(set(symbols_list) - set(df_stocks["company"].unique()))
            print(f"Data not found for symbols: {missing_symbols}")

        return df_stocks

