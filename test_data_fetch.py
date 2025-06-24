import logging
from src.data.data_fetcher import DataFetcher
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

if __name__ == "__main__":
    fetcher = DataFetcher()
    start_date = "2020-06-07"
    end_date = "2025-06-06"
    symbol = "ETHUSDT"  # Changed to ETHUSDT as per previous discussion
    kline_type = "60"    # Changed to 60 for 1-hour intervals

    print(f"Fetching historical data for {symbol} from {start_date} to {end_date}...")
    df = fetcher.get_historical_klines(
        symbol=symbol,
        kline_type=kline_type,
        start_time=int(pd.Timestamp(start_date).timestamp() * 1000),
        end_time=int(pd.Timestamp(end_date).timestamp() * 1000)
    )
    print(f"Data shape: {df.shape}")
    print(df.head())
    print(df.tail()) 