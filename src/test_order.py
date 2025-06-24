import os
import logging
from dotenv import load_dotenv
from src.bot.trading_bot import TradingBot

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_order_placement():
    try:
        # Load environment variables
        load_dotenv()
        
        # Initialize the trading bot
        logger.info("Initializing trading bot...")
        bot = TradingBot(trading_pair='ETHUSDT', interval='5')
        
        # Get current market data
        logger.info("Fetching current market data...")
        df = bot.data_fetcher.get_klines('ETHUSDT', 5, limit=1)
        if df is None or df.empty:
            logger.error("Failed to fetch market data")
            return
            
        current_price = float(df.iloc[0]['close'])
        logger.info(f"Current ETH price: {current_price}")
        
        # Calculate order quantity for 100 USDT
        target_order_value = 100.0  # Target order value in USDT
        min_order_qty = 0.001  # Minimum order quantity in ETH
        
        # Calculate quantity needed for target value
        order_qty = target_order_value / current_price
        
        # Ensure we meet minimum quantity
        order_qty = max(order_qty, min_order_qty)
        
        # Round to 3 decimal places
        order_qty = round(order_qty, 3)
        
        # Calculate final order value
        order_value = order_qty * current_price
        
        logger.info(f"Order details - Quantity: {order_qty} ETH, Value: {order_value:.2f} USDT")
        
        # Attempt to place the order
        logger.info("Attempting to place buy order...")
        success = bot.place_order("Buy", order_qty, current_price)
        
        if success:
            logger.info("Order placed successfully!")
        else:
            logger.error("Failed to place order")
            
    except Exception as e:
        logger.error(f"Error in test: {str(e)}")

if __name__ == "__main__":
    test_order_placement() 