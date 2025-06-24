from src.data.data_fetcher import DataFetcher

fetcher = DataFetcher()

try:
    print("Account balance (USDT):")
    print(fetcher.get_account_balance('USDT'))
except Exception as e:
    print(f"Error fetching account balance: {e}")

try:
    print("Recent klines (BTCUSDT, 5m):")
    df = fetcher.get_historical_klines('BTCUSDT', kline_type='5')
    print(df.head())
except Exception as e:
    print(f"Error fetching klines: {e}") 