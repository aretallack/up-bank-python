from .config import TRANSACTIONS_OUT, API_KEY, BASE_URL

def process_transactions():
    if os.path.exists(TRANSACTIONS_OUT):
        existing = pd.read_csv(TRANSACTIONS_OUT)
        lastDate, lastTime = existing['createdAt'][0].split('T')
        bufferDate = datetime.strftime(datetime.strptime(lastDate, '%Y-%m-%d') - timedelta(weeks = 16), '%Y-%m-%d')
        since = f'{bufferDate}T{lastTime}'
    else:
        since = None

    transDict = getTransactions(API_KEY, base_url= BASE_URL, since = since, headers = headers)

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