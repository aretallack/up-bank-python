import os
import pandas as pd
import requests
from datetime import datetime, timedelta
from src.config import API_KEY, BASE_URL, TRANSACTIONS_OUT, HEADERS

def getTransactions(API_KEY, BASE_URL, HEADERS, since = None):
    print('Getting latest transactions')
    
    params = {
        'page[size]': 100,
        'filter[since]': since,
        }

    # Get most recent request
    first_request= requests.get(f'{BASE_URL}/transactions', headers = HEADERS)
    transactions = first_request.json()['data']
    # Add to a list for all transactions
    all_transactions = transactions.copy()
    # Get links
    links = first_request.json()['links']

    # While there is a next link to click
    # Keep going next, and extend list of transactions
    while(links['next'] != None):
        next_request = requests.get(links['next'], headers=HEADERS, params=params)
        next_transaction = next_request.json()['data']
        all_transactions.extend(next_transaction)
        links = next_request.json()['links']
    return all_transactions


def transDict_to_df(transactionDict, attrList):
    print('Formatting transactions to dataframe')
    for i in range(len(transactionDict)):
        transaction = transactionDict[i].copy()
        transid = {'id': transaction['id']}
        attributes = transaction['attributes']
        attributes = {k: attributes[k] for k in attrList if k in attributes}
        ammountInfo = attributes['amount']
        attributes.update(ammountInfo)
        del attributes['amount']
        if attributes['cardPurchaseMethod'] is not None:
            cardPurchaseInfo = attributes['cardPurchaseMethod']
            attributes.update(cardPurchaseInfo)
            del attributes['cardPurchaseMethod']
            del attributes['method']

        parentCat = transaction['relationships']['parentCategory']
        if parentCat['data'] is None:
            parentCat = {'parentCategory': None}
        else:
            parentCat = {'parentCategory': parentCat['data']['id']} 
        
        cat = transaction['relationships']['category']
        if cat['data'] is  None:
            cat = {'category': None}
        else:
            cat = {'category': cat['data']['id']}
        
        outDict = {}
        outDict.update(transid)
        outDict.update(attributes)
        outDict.update(parentCat)
        outDict.update(cat)

        if i == 0:
            transactions_df = pd.DataFrame(outDict, index = [i])
        else:
            transactions_df = pd.concat([transactions_df, pd.DataFrame(outDict, index = [i])], axis = 0)
    return transactions_df

def process_transactions():
    if os.path.exists(TRANSACTIONS_OUT):
        existing = pd.read_csv(TRANSACTIONS_OUT)
        lastDate, lastTime = existing['createdAt'][0].split('T')
        bufferDate = datetime.strftime(datetime.strptime(lastDate, '%Y-%m-%d') - timedelta(weeks = 16), '%Y-%m-%d')
        since = f'{bufferDate}T{lastTime}'
    else:
        since = None

    transDict = getTransactions(API_KEY, BASE_URL = BASE_URL, since = since, HEADERS = HEADERS)

    attrList = [
        'status', 'rawText', 'description', 'amount', 
        'message', 'cardPurchaseMethod', 'settledAt', 
        'createdAt', 'transactionType', 'Note'
        ]

    # Dataframe of latest transactions
    transDF = transDict_to_df(transDict, attrList)

    if os.path.exists(TRANSACTIONS_OUT):
        existing = pd.read_csv(TRANSACTIONS_OUT)
        merged = pd.concat([existing, transDF])
        merged = merged.groupby('id').aggregate({
            'id': 'first',
            'status': 'last',
            'rawText': 'last',
            'description': 'last',
            'message': 'last',
            'settledAt': 'last',
            'createdAt': 'last',
            'transactionType': 'last',
            'category': 'last',
            'value': 'last',
            'valueInBaseUnits': 'last',
            'cardNumberSuffix': 'last',
            'cardNumberSuffix': 'last',
            'parentCategory': 'last'
        })
        if len(transDF) != 0:
            transDF = pd.concat([transDF, existing])
            transDF = transDF.sort_values('createdAt', ascending = False)
            transDF.to_csv(TRANSACTIONS_OUT, index = False)
        else:
            print('No new transactions')
    else:
        transDF.to_csv(TRANSACTIONS_OUT, index = False)


if __name__ == '__main__':
    process_transactions()
    