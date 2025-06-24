import os
from dotenv import load_dotenv
from kucoin.client import Market, User
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_api_connection():
    try:
        # Load environment variables
        load_dotenv()
        
        # Get API credentials
        api_key = os.getenv('KUCOIN_API_KEY')
        api_secret = os.getenv('KUCOIN_API_SECRET')
        api_passphrase = os.getenv('KUCOIN_API_PASSPHRASE')
        
        # Verify credentials are loaded
        if not all([api_key, api_secret, api_passphrase]):
            logger.error("Missing API credentials in .env file")
            return False
            
        logger.info("API credentials loaded successfully")
        
        # Initialize API clients
        market_client = Market()
        user_client = User(
            key=api_key,
            secret=api_secret,
            passphrase=api_passphrase
        )
        
        # Test market data access
        logger.info("Testing market data access...")
        ticker = market_client.get_ticker('BTC-USDT')
        logger.info(f"Current BTC-USDT price: {ticker['price']}")
        
        # Test account access
        logger.info("Testing account access...")
        accounts = user_client.get_account_list(currency='USDT')
        if accounts:
            logger.info(f"USDT Balance: {accounts[0]['balance']}")
        else:
            logger.warning("No USDT account found")
            
        logger.info("API connection test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error testing API connection: {str(e)}")
        return False

if __name__ == "__main__":
    test_api_connection() 