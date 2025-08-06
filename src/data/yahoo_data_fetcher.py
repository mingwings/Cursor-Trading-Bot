import pandas as pd
import yfinance as yf
from typing import Optional, Dict, List
import logging
from datetime import datetime, timedelta

class YahooDataFetcher:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing Yahoo Finance Data Fetcher...")
        
        # Available trading pairs
        self.available_pairs = {
            'BTCUSDT': 'BTC-USD',
            'ETHUSDT': 'ETH-USD',
            'ADAUSDT': 'ADA-USD',
            'DOTUSDT': 'DOT-USD',
            'LINKUSDT': 'LINK-USD',
            'BNBUSDT': 'BNB-USD',
            'SOLUSDT': 'SOL-USD',
            'MATICUSDT': 'MATIC-USD',
            'AVAXUSDT': 'AVAX-USD',
            'UNIUSDT': 'UNI-USD'
        }
    
    def get_historical_data(self, symbol: str, start_date: str, end_date: str, interval: str = '1h') -> Optional[pd.DataFrame]:
        """
        Get historical data from Yahoo Finance
        
        Args:
            symbol: Trading pair symbol (e.g., 'ETHUSDT')
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format
            interval: Data interval ('1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo')
            
        Returns:
            DataFrame with OHLCV data or None if failed
        """
        try:
            # Convert symbol to Yahoo Finance format
            yf_symbol = self.available_pairs.get(symbol, symbol)
            
            self.logger.info(f"Fetching historical data for {symbol} ({yf_symbol}) from {start_date} to {end_date}")
            
            # Download data
            data = yf.download(
                yf_symbol,
                start=start_date,
                end=end_date,
                interval=interval,
                progress=False
            )
            
            if data.empty:
                self.logger.warning(f"No data found for {symbol}")
                return None
            
            # Rename columns to match our expected format
            data = data.rename(columns={
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            })
            
            # Add timestamp column
            data['timestamp'] = data.index
            
            # Reset index to make timestamp a column
            data = data.reset_index(drop=True)
            
            self.logger.info(f"Successfully fetched {len(data)} records for {symbol}")
            return data
            
        except Exception as e:
            self.logger.error(f"Error fetching historical data for {symbol}: {str(e)}")
            return None
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """
        Get current price from Yahoo Finance
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            Current price as float or None if failed
        """
        try:
            yf_symbol = self.available_pairs.get(symbol, symbol)
            
            # Get current price
            ticker = yf.Ticker(yf_symbol)
            current_price = ticker.info.get('regularMarketPrice')
            
            if current_price:
                self.logger.info(f"Current {symbol} price: ${current_price:,.2f}")
                return float(current_price)
            else:
                self.logger.warning(f"Could not get current price for {symbol}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error fetching current price for {symbol}: {str(e)}")
            return None
    
    def get_available_symbols(self) -> List[str]:
        """Get list of available trading pairs"""
        return list(self.available_pairs.keys())
    
    def get_sample_data(self, symbol: str = 'ETHUSDT', days: int = 30) -> Optional[pd.DataFrame]:
        """
        Get sample data for testing
        
        Args:
            symbol: Trading pair symbol
            days: Number of days of data to fetch
            
        Returns:
            DataFrame with sample data
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        return self.get_historical_data(
            symbol=symbol,
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            interval='1h'
        )
    
    def get_klines(self, symbol: str, interval: int, limit: int = 1000) -> Optional[pd.DataFrame]:
        """
        Get klines data (compatible with existing interface)
        
        Args:
            symbol: Trading pair symbol
            interval: Interval in minutes
            limit: Number of records to fetch
            
        Returns:
            DataFrame with klines data
        """
        # Convert interval to Yahoo Finance format
        interval_map = {
            1: '1m',
            5: '5m',
            15: '15m',
            30: '30m',
            60: '1h',
            1440: '1d'
        }
        
        yf_interval = interval_map.get(interval, '1h')
        
        # Calculate date range based on limit and interval
        end_date = datetime.now()
        if interval <= 60:  # Intraday data
            # Yahoo Finance has limitations on intraday data
            start_date = end_date - timedelta(days=7)  # Max 7 days for intraday
        else:
            start_date = end_date - timedelta(days=limit)
        
        return self.get_historical_data(
            symbol=symbol,
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            interval=yf_interval
        ) 