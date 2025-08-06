import pandas as pd
import requests
import time
from typing import Optional, Dict, List
import logging
from datetime import datetime, timedelta
import json

class CoinGeckoDataFetcher:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing CoinGecko Data Fetcher...")
        
        # CoinGecko API base URL
        self.base_url = "https://api.coingecko.com/api/v3"
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1.2  # CoinGecko allows 50 calls per minute
        
        # Available trading pairs mapping
        self.available_pairs = {
            'BTCUSDT': 'bitcoin',
            'ETHUSDT': 'ethereum',
            'ADAUSDT': 'cardano',
            'DOTUSDT': 'polkadot',
            'LINKUSDT': 'chainlink',
            'BNBUSDT': 'binancecoin',
            'SOLUSDT': 'solana',
            'MATICUSDT': 'matic-network',
            'AVAXUSDT': 'avalanche-2',
            'UNIUSDT': 'uniswap',
            'LTCUSDT': 'litecoin',
            'XRPUSDT': 'ripple',
            'DOGEUSDT': 'dogecoin',
            'SHIBUSDT': 'shiba-inu',
            'ATOMUSDT': 'cosmos',
            'NEARUSDT': 'near',
            'ALGOUSDT': 'algorand',
            'VETUSDT': 'vechain',
            'ICPUSDT': 'internet-computer',
            'FILUSDT': 'filecoin'
        }
        
        # Cache for coin IDs
        self._coin_ids_cache = None
        self._cache_timestamp = 0
        self._cache_duration = 3600  # 1 hour
    
    def _rate_limit(self):
        """Implement rate limiting for CoinGecko API"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            self.logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make a request to CoinGecko API with rate limiting"""
        try:
            self._rate_limit()
            
            url = f"{self.base_url}/{endpoint}"
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                self.logger.warning("Rate limit exceeded, waiting 60 seconds...")
                time.sleep(60)
                return self._make_request(endpoint, params)  # Retry
            else:
                self.logger.error(f"API request failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error making request to {endpoint}: {str(e)}")
            return None
    
    def get_coin_id(self, symbol: str) -> Optional[str]:
        """Get CoinGecko coin ID from symbol"""
        # First, try the hardcoded mapping
        if symbol in self.available_pairs:
            return self.available_pairs[symbol]
        
        # Check cache first
        if self._coin_ids_cache and (time.time() - self._cache_timestamp) < self._cache_duration:
            return self._coin_ids_cache.get(symbol)
        
        # Fetch from API as fallback
        try:
            data = self._make_request("coins/list")
            if data:
                # Create mapping
                self._coin_ids_cache = {}
                for coin in data:
                    symbol_upper = coin['symbol'].upper()
                    self._coin_ids_cache[f"{symbol_upper}USDT"] = coin['id']
                    self._coin_ids_cache[symbol_upper] = coin['id']
                
                self._cache_timestamp = time.time()
                return self._coin_ids_cache.get(symbol)
            
        except Exception as e:
            self.logger.error(f"Error fetching coin list: {str(e)}")
        
        # If all else fails, try to extract the base symbol
        if symbol.endswith('USDT'):
            base_symbol = symbol[:-4]  # Remove 'USDT'
            if base_symbol in self.available_pairs:
                return self.available_pairs[base_symbol + 'USDT']
        
        self.logger.warning(f"Could not find coin ID for {symbol}")
        return None
    
    def get_historical_data(self, symbol: str, start_date: str, end_date: str, interval: str = 'daily') -> Optional[pd.DataFrame]:
        """
        Get historical data from CoinGecko
        
        Args:
            symbol: Trading pair symbol (e.g., 'ETHUSDT')
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format
            interval: Data interval ('daily' only for CoinGecko free tier)
            
        Returns:
            DataFrame with OHLCV data or None if failed
        """
        try:
            # Get coin ID
            coin_id = self.get_coin_id(symbol)
            if not coin_id:
                self.logger.error(f"Could not find coin ID for {symbol}")
                return None
            
            # Convert dates to timestamps
            start_timestamp = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp())
            end_timestamp = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp())
            
            self.logger.info(f"Fetching historical data for {symbol} ({coin_id}) from {start_date} to {end_date}")
            
            # Make API request
            params = {
                'vs_currency': 'usd',
                'from': start_timestamp,
                'to': end_timestamp
            }
            
            data = self._make_request(f"coins/{coin_id}/market_chart/range", params)
            
            if not data or 'prices' not in data:
                self.logger.warning(f"No data found for {symbol}")
                return None
            
            # Convert to DataFrame
            prices = data['prices']
            volumes = data.get('total_volumes', [])
            
            # Create DataFrame
            df_data = []
            for i, (timestamp, price) in enumerate(prices):
                volume = volumes[i][1] if i < len(volumes) else 0
                
                df_data.append({
                    'timestamp': datetime.fromtimestamp(timestamp / 1000),
                    'open': price,
                    'high': price,
                    'low': price,
                    'close': price,
                    'volume': volume
                })
            
            df = pd.DataFrame(df_data)
            
            # For daily data, we only have OHLCV at daily intervals
            # For more granular data, we'd need to interpolate or use a different endpoint
            if interval != 'daily':
                self.logger.warning(f"CoinGecko free tier only supports daily data. Using daily data for {interval} request.")
            
            self.logger.info(f"Successfully fetched {len(df)} records for {symbol}")
            return df
            
        except Exception as e:
            self.logger.error(f"Error fetching historical data for {symbol}: {str(e)}")
            return None
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """
        Get current price from CoinGecko
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            Current price as float or None if failed
        """
        try:
            coin_id = self.get_coin_id(symbol)
            if not coin_id:
                self.logger.error(f"Could not find coin ID for {symbol}")
                return None
            
            self.logger.info(f"Fetching price for {symbol} using coin ID: {coin_id}")
            
            data = self._make_request(f"simple/price", {
                'ids': coin_id,
                'vs_currencies': 'usd'
            })
            
            self.logger.info(f"API response for {symbol}: {data}")
            
            if data and coin_id in data:
                current_price = data[coin_id]['usd']
                self.logger.info(f"Current {symbol} price: ${current_price:,.2f}")
                return float(current_price)
            else:
                self.logger.warning(f"Could not get current price for {symbol}. Response: {data}")
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
            interval='daily'
        )
    
    def get_klines(self, symbol: str, interval: int, limit: int = 1000) -> Optional[pd.DataFrame]:
        """
        Get klines data (compatible with existing interface)
        
        Args:
            symbol: Trading pair symbol
            interval: Interval in minutes (not used for CoinGecko daily data)
            limit: Number of days to fetch
            
        Returns:
            DataFrame with klines data
        """
        # Calculate date range based on limit
        end_date = datetime.now()
        start_date = end_date - timedelta(days=limit)
        
        return self.get_historical_data(
            symbol=symbol,
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            interval='daily'
        )
    
    def get_market_data(self, symbol: str) -> Optional[Dict]:
        """
        Get comprehensive market data for a symbol
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            Dictionary with market data or None if failed
        """
        try:
            coin_id = self.get_coin_id(symbol)
            if not coin_id:
                return None
            
            data = self._make_request(f"coins/{coin_id}", {
                'localization': 'false',
                'tickers': 'false',
                'market_data': 'true',
                'community_data': 'false',
                'developer_data': 'false',
                'sparkline': 'false'
            })
            
            if data and 'market_data' in data:
                return {
                    'current_price': data['market_data']['current_price']['usd'],
                    'market_cap': data['market_data']['market_cap']['usd'],
                    'total_volume': data['market_data']['total_volume']['usd'],
                    'price_change_24h': data['market_data']['price_change_24h'],
                    'price_change_percentage_24h': data['market_data']['price_change_percentage_24h'],
                    'market_cap_rank': data['market_cap_rank'],
                    'ath': data['market_data']['ath']['usd'],
                    'ath_date': data['market_data']['ath_date']['usd'],
                    'atl': data['market_data']['atl']['usd'],
                    'atl_date': data['market_data']['atl_date']['usd']
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error fetching market data for {symbol}: {str(e)}")
            return None
    
    def search_coins(self, query: str) -> List[Dict]:
        """
        Search for coins by name or symbol
        
        Args:
            query: Search query
            
        Returns:
            List of matching coins
        """
        try:
            data = self._make_request("search", {'query': query})
            
            if data and 'coins' in data:
                return data['coins']
            
            return []
            
        except Exception as e:
            self.logger.error(f"Error searching coins: {str(e)}")
            return [] 