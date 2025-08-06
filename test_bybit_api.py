#!/usr/bin/env python3
"""
Test script to verify Bybit API connection
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def test_bybit_connection():
    """Test Bybit API connection"""
    try:
        from data.data_fetcher import DataFetcher
        
        print("🔗 Testing Bybit API connection...")
        
        # Initialize data fetcher
        data_fetcher = DataFetcher()
        print("✅ DataFetcher initialized successfully")
        
        # Test current price
        symbol = "ETHUSDT"
        price = data_fetcher.get_current_price(symbol)
        print(f"✅ Current {symbol} price: ${price:,.2f}")
        
        # Test klines data
        klines = data_fetcher.get_klines(symbol, 5, 10)
        if klines is not None:
            print(f"✅ Successfully fetched {len(klines)} klines")
            print(f"   Latest close price: ${klines['close'].iloc[-1]:,.2f}")
        else:
            print("❌ Failed to fetch klines data")
        
        # Test account balance
        try:
            balance = data_fetcher.get_account_balance("USDT")
            if balance:
                print("✅ Successfully fetched account balance")
            else:
                print("⚠️ No balance data available (normal for testnet)")
        except Exception as e:
            print(f"⚠️ Balance check failed: {e}")
        
        print("\n🎉 Bybit API connection test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Bybit API connection failed: {str(e)}")
        print("\n🔧 Troubleshooting:")
        print("1. Check your .env file has correct API credentials")
        print("2. Verify your API keys are from testnet.bybit.com")
        print("3. Ensure API keys have proper permissions")
        print("4. Check your internet connection")
        return False

if __name__ == "__main__":
    test_bybit_connection() 