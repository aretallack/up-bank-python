#%%################
##### IMPORTS #####
###################
# import os
import re
import pandas as pd
# import numpy as np
import requests
from datetime import datetime
import pytz

from src.config import BASE_URL, BALANCES_OUT, HEADERS

#%%#################
##### LOAD API #####
####################
def getBalance(BASE_URL, HEADERS):
    # Get most recent request
    request = requests.get(f'{BASE_URL}/accounts', headers = HEADERS)
    accounts = request.json()['data']

    now = datetime.now(pytz.timezone("Australia/Adelaide"))
    date = now.strftime("%Y-%m-%d %H:%M:%S%z")
    tz = now.strftime('%z')
    date = f"{date}{tz[:-2]}:{tz[-2:]}"
    date = pd.to_datetime(date)

    # Remove non letters from account names (I.e. the emojis)
    balances = {re.sub(r'[^a-zA-Z]', '', x['attributes']['displayName']): float(x['attributes']['balance']['value']) for x in accounts}
    balances = {f'{x.lower()}Balance':y for x,y in zip(balances.keys(), balances.values())}
    return balances

if __name__ == '__main__':
    currentBalance = getBalance(BASE_URL, HEADERS)
# %%
