# main.py

import os
import openai
import pandas as pd
import time
from tqdm import tqdm

from data_fetcher import DataFetcher
from data_processing import DataProcessor

from prompt_engineering import (
    prompt_task,
    prompt_task_support,
    type_response,
    format_response,
    llm_model,
)


def main():
    data_path = "data/"
    alpha_vantage_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    openai.organization = os.getenv("OPENAI_ORG_ID")

    if not alpha_vantage_key:
        raise ValueError("Alpha Vantage API key is not set.")

    data_fetcher = DataFetcher(api_key=alpha_vantage_key, data_path=data_path)
    data_processor = DataProcessor()

    try:
        symbols_list, df_listed_stocks = data_fetcher.fetch_stocks_listing(
            status="active", assetType="stock"
        )
    except Exception as e:
        print(f"Error fetching stocks listing: {e}")

    try:
        max_stock_price = 10000
        df_stocks_price = data_fetcher.fetch_latest_stock_price_vol(
            symbols_list=symbols_list, period="monthly", max_stock_price=max_stock_price
        )
    except Exception as e:
        print(f"Error fetching stocks listing: {e}")

    try:
        stock_data_overview = data_fetcher.fetch_fundamental_data(
            symbols_list=symbols_list, fundamental_data="OVERVIEW"
        )
        all_results_overview = data_processor.process_fundamental_data_overview(
            stock_data=stock_data_overview
        )
    except Exception as e:
        print(f"Error fetching and processing overview data: {e}")

    try:
        stock_data_income_statement = data_fetcher.fetch_fundamental_data(
            symbols_list=symbols_list, fundamental_data="INCOME_STATEMENT"
        )
        all_results_income_statement = data_processor.process_fundamental_data_income(
            stock_data=stock_data_income_statement
        )
    except Exception as e:
        print(f"Error fetching and processing income statement data: {e}")

    try:
        stock_data_balance_sheet = data_fetcher.fetch_fundamental_data(
            symbols_list=symbols_list, fundamental_data="BALANCE_SHEET"
        )
        all_results_balance_sheet = (
            data_processor.process_fundamental_data_balance_sheet(
                stock_data=stock_data_balance_sheet
            )
        )
    except Exception as e:
        print(f"Error fetching and processing balance sheet data: {e}")

    try:
        stock_data_cash_flow = data_fetcher.fetch_fundamental_data(
            symbols_list=symbols_list, fundamental_data="CASH_FLOW"
        )
        all_results_cash_flow = data_processor.process_fundamental_data_cash_flow(
            stock_data=stock_data_cash_flow
        )
    except Exception as e:
        print(f"Error fetching and processing cash flow data: {e}")

    mask = df_stocks_price["company"].isin(["LCID", "RIVN", "U"])
    df_stocks_price_temp = df_stocks_price.loc[mask].copy()

    company_symbol_key = "Symbol"
    final_response = []
    company_symbol_stock_list = df_stocks_price_temp.loc[:, "company"].reset_index(
        drop=True
    )
    start_time = time.time()
    max_attempts = 100

    for company_symbol_stock in tqdm(
        company_symbol_stock_list, desc="Analysing companies", unit="stock"
    ):
        print(f"AI working on company symbol: {company_symbol_stock}...")
        attempts = 0
        while attempts < max_attempts:
            try:
                """
                company_symbol_stock = "LCID"

                """

                company_analyze_temp = []
                company_analyze = []

                company_analyze_temp = data_fetcher.fetch_company_data_by_key(
                    stock_data=all_results_overview,
                    key=company_symbol_key,
                    company_symbol=company_symbol_stock,
                )

                company_analyze.append(company_analyze_temp)

                company_analyze_temp = data_fetcher.fetch_company_data_by_key(
                    stock_data=all_results_income_statement,
                    key=company_symbol_key,
                    company_symbol=company_symbol_stock,
                )

                company_analyze.append(company_analyze_temp)

                company_analyze_temp = data_fetcher.fetch_company_data_by_key(
                    stock_data=all_results_balance_sheet,
                    key=company_symbol_key,
                    company_symbol=company_symbol_stock,
                )

                company_analyze.append(company_analyze_temp)

                company_analyze_temp = data_fetcher.fetch_company_data_by_key(
                    stock_data=all_results_cash_flow,
                    key=company_symbol_key,
                    company_symbol=company_symbol_stock,
                )

                company_analyze.append(company_analyze_temp)

                question = f"{prompt_task} {company_symbol_stock}, {prompt_task_support}. All {company_symbol_stock}'s {type_response}: {format_response}"
                input_text = question + str(company_analyze_temp.copy())

                llm_model = llm_model
                llm_message = [{"role": "user", "content": input_text}]

                response = openai.ChatCompletion.create(
                    model=llm_model, messages=llm_message
                )

                final_response.append(
                    [company_symbol_stock, response["choices"][0]["message"]["content"]]
                )

                # Save list to csv file where each row is a list item
                # Check if the list is not empty
                if final_response:
                    # Convert the list to a DataFrame
                    df = pd.DataFrame(final_response)

                    # Write the DataFrame to a CSV file
                    df.to_csv(
                        f"{data_path}final_response.csv", index=False, header=False
                    )

                print(f"...finished and saved results to {data_path}final_response.csv")
                break  # Exit the loop if the request is successful

            except Exception as e:
                print(
                    f"Error fetching data for {company_symbol_stock}: {e}. Retrying..."
                )
                attempts += 1
                time.sleep(2)  # Wait before retrying the request

            if attempts == max_attempts:
                print(
                    f"Failed to fetch data for {company_symbol_stock} after {max_attempts} attempts. Skipping..."
                )

            time.sleep(
                1
            )  # Wait xx seconds between requests to avoid hitting API rate limits

        elapsed_time = time.time() - start_time
        print(f"Total time elapsed: {elapsed_time:.2f} seconds")


if __name__ == "__main__":
    main()
