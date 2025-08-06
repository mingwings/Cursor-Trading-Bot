#!/usr/bin/env python3
"""
Test script to verify CoinGecko API data fetching
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def test_coingecko_data():
    """Test CoinGecko API data fetching"""
    try:
        from data.coingecko_data_fetcher import CoinGeckoDataFetcher
        
        print("🔗 Testing CoinGecko API data fetching...")
        
        # Initialize data fetcher
        data_fetcher = CoinGeckoDataFetcher()
        print("✅ CoinGeckoDataFetcher initialized successfully")
        
        # Test current price
        symbol = "ETHUSDT"
        price = data_fetcher.get_current_price(symbol)
        if price:
            print(f"✅ Current {symbol} price: ${price:,.2f}")
        else:
            print(f"❌ Failed to get current price for {symbol}")
        
        # Test historical data
        print("\n📊 Testing historical data...")
        data = data_fetcher.get_sample_data(symbol, days=7)
        if data is not None and not data.empty:
            print(f"✅ Successfully fetched {len(data)} records")
            print(f"   Date range: {data['timestamp'].iloc[0]} to {data['timestamp'].iloc[-1]}")
            print(f"   Latest close price: ${data['close'].iloc[-1]:,.2f}")
            print(f"   Columns: {list(data.columns)}")
        else:
            print("❌ Failed to fetch historical data")
        
        # Test market data
        print("\n📈 Testing market data...")
        market_data = data_fetcher.get_market_data(symbol)
        if market_data:
            print(f"✅ Market data for {symbol}:")
            print(f"   Market Cap: ${market_data['market_cap']:,.0f}")
            print(f"   24h Volume: ${market_data['total_volume']:,.0f}")
            print(f"   24h Change: {market_data['price_change_percentage_24h']:.2f}%")
            print(f"   Market Rank: #{market_data['market_cap_rank']}")
        else:
            print("❌ Failed to fetch market data")
        
        # Test available symbols
        symbols = data_fetcher.get_available_symbols()
        print(f"\n📋 Available symbols: {len(symbols)}")
        for symbol in symbols[:5]:  # Show first 5
            print(f"   - {symbol}")
        
        # Test coin search
        print("\n🔍 Testing coin search...")
        search_results = data_fetcher.search_coins("bitcoin")
        if search_results:
            print(f"✅ Found {len(search_results)} results for 'bitcoin'")
            for i, coin in enumerate(search_results[:3]):
                print(f"   {i+1}. {coin['name']} ({coin['symbol'].upper()}) - Rank: {coin['market_cap_rank']}")
        else:
            print("❌ Failed to search coins")
        
        print("\n🎉 CoinGecko API data test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ CoinGecko API data test failed: {str(e)}")
        print("\n🔧 Troubleshooting:")
        print("1. Check internet connection")
        print("2. Verify CoinGecko API is accessible")
        print("3. Check if rate limits are exceeded")
        print("4. Ensure all dependencies are installed")
        return False

if __name__ == "__main__":
    test_coingecko_data() 