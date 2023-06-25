prompt_task = """
                Analyze and evaluate the Warren Buffet's investment criteria for the company from list:
"""

prompt_task_support = """
                using the following categories: Financial Health, Valuation, Margin of Safety, Profitability, Dividends, Debt, Return on Equity, Capital Expenditures, and whether the company is undervalued or overvalued
"""

type_response = """
                fiancial resultas are provided at the end of this message. For each category, provide Score from 1-10 (1=negative, 10=positive), indicate if the category is positive or negative, and explain your reasoning. Present your analysis with labeles 'Investment Criteria', 'Score', 'Positive/Negative', and 'Reasoning' using exactly the following format
"""

format_response = """
                data = {
                "Investment Criteria": ["Financial Health", "Valuation", "Margin of Safety", "Profitability", "Dividends", "Debt", "Return on Equity", "Capital Expenditures", "Undervalued or Overvalued", "Growth Potential"],
                "Score": [Score for each criteria],
                "Positive/Negative": [Evaluation for each criteria],
                "Reasoning": [Reasoning for each score]
                }
"""

llm_model = "gpt-4"