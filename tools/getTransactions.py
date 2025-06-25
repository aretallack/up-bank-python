#%%########
##### #####
###########
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.api import ping_api, getAccounts, getTransactionIDs, getTransaction, getAllTransactions
from src.config import BASE_URL, HEADERS, TRANSACTIONS_OUT
from src.getBalances import getBalance

#%%########
##### #####
###########

def manualFlattenDictionary(dictionary: dict, paths: list[str], names: list[str]):
    if len(paths) != len(names):
        print('len(names) must match len(paths)')
        return

    outDictionary = {x: '' for x in names}

    for key, name in zip(paths, names):
        path = key.split(':')
        value = dictionary
        try:
            for p in path:
                value = value[p]
            outDictionary[name] = value
        except (KeyError, TypeError):
            # print(f"Warning: Path '{key}' could not be fully resolved in dictionary.")
            pass
    return outDictionary

def formatAsDataFrame(transactionDictionary):
    transactionDataFrame = pd.DataFrame.from_dict(transactionDictionary)
    transactionDataFrame.loc[:, 'value'] = transactionDataFrame['value'].astype(np.float64)
    # Set createdAt column as index, and convert to datetime
    transactionDataFrame.set_index('createdAt', inplace = True)
    transactionDataFrame.index = list(map(lambda x: pd.to_datetime(x, format="%Y-%m-%dT%H:%M:%S%z"), transactionDataFrame.index))
    transactionDataFrame.index = list(map(lambda x: x.astimezone('Australia/Adelaide'), transactionDataFrame.index))
    transactionDataFrame.index.name = 'createdAt'
    return transactionDataFrame

def mapAccountInfo(transactionDataFrame):
    # Get list of accounts, includes account name, id and saver vs transactional
    accounts = getAccounts()
    mappingName = {account[2]:account[0] for account in accounts}
    mappingType = {account[2]:account[1].title() for account in accounts}

    transactionDataFrame.loc[:,'accountName'] = transactionDataFrame['accountID'].map(mappingName)
    transactionDataFrame.loc[:,'accountType'] = transactionDataFrame['accountID'].map(mappingType)
    return transactionDataFrame

def sinceWhen(TRANSACTIONS_OUT, backtrackDays = 90):
    if os.path.exists(TRANSACTIONS_OUT):
        latestDate = pd.read_csv(TRANSACTIONS_OUT, index_col=0).index[0]
        
        if backtrackDays != None:
            backtrack = datetime.strptime(latestDate, '%Y-%m-%d %H:%M:%S%z') - timedelta(days = backtrackDays)
            tz = backtrack.strftime('%z')
            since = backtrack.strftime('%Y-%m-%dT%H:%M:%S')
            since = f'{since}{tz[0:3]}:{tz[3:5]}'
            return since
        since = latestDate.replace(' ', 'T')
        return since
    # If no existing file, since None. i.e. get all dates
    return None

def mergeToExisting(TRANSACTIONS_OUT, transactionDataFrame):
    existing = pd.read_csv(TRANSACTIONS_OUT, index_col=0, parse_dates=True)
    existing.index = list(map(lambda x: pd.to_datetime(x, format="%Y-%m-%d %H:%M:%S%z"), existing.index))
    existing.index = list(map(lambda x: x.astimezone('Australia/Adelaide'), existing.index))
    existing.index.name = 'createdAt'

    merged = pd.concat([existing, transactionDataFrame])
    # get rows with no ID out as these are lost in the grouping and aggregating
    # These rows are balances
    balances = merged[merged['id'].isna()]
    merged.reset_index(inplace = True)

    aggDict = {x:'first' for x in list(merged)}

    merged = merged.groupby('id').aggregate(aggDict)
    
    merged.set_index('createdAt', inplace = True)
    merged.index = list(map(lambda x: pd.to_datetime(x, format="%Y-%m-%d %H:%M:%S%z"), merged.index))
    merged.index.name = 'createdAt'

    # Add balances back in.
    merged = pd.concat([merged, balances])

    # Sort by datetime index
    merged = merged.sort_index(ascending = False)
    return merged


