#%%################
##### IMPORTS #####
###################
import os
import pandas as pd
import numpy as np
import requests
from dotenv import load_dotenv
from use_up_api.transactions import getTransactions, transDict_to_df

#%%#################
##### LOAD API #####
####################
load_dotenv()  # Load variables from .env file
api_key = os.getenv('API_KEY')
base_url = 'https://api.up.com.au/api/v1'
headers = {
        "Authorization": f'Bearer {api_key}'
    }
outPath = './output/accounts.csv'
os.makedirs(os.path.dirname(outPath), exist_ok = True)

#%%###################
##### VERIFY API #####
######################
response = requests.get(F'{base_url}/util/ping', headers=headers)

if response.status_code == 200:
    print("Success:", response.json())
else:
    print(f"Error {response.status_code}: {response.text}")

import requests

print('Getting latest transactions')

params = {
    'page[size]': 100,
    'filter[since]': since,
    }

# Get most recent request
request= requests.get(f'{base_url}/accounts', headers = headers)
accounts = request.json()['data']
# Add to a list for all transactions
all_transactions = transactions.copy()
# Get links
links = first_request.json()['links']


def get_account_balance(api_key, base_url):
    first_request = f"{base_url}/accounts/balance"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        balance_info = response.json()
        return balance_info["data"]["balance"]  # Adjust according to API's response structure
    else:
        print("Error:", response.status_code, response.text)
        return None
