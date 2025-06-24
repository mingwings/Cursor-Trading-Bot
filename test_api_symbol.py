import requests

def test_symbol(symbol):
    url = 'https://api-testnet.bybit.com/v5/market/tickers'
    params = {'category': 'spot', 'symbol': symbol}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data.get('retCode') == 0:
            print(f"Symbol {symbol} is valid.")
        else:
            print(f"Symbol {symbol} is not valid. Error: {data.get('retMsg')}")
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")

if __name__ == '__main__':
    test_symbol('ETHUSDT') 