from src.bot.trading_bot import TradingBot
import os
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()
    
    # Initialize the trading bot
    bot = TradingBot(
        trading_pair='ETHUSDT',
        interval='5'
    )
    
    # Order ID from the recently placed order
    order_id = "1971135272045516288"
    
    try:
        print(f"\nChecking status for order: {order_id}")
        status = bot.check_order_status(order_id)
        print(f"\nOrder Status:")
        print(f"Response: {status}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 