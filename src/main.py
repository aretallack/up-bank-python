from src.api import ping_api
from src.transactions import process_transactions
from src.getBalances import processBalances

if __name__ == '__main__':
    ping_api()
    process_transactions()
    processBalances()