def backFillBalances(transactionDataFrame):
    '''
    Funtion to interpolate between actual API-retrieved balances, based on transaction information from each account
    Enables tracking of account balances by inference of incoming and outgoing values with reference to a point of truth
    '''
    transactionDataFrame = transactionDataFrame.reset_index()
    balanceCols = [x for x in list(transactionDataFrame) if 'Balance' in x]

    # Find index of first NA balance
    # No point looking through rows before this point
    # Probably 0 if addTrueBalance() has just been run.
    startIndex = transactionDataFrame[transactionDataFrame[balanceCols].isna().any(axis=1)].index
    if len(startIndex) > 0:
        startIndex = startIndex[0]
    else:
        startIndex = 0

    # From this point, iterate through to the current time
    i = startIndex
    while i <= transactionDataFrame.index.max():
        # Check if the balance of any account is NA and needs filling
        needFill = transactionDataFrame.loc[i, balanceCols].isna().any()

        if needFill: # If next row has no balance
            # Get account from which money moved to/from
            account = transactionDataFrame.loc[i, 'accountName']
            # Combine current row (to fill), with previous row (balance)
            # This fills NA values in the current row with the values from the previous row
            transactionDataFrame.loc[i, balanceCols] = transactionDataFrame.loc[i-1, balanceCols]

            # Currently, the balances represent the state they were in AFTER the following transaction
            # We need to know the state they were in after the current transaction
            # So, remove (subtract), the previous transaction from the current row (It technically hasnt happend yet)
            transactionDataFrame.loc[i, f'{account.lower()}Balance'] -= transactionDataFrame.loc[i - 1, 'value']

            i += 1
            continue
        i += 1

    transactionDataFrame.set_index('createdAt', inplace = True)
    transactionDataFrame.sort_index(ascending = False, inplace = True)
    return transactionDataFrame

def splitByAccount(transactionDataFrame):

    accountNames = np.unique(transactionDataFrame['accountName'])

    transactionsByAccount = {x: '' for x in accountNames}
    for name in accountNames:
        transactionsByAccount[name] = transactionDataFrame[transactionDataFrame['accountName'] == name]

    return transactionsByAccount


if __name__ == '__main__':

    ping_api()

    since = sinceWhen(TRANSACTIONS_OUT)
    
    params = {
    'page[size]': 100,
    'filter[since]': since
    }

    # Get all transaction data
    transactionDictionary = getAllTransactions(params)

    paths = [
        'type', 'id', 'attributes:status', 'attributes:rawText', 'attributes:description', 
        'attributes:message', 'attributes:roundUp', 'attributes:cashback', 'attributes:amount:currencyCode', 
        'attributes:amount:value', 'attributes:foreignAmount', 'attributes:cardPurchaseMethod:method', 
        'attributes:cardPurchaseMethod:cardNumberSuffix', 'attributes:settledAt', 'attributes:createdAt', 
        'attributes:transactionType', 'attributes:note', 'attributes:performingCustomer:displayName',
        'relationships:account:data:id', 'relationships:category:data:id', 'relationships:parentCategory:data:id', 
        'relationships:tags:data'
        ]
    names = [
        'type', 'id', 'status', 'rawText', 'description', 
        'message', 'roundUp', 'cashback', 'currencyCode', 
        'value', 'foreignAmount', 'cardPurchaseMethod', 
        'cardNumberSuffix', 'settledAt', 'createdAt', 
        'transactionType', 'note', 'displayName',
        'accountID', 'category', 'parentCategory', 'tags'
        ]

    transactionDictionary = [manualFlattenDictionary(x, paths, names) for x in transactionDictionary]
    transactionDataFrame = formatAsDataFrame(transactionDictionary)
    transactionDataFrame = mapAccountInfo(transactionDataFrame)

    transactionDataFrame = splitByAccount(transactionDataFrame)

    # Add current balance to top row
    balance = getBalance(BASE_URL, HEADERS)

    for account in transactionDataFrame.keys():
        temp = transactionDataFrame[account].copy()
        temp.loc[temp.index[0], f'{account.lower()}Balance'] = balance[f'{account.lower()}Balance']
        temp = backFillBalances(temp)
        transactionDataFrame[account] = temp

    transactionDataFrame = pd.concat([transactionDataFrame[x] for x in transactionDataFrame.keys()])
    transactionDataFrame.sort_index(inplace = True, ascending = False)

    # Fix tags col. unlist. 
    transactionDataFrame.loc[:,'tags'] = transactionDataFrame['tags'].apply(lambda x: x[0]['id'] if len(x) > 0 else '') 
 
    # If there is a saver (from balances) that has no transactions, create a transaction column with all zeros
    noTransactionSavers = [x for x in balance.keys() if x not in list(transactionDataFrame)]
    if len(noTransactionSavers) > 0:
        for name in noTransactionSavers:
            transactionDataFrame.loc[:,name] = 0
    
    transactionDataFrame[list(balance.keys())] = transactionDataFrame[list(balance.keys())].bfill()
    
    if since != None:
        transactionDataFrame = mergeToExisting(TRANSACTIONS_OUT, transactionDataFrame)

    transactionDataFrame.to_csv(TRANSACTIONS_OUT)

# %%
