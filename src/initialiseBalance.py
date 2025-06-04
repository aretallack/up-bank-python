#%%########
##### #####
###########
import pandas as pd
import numpy as np
from datetime import datetime
from src.config import TRANSACTIONS_OUT, BALANCES_OUT, API_KEY, BASE_URL, HEADERS
from src.getBalances import getBalance
#%%########
##### #####
###########
# def needInitialise():
#     df = pd.read_csv(TRANSACTIONS_OUT)
#     return bool(pd.isna(df['bankBalance']).all())

# def saveBalances():
#     currentBalances = getBalance(API_KEY, BASE_URL, HEADERS)
#     if os.path.exists(BALANCES_OUT):
#         existing = pd.read_csv(BALANCES_OUT, index_col=0, parse_dates=True)
#         appended = pd.concat([existing, currentBalances])
#         appended.to_csv(BALANCES_OUT)
#         return
#     currentBalances.to_csv(BALANCES_OUT)

def addTrueBalance(TRANSACTIONS_OUT):
    # balances = pd.read_csv(BALANCES_OUT, index_col=0, parse_dates=True)
    transactions = pd.read_csv(TRANSACTIONS_OUT, index_col=0, parse_dates=True)
    # transactions = transactions[['value', 'account']]
    # transactions['createdAt'] = pd.to_datetime(transactions['createdAt'], utc=True)
    # transactions['createdAt'] = transactions['createdAt'].dt.tz_convert('Australia/Adelaide')
    # transactions.set_index('createdAt', inplace = True)

    latestBalance = getBalance(API_KEY, BASE_URL, HEADERS)

    # Append as a new row, keeping its own index (e.g., timestamp)
    transactions = pd.concat([transactions, latestBalance])
    transactions = transactions.sort_index(ascending = False)
    transactions.index.name = 'createdAt'

    transactions.to_csv(TRANSACTIONS_OUT)


def backCalculateBalances(TRANSACTIONS_OUT):
    '''
    Funtion to interpolate between actual API-retrieved balances, based on transaction information from each account
    Enables tracking of account balances by inference of incoming and outgoing values with reference to a point of truth
    '''
    transactions = pd.read_csv(TRANSACTIONS_OUT, index_col=0, parse_dates=True)
    transactions = transactions.reset_index()

    needCalculation = transactions['Spending'].isna().any()

    if not needCalculation:
        print('All balances filled - no calculation needed')
        # return
    
    # Find index of first non-NA balance
    # No point looking through rows before this point
    # Probably 0 if addTrueBalance() has just been run.
    startIndex = transactions[~transactions['Spending'].isna()].index.min()

    # From this point, iterate through to the current time
    i = startIndex
    while i <= transactions.index.max() - 1:
        # Check if next value is NA, and needs filling
        needFill = np.isnan(transactions.loc[i+1, 'Spending'])

        if needFill: # If next row has no balance
            # Get account from which money moved to/from
            account = transactions.loc[i + 1, 'account']
            # Combine first current row (to fill), with previous row (balance)
            # This fills NA values in the current row with the values from the previous row
            transactions.iloc[i + 1] = transactions.iloc[i + 1].combine_first(transactions.iloc[i])

            # Subtract transaction value to the appropriate account balance
            # Subtract because going backwards in time
            transactions.loc[i+1, account] -= transactions.loc[i+1, 'value']

            i += 1
            continue
        i += 1

    transactions.set_index('createdAt', inplace = True)
    transactions.sort_index(ascending = False, inplace = True)


transactions.to_csv('./test.csv')

if  __name__ == '__main__':
    addTrueBalance()
