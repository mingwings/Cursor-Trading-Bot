import os
import time
import yaml
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
import pandas as pd
import requests
import hashlib
import hmac
import uuid
from dotenv import load_dotenv
import json

from ..data.data_fetcher import DataFetcher
from .strategy import BollingerBandStrategy
from .risk_manager import RiskManager
from ..ml.model import MLModel

class TradingBot:
    def __init__(self, trading_pair='ETHUSDT', interval='5'):
        try:
            # Debug log at the beginning
            print(f"[DEBUG] __init__ - Starting initialization")
            print(f"[DEBUG] __init__ - Parameters: trading_pair={trading_pair}, interval={interval}")
            
            # Load environment variables
            print(f"[DEBUG] __init__ - Loading environment variables")
            load_dotenv()
            
            # Set trading pair and interval
            self.trading_pair = trading_pair  # Keep original trading pair format
            self.interval = int(interval)  # Convert interval to integer
            
            # Initialize data fetcher
            print(f"[DEBUG] __init__ - Initializing data fetcher")
            self.data_fetcher = DataFetcher()
            
            # Initialize strategy
            print(f"[DEBUG] __init__ - Initializing strategy")
            self.strategy = BollingerBandStrategy()
            
            # Initialize risk manager with default configuration
            print(f"[DEBUG] __init__ - Initializing risk manager")
            default_config = {
                'risk': {
                    'max_daily_trades': 10,
                    'max_daily_loss_percentage': 5.0,
                    'position_sizing': {
                        'base_risk_per_trade': 1.0,
                        'max_risk_per_trade': 2.0
                    }
                },
                'ml': {
                    'window_size': 20,
                    'target_column': 'future_returns',
                    'min_samples_for_training': 100,
                    'retrain_interval': 24  # hours
                }
            }
            self.risk_manager = RiskManager(default_config)
            self.ml_model = MLModel(default_config)
            
            # Initialize logger
            print(f"[DEBUG] __init__ - Initializing logger")
            self.logger = logging.getLogger(__name__)
            
            # Get API credentials from environment variables
            print(f"[DEBUG] __init__ - Getting API credentials")
            self.api_key = os.getenv('BYBIT_API_KEY')
            self.secret_key = os.getenv('BYBIT_API_SECRET')
            print(f"[DEBUG] __init__ - api_key type: {type(self.api_key)}, value: {self.api_key}")
            print(f"[DEBUG] __init__ - secret_key type: {type(self.secret_key)}, value: {self.secret_key}")
            
            if not self.api_key or not self.secret_key:
                raise ValueError("API credentials not found in environment variables")
            
            print(f"[DEBUG] __init__ - Initializing HTTP client")
            self.httpClient = requests.Session()
            self.recv_window = str(5000)
            self.url = "https://api-testnet.bybit.com"  # Testnet endpoint
            
            print(f"[DEBUG] __init__ - Initialization complete")
            
        except Exception as e:
            print(f"[ERROR] __init__ - Failed to initialize trading bot: {str(e)}")
            raise

    def genSignature(self, param_str: str) -> str:
        """
        Generate signature for API request
        
        Args:
            param_str: Parameter string to sign
            
        Returns:
            str: Generated signature
        """
        try:
            self.logger.debug(f"genSignature - param_str: {param_str}")
            self.logger.debug(f"genSignature - secret_key type: {type(self.secret_key)}, value: {self.secret_key}")
            
            # Convert secret key to bytes
            secret_key_bytes = self.secret_key.encode('utf-8')
            self.logger.debug(f"genSignature - secret_key bytes: {secret_key_bytes}")
            
            # Convert parameter string to bytes
            param_str_bytes = param_str.encode('utf-8')
            self.logger.debug(f"genSignature - param_str encoded: {param_str_bytes}")
            
            # Generate HMAC SHA256 signature
            signature = hmac.new(
                secret_key_bytes,
                param_str_bytes,
                hashlib.sha256
            ).hexdigest()
            
            self.logger.debug(f"genSignature - Generated signature: {signature}")
            return signature
            
        except Exception as e:
            self.logger.error(f"genSignature - Error: {str(e)}")
            raise

    def HTTP_Request(self, method: str, endpoint: str, params: dict, operation: str) -> dict:
        """
        Make an HTTP request to Bybit API
        
        Args:
            method: HTTP method (GET/POST)
            endpoint: API endpoint
            params: Request parameters
            operation: Operation name for logging
            
        Returns:
            dict: API response
        """
        try:
            # Get current timestamp in milliseconds
            timestamp = int(time.time() * 1000)
            
            # Add timestamp and recv_window to params
            params['timestamp'] = str(timestamp)
            params['recv_window'] = str(self.recv_window)
            
            # Sort parameters alphabetically
            sorted_params = dict(sorted(params.items()))
            
            # Generate signature
            param_str = '&'.join([f"{k}={v}" for k, v in sorted_params.items()])
            signature = hmac.new(
                bytes(self.secret_key, 'utf-8'),
                bytes(param_str, 'utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            # Add signature to params
            params['sign'] = signature
            
            # Add API key to headers
            headers = {
                'X-BAPI-API-KEY': self.api_key,
                'X-BAPI-SIGN': signature,
                'X-BAPI-SIGN-TYPE': '2',
                'X-BAPI-TIMESTAMP': str(timestamp),
                'X-BAPI-RECV-WINDOW': str(self.recv_window)
            }
            
            # Make request
            url = f"{self.url}{endpoint}"
            
            # For GET requests, add params to URL
            if method == 'GET':
                query_string = '&'.join([f"{k}={v}" for k, v in sorted_params.items()])
                url = f"{url}?{query_string}"
                response = self.httpClient.request(
                    method,
                    url,
                    headers=headers
                )
            else:
                response = self.httpClient.request(
                    method,
                    url,
                    json=sorted_params,
                    headers=headers
                )
            
            # Log response
            print(f"Response Status: {response.status_code}")
            print(f"Response Body: {response.text}")
            print(f"Response Headers: {response.headers}")
            
            # Parse response
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"{operation} - HTTP request failed: {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"{operation} - Error in HTTP request: {str(e)}")
            return None

    def generate_order_link_id(self) -> str:
        """
        Generate a unique order link ID
        
        Returns:
            str: Unique order link ID
        """
        try:
            # Generate a unique ID using timestamp and random string
            timestamp = str(int(time.time() * 1000))
            random_str = ''.join([str(int(time.time() * 1000))[-4:] for _ in range(4)])
            return f"order_{timestamp}_{random_str}"
        except Exception as e:
            self.logger.error(f"generate_order_link_id - Error: {str(e)}")
            raise

    def place_order(self, side: str, qty: float, current_price: float) -> bool:
        """
        Place an order
        
        Args:
            side: Order side (Buy/Sell)
            qty: Order quantity
            current_price: Current market price
            
        Returns:
            bool: True if order placed successfully
        """
        try:
            # Truncate quantity to 3 decimal places to meet Bybit's precision requirements
            # Using floor division to ensure we never round up
            qty = float(int(qty * 1000) / 1000)
            
            self.logger.info(f"place_order - Placing {side} order for {qty} {self.trading_pair}")
            
            # Calculate order value
            order_value = qty * current_price
            
            # Check minimum order value (usually 1 USDT for spot)
            if order_value < 1:
                self.logger.warning(f"place_order - Order value {order_value} USDT is below minimum of 1 USDT")
                return False
            
            # Generate unique order link ID
            order_link_id = self.generate_order_link_id()
            
            # Place the order with all required parameters
            response = self.data_fetcher.client.place_order(
                category="spot",
                symbol=self.trading_pair,
                side=side,
                orderType="Limit",
                qty=str(qty),
                price=str(current_price),
                timeInForce="GTC",
                orderLinkId=order_link_id,
                isLeverage=0,
                orderFilter="Order"
            )
            
            if response.get('retCode') == 0:
                self.logger.info(f"place_order - Order placed successfully: {response}")
                return True
            else:
                self.logger.error(f"place_order - Failed to place order: {response}")
                return False
                
        except Exception as e:
            self.logger.error(f"place_order - Error: {str(e)}")
            return False

    def check_order_status(self, order_id: str) -> Dict:
        """
        Check the status of an order using its order ID.
        
        Args:
            order_id: The order ID to check
            
        Returns:
            Dictionary containing order status information
        """
        try:
            print(f"[DEBUG] check_order_status - Checking status for order {order_id}")
            
            endpoint = "/v5/order/realtime"
            method = "GET"
            params = {
                "category": "spot",
                "orderId": order_id
            }
            
            response = self.HTTP_Request(method, endpoint, params, "Check Order Status")
            print(f"[DEBUG] check_order_status - Response: {response.text}")
            return response.json()
            
        except Exception as e:
            self.logger.error(f"Error checking order status: {str(e)}")
            raise

    def get_position(self) -> Optional[Dict]:
        """
        Get current position
        
        Returns:
            Optional[Dict]: Position data or None if error
        """
        try:
            self.logger.info(f"get_position - Getting position for {self.trading_pair}")
            
            # For spot trading, we need to check the wallet balance instead of positions
            response = self.data_fetcher.client.get_wallet_balance(
                accountType="UNIFIED",
                coin="ETH"  # Get ETH balance since we're trading ETH/USDT
            )
            
            if response.get('retCode') == 0:
                balance_data = response.get('result', {}).get('list', [{}])[0]
                self.logger.info(f"get_position - Full response: {response}")
                
                # Get ETH balance from coin list
                eth_balance = 0
                for coin in balance_data.get('coin', []):
                    if coin.get('coin') == 'ETH':
                        eth_balance = float(coin.get('walletBalance', 0))
                        break
                
                if eth_balance > 0:
                    return {
                        'size': eth_balance,
                        'side': 'Buy'  # If we have ETH, we're long
                    }
                return None
            else:
                self.logger.error(f"get_position - Failed to get position: {response}")
                return None
                
        except Exception as e:
            self.logger.error(f"get_position - Error: {str(e)}")
            return None

    def get_balance(self) -> Optional[Dict]:
        """
        Get current balance for the quote currency (e.g., USDT)
        
        Returns:
            Optional[Dict]: Balance information or None if error
        """
        try:
            self.logger.debug("get_balance - Getting current balance")
            response = self.data_fetcher.client.get_wallet_balance(
                accountType="UNIFIED",
                coin="USDT"
            )
            
            # Log the full response for debugging
            self.logger.info(f"get_balance - Full response: {response}")
            
            if response.get('retCode') == 0 and response.get('result', {}).get('list'):
                balance = response['result']['list'][0]
                self.logger.info(f"get_balance - Raw balance data: {balance}")
                
                if balance.get('coin'):
                    for coin in balance['coin']:
                        if coin['coin'] == 'USDT':
                            # Handle empty string values by defaulting to 0
                            return {
                                'totalAvailableBalance': float(coin.get('walletBalance', '0') or '0'),
                                'free': float(coin.get('availableToWithdraw', '0') or '0'),
                                'locked': float(coin.get('locked', '0') or '0')
                            }
                self.logger.warning("get_balance - USDT balance not found in response")
                return None
            else:
                self.logger.warning(f"get_balance - No balance data in response: {response}")
                return None
                
        except Exception as e:
            self.logger.error(f"get_balance - Error: {str(e)}")
            return None

    def run(self):
        """
        Run the trading bot
        """
        try:
            self.logger.info(f"Starting trading bot for {self.trading_pair} with {self.interval}m interval")
            
            while True:
                try:
                    # Fetch latest klines
                    df = self.data_fetcher.get_klines(self.trading_pair, self.interval)
                    if df is None or len(df) < 20:  # Need at least 20 candles for strategy
                        self.logger.warning("Not enough klines data")
                        time.sleep(self.interval * 60)
                        continue
                    
                    # Debug log the first few klines
                    self.logger.info(f"First kline: {df.iloc[0].to_dict()}")
                    self.logger.info(f"Last kline: {df.iloc[-1].to_dict()}")
                    
                    # Debug log the DataFrame
                    self.logger.info(f"DataFrame head:\n{df.head()}")
                    self.logger.info(f"DataFrame dtypes:\n{df.dtypes}")
                    
                    # Drop any rows with NaN values
                    df = df.dropna()
                    
                    if len(df) < 20:
                        self.logger.warning("Not enough valid klines data after cleaning")
                        time.sleep(self.interval * 60)
                        continue
                    
                    # Get latest price
                    latest_price = float(df['close'].iloc[-1])
                    if latest_price <= 0:
                        self.logger.warning(f"Invalid price: {latest_price}")
                        time.sleep(self.interval * 60)
                        continue
                    
                    # Get current position
                    position = self.get_position()
                    
                    # Get trading signal
                    signal = self.strategy.generate_signal(df)
                    self.logger.info(f"Index {len(df)-1} | Time: {df['timestamp'].iloc[-1]} | Close: {latest_price:.8f} | Signal: {signal}")
                    
                    # Calculate order quantity based on available balance
                    balance = self.get_balance()
                    if balance is None:
                        self.logger.error("Failed to get balance")
                        time.sleep(self.interval * 60)
                        continue
                        
                    available_balance = float(balance.get('totalAvailableBalance', 0))
                    if available_balance <= 0:
                        self.logger.warning(f"Invalid balance: {available_balance}")
                        time.sleep(self.interval * 60)
                        continue
                    
                    # Use 10% of portfolio value for each trade
                    target_order_value = available_balance * 0.10  # 10% of portfolio
                    min_order_qty = 0.01  # Minimum order quantity in ETH
                    
                    # Calculate quantity needed for target value
                    order_qty = target_order_value / latest_price
                    
                    # Ensure we meet minimum quantity
                    order_qty = max(order_qty, min_order_qty)
                    
                    # Round to 3 decimal places
                    order_qty = round(order_qty, 3)
                    
                    # Calculate final order value
                    order_value = order_qty * latest_price
                    
                    # Log order details
                    self.logger.info(f"Order details - Quantity: {order_qty} ETH, Value: {order_value:.2f} USDT")
                    
                    # Execute trades based on signals
                    if signal == 1:  # Buy signal
                        self.logger.info(f"Buy signal detected - Signal: {signal}, Position: {position}")
                        
                        # Calculate maximum position size (e.g., 50% of portfolio)
                        max_position_value = available_balance * 0.50  # Maximum 50% of portfolio in ETH
                        current_position_value = position['size'] * latest_price if position else 0
                        
                        if current_position_value < max_position_value:
                            # Calculate how much more we can buy
                            remaining_value = max_position_value - current_position_value
                            additional_qty = min(order_qty, remaining_value / latest_price)
                            
                            if additional_qty >= min_order_qty:
                                self.logger.info(f"Attempting to place buy order - Price: {latest_price:.8f} | Quantity: {additional_qty}")
                                order_result = self.place_order("Buy", additional_qty, latest_price)
                                self.logger.info(f"Order placement result: {order_result}")
                            else:
                                self.logger.info(f"Additional quantity {additional_qty} ETH is below minimum order quantity {min_order_qty} ETH")
                        else:
                            self.logger.info(f"Maximum position size reached. Current: {current_position_value:.2f} USDT, Max: {max_position_value:.2f} USDT")
                            
                    elif signal == -1 and position is not None:  # Sell signal
                        self.logger.info(f"Sell signal detected - Signal: {signal}, Position: {position}")
                        self.logger.info(f"Attempting to place sell order - Price: {latest_price:.8f} | Quantity: {position['size']}")
                        order_result = self.place_order("Sell", position['size'], latest_price)
                        self.logger.info(f"Order placement result: {order_result}")
                    else:
                        self.logger.info(f"No trade executed - Signal: {signal}, Position: {position}")
                    
                    # Wait for next interval
                    time.sleep(self.interval * 60)
                    
                except KeyboardInterrupt:
                    self.logger.info("Trading bot stopped by user")
                    break
                except Exception as e:
                    self.logger.error(f"Error in run loop: {str(e)}")
                    time.sleep(self.interval * 60)
                    
        except Exception as e:
            self.logger.error(f"Error running trading bot: {str(e)}")
            raise

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    bot = TradingBot()
    bot.run() 