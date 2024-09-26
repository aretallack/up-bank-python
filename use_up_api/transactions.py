import requests
import pandas as pd

def getTransactions(api_key, base_url, headers, since = None):
    print('Getting latest transactions')
    
    params = {
        'page[size]': 100,
        'filter[since]': since,
        }

    # Get most recent request
    first_request= requests.get(f'{base_url}/transactions', headers = headers)
    transactions = first_request.json()['data']
    # Add to a list for all transactions
    all_transactions = transactions.copy()
    # Get links
    links = first_request.json()['links']

    # While there is a next link to click
    # Keep going next, and extend list of transactions
    while(links['next'] != None):
        next_request = requests.get(links['next'], headers=headers, params=params)
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