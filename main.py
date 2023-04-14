import os
import sys
from dotenv import load_dotenv

import pandas as pd
import numpy as np

import openai
import requests


openai.organization = os.getenv("OPENAI_ORG_ID")


load_dotenv()  # Loads the environment variables from the .env file



openai.Model.list()



# Generate input for GPT-3
input_text = f"The closing price for {symbol} on {latest_date} was {closing_price}. What do you think about this stock?"
input_text = "test"

# Query GPT-3
response = openai.Completion.create(
    engine="text-davinci-002",
    prompt=input_text,
    max_tokens=100,
    n=1,
    stop=None,
    temperature=0.5,
)

# Print GPT-3's response
print(response.choices[0].text.strip())


from ftplib import FTP

def is_file(ftp, name):
    try:
        ftp.cwd(name)
    except Exception as e:
        return True
    ftp.cwd('..')
    return False

ftp = FTP('ftp.nasdaqtrader.com')
ftp.login()

ftp.cwd('symboldirectory')

file_list = []
ftp.dir(lambda x: file_list.append(x))


file_list = [entry.split()[-1] for entry in file_list if is_file(ftp, entry.split()[-1])]

# Download all files from file_list, and write to data folder in current directory
for file in file_list:
    with open(f"data/{file}", "wb") as f:
        ftp.retrbinary(f"RETR {file}", f.write)


filename = 'nasdaqlisted.txt'
with open(filename, 'wb') as local_file:
    ftp.retrbinary(f'RETR {filename}', local_file.write)


print(file_list)

ftp.quit()

