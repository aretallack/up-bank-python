import requests
from src.config import API_KEY, BASE_URL, HEADERS

def firstRequest(params, url, HEADERS = HEADERS):
    request = requests.get(url, headers = HEADERS, params = params)
    return request

def iteratePages(request, params, HEADERS = HEADERS):
    # Add to a list for all transactions
    allData = request.json()['data'].copy()
    # Get links
    links = request.json()['links']

    # While there is a next link to click
    # Keep going next, and extend list of transactions
    while(links['next'] != None):
        nextRequest = requests.get(links['next'], headers=HEADERS, params=params)
        nextData = nextRequest.json()['data']
        allData.extend(nextData)
        links = nextRequest.json()['links']
    return allData