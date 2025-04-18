import os
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env file

API_KEY = os.getenv('API_KEY')
BASE_URL = 'https://api.up.com.au/api/v1'
TRANSACTIONS_OUT = './output/transactions.csv'
BALANCES_OUT = './output/balances.csv'
HEADERS = {"Authorization": f'Bearer {API_KEY}'}

os.makedirs(os.path.dirname(TRANSACTIONS_OUT), exist_ok = True)