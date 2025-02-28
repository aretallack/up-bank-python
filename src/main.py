from src.api import ping_api
from transactions import getTransactions, transDict_to_df

if __name__ == '__main__':
    ping_api()
    process_transactions()
    
