import requests
import time
import pandas as pd
import os
import io
import pickle
from tqdm import tqdm
from helpers import save_dataframe_to_csv


class DataFetcher:

    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query?"
        self.data_path = "data/"

    def get_fundamental_data(self, **kwargs):
        
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
    

    def get_stocks_listing(self, **kwargs):
        # Get listing status for all stocks.

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
            mask = mask1 & mask2 & mask3 & mask4 & mask5 & mask6
            df_temp = df_temp.loc[mask]

            df_temp.drop_duplicates(subset = ['symbol'], inplace = True)
            df_temp.drop_duplicates(subset = ['name'], keep = 'first', inplace = True)

            df_temp = df_temp[['symbol', 'name', 'exchange', 'ipoDate']].reset_index(drop = True)


        return df_temp
    
    def fetch_stocks_listing(self, **kwargs):
            
        file_path_listings = os.path.join(self.data_path, "listed_stocks.csv")

        if not os.path.exists(file_path_listings):
            print("CSV file for listed stocks not found. Fetching data...")
            df_listed_stocks = self.get_stocks_listing(api_key = self.api_key)
            save_dataframe_to_csv(df_listed_stocks, file_path_listings)
            print("Listed stocks data saved to CSV file.")
        else:
            print("CSV file for listed stocks found. Loading data...")
            df_listed_stocks = pd.read_csv(file_path_listings)
            print("Listed stocks data loaded from CSV file.")

        symbols_list = df_listed_stocks['symbol'].tolist()

        return symbols_list, df_listed_stocks
    

    def fetch_fundamental_data(self, **kwargs):
                            
        symbols_list = kwargs.get("symbols_list")
        fundamental_data = kwargs.get("fundamental_data")

        pickle_file_path = os.path.join(self.data_path, f"{fundamental_data}_data.pkl")

        if not os.path.exists(pickle_file_path):
            print(f"Pickle file for {fundamental_data} not found. Fetching data...")
            # Get fundamental data
            data = self.get_fundamental_data(api_key = self.api_key, symbols_list=symbols_list, fundamental_data=fundamental_data)
            
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
        
        stock_data = kwargs.get("stock_data")
        key = kwargs.get("key", "symbol")
        company_symbol = kwargs.get("company_symbol")

        output_list = [company for company in stock_data if company[key] == company_symbol]

        return output_list
