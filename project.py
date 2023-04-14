
import numpy as np
import pandas as pd
import os
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

print("All libraries loaded")




load_dotenv() 


config = {
    "alpha_vantage": {
        "key": os.getenv("ALPHA_VANTAGE_API_KEY"),
        "symbol": "IBM",
        "outputsize": "full",
        "key_adjusted_close": "5. adjusted close",
    },
}




def download_data(config):
    ts = TimeSeries(key=config["alpha_vantage"]["key"])  
    data, meta_data = ts.get_daily_adjusted(config["alpha_vantage"]["symbol"], outputsize=config["alpha_vantage"]["outputsize"])

    data_date = [date for date in data.keys()]
    data_date.reverse()

    data_close_price = [float(data[date][config["alpha_vantage"]["key_adjusted_close"]]) for date in data.keys()]
    data_close_price.reverse()
    data_close_price = np.array(data_close_price)

    num_data_points = len(data_date)
    display_date_range = "from " + data_date[0] + " to " + data_date[num_data_points-1]
    print("Number data points", num_data_points, display_date_range)

    return data_date, data_close_price, num_data_points, display_date_range



data_date, data_close_price, num_data_points, display_date_range = download_data(config)



df_usa_stocks = pd.read_csv("data/usa_stocks.csv")















