import requests
from src.config import API_KEY, BASE_URL, HEADERS

def ping_api():
    response = requests.get(F'{BASE_URL}/util/ping', headers=HEADERS)

    if response.status_code == 200:
        print("Success:", response.json())
    else:
        print(f"Error {response.status_code}: {response.text}")

if __name__ == '__main__':
    ping_api()