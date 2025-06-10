import requests
import re
from src.requests import firstRequest, iteratePages
from src.config import API_KEY, BASE_URL, HEADERS

def ping_api():
    response = requests.get(F'{BASE_URL}/util/ping', headers=HEADERS)
    if response.status_code == 200:
        print(f"Success {response.json()['meta']['statusEmoji']}: Connected to API", )
    else:
        print(f"Error {response.json()['meta']['statusEmoji']}: Unable to connect to API")

def getAccounts(BASE_URL = BASE_URL, HEADERS = HEADERS):
    request = requests.get(f'{BASE_URL}/accounts', headers = HEADERS)
    data = request.json()['data']
    accounts = [(x['attributes']['displayName'], x['attributes']['accountType'], x['id']) for x in data]
    accounts = [(re.sub(r'[^a-zA-Z]', '', item[0]), item[1], item[2]) for item in accounts]
    return accounts

def getTransactionIDs(byAccount = False, BASE_URL = BASE_URL, HEADERS = HEADERS, accounts = None):
    '''
    Function to get transaction IDs, either accross all accounts, or per account.
    '''
    if byAccount:
        if accounts == None:
            print('accounts list from getAccounts() must be specified')
            return
        accountNames = [x[0] for x in accounts]
        transactions = {account: '' for account in accountNames}
        for account in accounts:
            name, accountType, accountID = account
            url = f'{BASE_URL}/accounts/{accountID}/transactions'
            print(f'Getting transaction IDs for {name}')
        
            request = firstRequest(params, url, HEADERS)
            data = iteratePages(request, params, HEADERS)
            transactionIDs = [x['id'] for x in data]
            transactions[name] = transactionIDs
        return transactions
            
    print('Getting transaction IDs')
    url = f'{BASE_URL}/transactions'
    request = firstRequest(params, url, HEADERS)
    data = iteratePages(request, HEADERS, params)
    transactionIDs = [x['id'] for x in data]
    return transactionIDs


def getTransaction(transactionID, HEADERS = HEADERS, BASE_URL = BASE_URL):
    '''
    Funtion to get transaction data, given a transaction ID
    '''
    url = f'{BASE_URL}/transactions/{transactionID}'
    request = firstRequest(params, url, HEADERS)
    data = request.json()
    return data

def getAllTransactions(params, BASE_URL = BASE_URL, HEADERS = HEADERS):
    url = f'{BASE_URL}/transactions'
    print(f'Getting transactions{f" since {params['filter[since]']}" if not params["filter[since]"] == None else ""}')
    request = firstRequest(params, url)
    data = iteratePages(request, params)
    return data

# def getTransactionsByAccount():
#     accountNames = [x[0] for x in accounts]
#     accountTransactions = {name: [] for name in accountNames}

#     for account in accounts:
#         name, accountType, accountID = account
#         print(f'Getting transactions for {name}')
#         fullUrl = f'{BASE_URL}/accounts/{accountID}/transactions'
        
#         request = firstRequest(
#             url = fullUrl,
#             headers = HEADERS,
#             params = params
#         )

#         allData = iteratePages(
#             request=request,
#             url = fullUrl,
#             headers = HEADERS,
#             params = params
#         )

#         allDataFlat = [flattenDictionary(x) for x in allData]
#         df = pd.DataFrame.from_dict(allDataFlat)
#         df.insert(len(list(df)), 'account', name)

#         accountTransactions[name] = df
#     allTransactions = pd.concat(accountTransactions)
#     allTransactions.index = range(len(allTransactions))


if __name__ == '__main__':
    ping_api()