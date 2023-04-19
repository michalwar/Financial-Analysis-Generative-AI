import pandas as pd


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
