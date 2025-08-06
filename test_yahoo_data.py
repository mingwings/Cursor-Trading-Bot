#!/usr/bin/env python3
"""
Test script to verify Yahoo Finance data fetching
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def test_yahoo_data():
    """Test Yahoo Finance data fetching"""
    try:
        from data.yahoo_data_fetcher import YahooDataFetcher
        
        print("🔗 Testing Yahoo Finance data fetching...")
        
        # Initialize data fetcher
        data_fetcher = YahooDataFetcher()
        print("✅ YahooDataFetcher initialized successfully")
        
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
        
        # Test available symbols
        symbols = data_fetcher.get_available_symbols()
        print(f"\n📋 Available symbols: {len(symbols)}")
        for symbol in symbols[:5]:  # Show first 5
            print(f"   - {symbol}")
        
        print("\n🎉 Yahoo Finance data test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Yahoo Finance data test failed: {str(e)}")
        print("\n🔧 Troubleshooting:")
        print("1. Check internet connection")
        print("2. Install yfinance: pip install yfinance")
        print("3. Verify the symbol exists on Yahoo Finance")
        return False

if __name__ == "__main__":
    test_yahoo_data() 