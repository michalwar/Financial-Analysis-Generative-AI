import pandas as pd
from helpers import to_float, safe_divide, remove_unwanted_values

class DataProcessor:
    def __init__(self):
        pass

    def process_fundamental_data_overview(self, **kwargs):
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

    def process_fundamental_data_income(self, **kwargs):
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



    def process_fundamental_data_balance_sheet(self, **kwargs):
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


    def process_fundamental_data_cash_flow(self, **kwargs):
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