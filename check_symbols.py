from src.data.data_fetcher import DataFetcher
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Initialize data fetcher
    data_fetcher = DataFetcher()
    
    # Get valid symbols for spot trading
    spot_symbols = data_fetcher.get_valid_symbols(category="spot")
    logger.info("\nValid spot symbols:")
    for symbol in sorted(spot_symbols):
        logger.info(symbol)

if __name__ == "__main__":
    main() 