# Stock Analysis PoC

This project aims to develop a PoC solution for stock analysis and recommendation using financial data and OpenAI API to GPT model.

## Table of Contents

1. [Data Collection](#data-collection)
2. [Data Preprocessing](#data-preprocessing)
3. [Feature Selection](#feature-selection)
4. [Integration with OpenAI API](#integration-with-apenai-api)
5. [Company Evaluation](#company-evaluation)
6. [Stock Recommendations](#stock-recommendations)
7. [Output Presentation](#output-presentation)
8. [Testing and Validation](#testing-and-validation)
9. [Iterate and Refine](#iterate-and-refine)

## Data Collection

### Alpha Vantage API

- Stock symbols list (USA)
- Collect the following data using Alpha Vantage API:
  - Stock price:
    - Daily, weekly, and monthly time series.
    - Adjusted close prices for splits and dividends.
  - Fundamental data:
    - Income statement (revenue, net income, etc.).
    - Balance sheet (total assets, total liabilities, etc.).
    - Cash flow statement (operating cash flow, investing cash flow, etc.).
    - Earnings data and estimates.
    - Dividends and stock splits history.

## Data Preprocessing

- Handle missing values.
- Convert data types.
- Normalize/scale data if required.

## Feature Selection

- Identify relevant factors:
  - Revenue growth.
  - Earnings growth.
  - Profit margin.
  - Return on equity.
  - Valuation ratios.

## Integration with OpenAI API

- Send preprocessed data as context/input.
- Include prompt for company evaluation.

## Company Evaluation

- Parse OpenAI API responses.
- Implement scoring system or ranking method.

## Stock Recommendations

- Formulate prompts for recommendations.
- Provide context on Warren Buffett principles.

## Output Presentation

- Display recommended companies in a table/list.
- Include reasons for recommendations.

## Testing and Validation

- Test PoC solution functionality.
- Validate recommendations against historical data/expert opinions.

## Iterate and Refine

- Improve solution based on feedback.
- Update data and adapt to market conditions.

