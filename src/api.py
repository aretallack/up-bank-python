import requests
from src.config import API_KEY, BASE_URL, HEADERS

def ping_api():
    
    response = requests.get(F'{BASE_URL}/util/ping', headers=HEADERS)
    if response.status_code == 200:
        print(f"Success {response.json()['meta']['statusEmoji']}: Connected to API", )
    else:
        print(f"Error {response.json()['meta']['statusEmoji']}: Unable to connect to API")

if __name__ == '__main__':
    ping_api()