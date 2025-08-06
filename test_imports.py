#!/usr/bin/env python3
"""
Test script to verify all imports work correctly
"""

import sys
from pathlib import Path

def test_imports():
    """Test all the imports used in the dashboard"""
    
    print("🧪 Testing imports...")
    
    # Add src to path
    src_path = Path(__file__).parent / "src"
    sys.path.insert(0, str(src_path))
    
    # Test basic imports
    try:
        import streamlit as st
        print("✅ streamlit imported successfully")
    except ImportError as e:
        print(f"❌ streamlit import failed: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ pandas imported successfully")
    except ImportError as e:
        print(f"❌ pandas import failed: {e}")
        return False
    
    try:
        import numpy as np
        print("✅ numpy imported successfully")
    except ImportError as e:
        print(f"❌ numpy import failed: {e}")
        return False
    
    try:
        import plotly.graph_objects as go
        print("✅ plotly imported successfully")
    except ImportError as e:
        print(f"❌ plotly import failed: {e}")
        return False
    
    # Test trading bot imports
    try:
        from bot.trading_bot import TradingBot
        print("✅ TradingBot imported successfully")
    except ImportError as e:
        print(f"❌ TradingBot import failed: {e}")
        print("   This is expected if API credentials are not set up")
    
    try:
        from bot.strategy import BollingerBandStrategy
        print("✅ BollingerBandStrategy imported successfully")
    except ImportError as e:
        print(f"❌ BollingerBandStrategy import failed: {e}")
    
    try:
        from data.data_fetcher import DataFetcher
        print("✅ DataFetcher imported successfully")
    except ImportError as e:
        print(f"❌ DataFetcher import failed: {e}")
    
    try:
        from backtest.backtest_engine import BacktestEngine
        print("✅ BacktestEngine imported successfully")
    except ImportError as e:
        print(f"❌ BacktestEngine import failed: {e}")
    
    print("\n🎉 Import test completed!")
    return True

if __name__ == "__main__":
    test_imports() 