from src.api import ping_api
from src.getTransactions import processTransactions
from src.getBalances import processBalances

if __name__ == '__main__':
    ping_api()
    processTransactions()
    processBalances()
