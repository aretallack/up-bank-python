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
outPath = './output/transactions.csv'
os.makedirs(os.path.dirname(outPath), exist_ok = True)

#%%###################
##### VERIFY API #####
######################
response = requests.get(F'{base_url}/util/ping', headers=headers)

if response.status_code == 200:
    print("Success:", response.json())
else:
    print(f"Error {response.status_code}: {response.text}")

#%%#####################
##### TRANSACTIONS #####
########################
if os.path.exists(outPath):
    existing = pd.read_csv(outPath)
    since = existing['createdAt'][0]
else:
    since = None

transDict = getTransactions(api_key, base_url= base_url, since = since, headers = headers)

attrList = [
    'status', 'rawText', 'description', 'amount', 
    'message', 'cardPurchaseMethod', 'settledAt', 
    'createdAt', 'transactionType', 'Note'
    ]

transDF = transDict_to_df(transDict, attrList)

if os.path.exists(outPath):
    existingIDs = list(np.unique(existing['id']))
    transDF = transDF[~transDF['id'].isin(existingIDs)]
    if len(transDF) != 0:
        transDF = pd.concat([existing, transDF])
        transDF.to_csv(outPath, index = False)
    else:
        print('No new transactions')
else:
    transDF.to_csv(outPath, index = False)