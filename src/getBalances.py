#%%################
##### IMPORTS #####
###################
import os
import pandas as pd
import numpy as np
import requests
from dotenv import load_dotenv
from datetime import datetime
from src.config import API_KEY, BASE_URL, BALANCES_OUT, HEADERS

#%%#################
##### LOAD API #####
####################
def getBalance(API_KEY, BASE_URL, HEADERS, since = None):
    params = {
        'page[size]': 1,
        'filter[since]': since,
        }

    # Get most recent request
    first_request = requests.get(f'{BASE_URL}/accounts', headers = HEADERS)
    accounts = first_request.json()['data']

    accountNames = [x['attributes']['displayName'] for x in accounts]
    date = datetime.now()
    balances = {x['attributes']['displayName']: float(x['attributes']['balance']['value']) for x in accounts}
    return balances

def getDictTotal(balanceDict: dict[str, float]) -> float:    
    return int(np.sum(list(balanceDict.values())))

def processBalances():
    balance = getBalance(API_KEY, BASE_URL, HEADERS)
    totalBalance = getDictTotal(balance)

    balanceDF = pd.DataFrame({
        'balance': totalBalance
    }, index = [datetime.now()])

    if not os.path.exists(BALANCES_OUT):
        os.makedirs(os.path.dirname(BALANCES_OUT), exist_ok = True)
        balanceDF.to_csv(BALANCES_OUT)
    else:
        existing = pd.read_csv(BALANCES_OUT, index_col=0, parse_dates=True)
        appended = pd.concat([existing, balanceDF])
        appended.to_csv(BALANCES_OUT)

