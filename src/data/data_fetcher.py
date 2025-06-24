import os
import time
from typing import List, Dict, Optional
import pandas as pd
from pybit.unified_trading import HTTP
from dotenv import load_dotenv
import logging

class DataFetcher:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing DataFetcher...")
        
        try:
            load_dotenv()
            self.api_key = os.getenv('BYBIT_API_KEY')
            self.api_secret = os.getenv('BYBIT_API_SECRET')
            
            if not self.api_key or not self.api_secret:
                raise ValueError("API key or secret not found in environment variables")
            
            self.logger.info("Creating Bybit HTTP client...")
            self.client = HTTP(
                testnet=True,
                api_key=str(self.api_key),
                api_secret=str(self.api_secret)
            )
            self.logger.info("Bybit HTTP client created successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing DataFetcher: {str(e)}")
            raise

    def get_klines(self, symbol: str, interval: int, limit: int = 1000) -> Optional[pd.DataFrame]:
        """
        Get historical klines/candlestick data
        
        Args:
            symbol: Trading pair symbol
            interval: Kline interval in minutes
            limit: Number of klines to fetch (default: 1000)
            
        Returns:
            Optional[pd.DataFrame]: DataFrame of klines or None if failed
        """
        try:
            self.logger.info(f"Fetching klines for {symbol} with interval {interval}")
            response = self.client.get_kline(
                category="spot",
                symbol=symbol,
                interval=str(interval),
                limit=limit
            )
            
            if response.get('retCode') == 0 and response.get('result', {}).get('list'):
                klines = response['result']['list']
                self.logger.info(f"Successfully fetched {len(klines)} klines for {symbol}")
                
                # Convert to DataFrame
                df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover'])
                
                # Convert timestamp to datetime
                df['timestamp'] = pd.to_datetime(df['timestamp'].astype(int), unit='ms')
                
                # Convert numeric columns
                numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'turnover']
                df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric)
                
                return df
            else:
                self.logger.error(f"Failed to get klines: {response}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error fetching klines: {str(e)}")
            return None

    def get_current_price(self, symbol: str) -> float:
        """
        Get the current price for a symbol from Bybit.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            
        Returns:
            Current price as float
        """
        try:
            ticker = self.client.get_tickers(
                category="spot",
                symbol=symbol
            )
            return float(ticker['result']['list'][0]['lastPrice'])
        except Exception as e:
            self.logger.error(f"Error fetching current price for {symbol}: {str(e)}")
            raise

    def get_account_balance(self, currency: str) -> Dict:
        """
        Get account balance for a specific currency from Bybit.
        
        Args:
            currency: Currency symbol (e.g., 'USDT', 'BTC')
            
        Returns:
            Dictionary containing balance information
        """
        try:
            accounts = self.client.get_wallet_balance(
                accountType="UNIFIED",
                coin=currency
            )
            return accounts['result']['list'][0] if accounts['result']['list'] else None
        except Exception as e:
            self.logger.error(f"Error fetching balance for {currency}: {str(e)}")
            raise

    def get_order_book(self, symbol: str, limit: int = 20) -> Dict:
        """
        Get the order book for a symbol from Bybit.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            limit: Number of orders to return
            
        Returns:
            Dictionary containing order book data
        """
        try:
            return self.client.get_orderbook(
                category="spot",
                symbol=symbol,
                limit=limit
            )
        except Exception as e:
            self.logger.error(f"Error fetching order book for {symbol}: {str(e)}")
            raise

    def get_recent_trades(self, symbol: str, limit: int = 100) -> List[Dict]:
        """
        Get recent trades for a symbol from Bybit.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            limit: Number of trades to return
            
        Returns:
            List of recent trades
        """
        try:
            return self.client.get_public_trade_history(
                category="spot",
                symbol=symbol,
                limit=limit
            )
        except Exception as e:
            self.logger.error(f"Error fetching recent trades for {symbol}: {str(e)}")
            raise

    def get_valid_symbols(self, category: str = "spot") -> List[str]:
        """
        Get list of valid symbols for a given category from Bybit.
        
        Args:
            category: Trading category (spot, spot, etc.)
            
        Returns:
            List of valid symbols
        """
        try:
            self.logger.info(f"Fetching valid symbols for category {category}")
            response = self.client.get_instruments_info(
                category=category
            )
            
            if response.get('retCode') == 0 and response.get('result', {}).get('list'):
                symbols = [item['symbol'] for item in response['result']['list']]
                self.logger.info(f"Found {len(symbols)} valid symbols for {category}")
                return symbols
            else:
                self.logger.error(f"Failed to get valid symbols: {response}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error fetching valid symbols: {str(e)}")
            return [] 