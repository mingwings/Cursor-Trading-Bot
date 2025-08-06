# 📊 Data Sources Comparison

This document compares the different data sources available for backtesting cryptocurrency trading strategies.

## 🎯 Available Data Sources

### 1. **Yahoo Finance (yfinance)**
**Status**: ✅ Implemented  
**Cost**: Free  
**API Key**: Not required  

#### ✅ Pros:
- **Easy Setup**: No API keys required
- **Fast**: Quick data fetching
- **Granular Data**: 1-minute intervals available
- **Reliable**: Stable and well-maintained
- **Comprehensive**: Covers major cryptocurrencies

#### ⚠️ Cons:
- **Limited Pairs**: Only major cryptocurrencies
- **No Intraday**: Limited to 1-minute minimum
- **Exchange Data**: Not direct exchange data

#### 📊 Data Quality:
- **OHLCV**: ✅ Complete
- **Volume**: ✅ Available
- **Timestamps**: ✅ Accurate
- **Gaps**: Minimal

#### 🔧 Setup:
```bash
pip install yfinance
```

#### 📈 Usage:
```python
from src.data.yahoo_data_fetcher import YahooDataFetcher

# Initialize
fetcher = YahooDataFetcher()

# Get current price
price = fetcher.get_current_price("ETHUSDT")

# Get historical data
data = fetcher.get_historical_data(
    symbol="ETHUSDT",
    start_date="2024-01-01",
    end_date="2024-02-01",
    interval="1h"
)
```

---

### 2. **CoinGecko API**
**Status**: ✅ Implemented  
**Cost**: Free (with rate limits)  
**API Key**: Not required  

#### ✅ Pros:
- **Comprehensive**: 13,000+ cryptocurrencies
- **Rich Data**: Market cap, volume, rankings
- **Search Function**: Find any coin by name/symbol
- **Market Data**: Additional metrics available
- **Reliable**: Well-established API

#### ⚠️ Cons:
- **Rate Limited**: 50 calls per minute
- **Daily Only**: Free tier limited to daily data
- **Slower**: Rate limiting makes it slower
- **No Intraday**: No minute/hourly data

#### 📊 Data Quality:
- **OHLCV**: ✅ Complete
- **Volume**: ✅ Available
- **Market Cap**: ✅ Available
- **Rankings**: ✅ Available
- **Timestamps**: ✅ Accurate

#### 🔧 Setup:
```bash
# No additional packages needed
# Uses requests library (already included)
```

#### 📈 Usage:
```python
from src.data.coingecko_data_fetcher import CoinGeckoDataFetcher

# Initialize
fetcher = CoinGeckoDataFetcher()

# Get current price
price = fetcher.get_current_price("ETHUSDT")

# Get historical data
data = fetcher.get_historical_data(
    symbol="ETHUSDT",
    start_date="2024-01-01",
    end_date="2024-02-01",
    interval="daily"
)

# Get market data
market_data = fetcher.get_market_data("ETHUSDT")

# Search coins
results = fetcher.search_coins("bitcoin")
```

---

### 3. **Alpha Vantage** (Future Implementation)
**Status**: 🔄 Planned  
**Cost**: Free tier available  
**API Key**: Required  

#### ✅ Pros:
- **High Quality**: Professional-grade data
- **Multiple Intervals**: 1min to daily
- **Real-time**: Live market data
- **Comprehensive**: Multiple data types

#### ⚠️ Cons:
- **API Key**: Registration required
- **Rate Limits**: Strict limits on free tier
- **Cost**: Paid tiers for high volume

---

### 4. **CSV/JSON Files** (Future Implementation)
**Status**: 🔄 Planned  
**Cost**: Free  
**API Key**: Not required  

#### ✅ Pros:
- **Offline**: No internet required
- **Custom**: Any data format
- **Fast**: No API calls
- **Unlimited**: No rate limits

#### ⚠️ Cons:
- **Manual**: Requires data download
- **Static**: No real-time updates
- **Limited**: Only historical data

---

## 📊 Detailed Comparison

| Feature | Yahoo Finance | CoinGecko | Alpha Vantage | CSV Files |
|---------|---------------|-----------|---------------|-----------|
| **Setup Difficulty** | ⭐⭐ | ⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Data Granularity** | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Coverage** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Speed** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Reliability** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Cost** | Free | Free | Free/Paid | Free |
| **Real-time** | ✅ | ✅ | ✅ | ❌ |
| **Historical** | ✅ | ✅ | ✅ | ✅ |
| **Volume Data** | ✅ | ✅ | ✅ | ✅ |
| **Market Cap** | ❌ | ✅ | ✅ | ✅ |

## 🎯 Recommendations

### **For Beginners**: Yahoo Finance
- **Why**: Easy setup, fast, reliable
- **Best for**: Quick testing, learning, basic strategies
- **Limitation**: Limited to major cryptocurrencies

### **For Research**: CoinGecko
- **Why**: Comprehensive coverage, rich data
- **Best for**: Exploring new coins, market analysis
- **Limitation**: Rate limited, daily data only

### **For Production**: Alpha Vantage (Future)
- **Why**: Professional-grade, real-time
- **Best for**: Live trading, high-frequency strategies
- **Limitation**: API key required, potential costs

### **For Custom Data**: CSV Files (Future)
- **Why**: Complete control, offline capability
- **Best for**: Custom datasets, research projects
- **Limitation**: Manual setup required

## 🚀 Quick Start Guide

### 1. **Test Yahoo Finance**:
```bash
python test_yahoo_data.py
```

### 2. **Test CoinGecko**:
```bash
python test_coingecko_data.py
```

### 3. **Run Backtest with Yahoo Finance**:
```bash
python backtest/yahoo_backtest_engine.py
```

### 4. **Run Backtest with CoinGecko**:
```bash
python backtest/coingecko_backtest_engine.py
```

### 5. **Launch Dashboard**:
```bash
streamlit run trading_dashboard.py
```

## 🔧 Configuration

### Dashboard Data Source Selection:
1. Open the dashboard
2. Go to sidebar → "Data Source"
3. Choose between "Yahoo Finance" or "CoinGecko"
4. The dashboard will automatically use the selected source

### Trading Pairs Available:

#### Yahoo Finance:
- BTCUSDT (Bitcoin)
- ETHUSDT (Ethereum)
- ADAUSDT (Cardano)
- DOTUSDT (Polkadot)
- LINKUSDT (Chainlink)
- BNBUSDT (Binance Coin)
- SOLUSDT (Solana)
- MATICUSDT (Polygon)
- AVAXUSDT (Avalanche)
- UNIUSDT (Uniswap)

#### CoinGecko:
- All Yahoo Finance pairs +
- LTCUSDT (Litecoin)
- XRPUSDT (Ripple)
- DOGEUSDT (Dogecoin)
- SHIBUSDT (Shiba Inu)
- ATOMUSDT (Cosmos)
- NEARUSDT (NEAR)
- ALGOUSDT (Algorand)
- VETUSDT (VeChain)
- ICPUSDT (Internet Computer)
- FILUSDT (Filecoin)
- And 13,000+ more...

## 📈 Performance Metrics

Both data sources provide the same performance metrics:
- **Total Return**: Percentage gain/loss
- **Sharpe Ratio**: Risk-adjusted returns
- **Max Drawdown**: Largest peak-to-trough decline
- **Win Rate**: Percentage of profitable trades
- **Total Trades**: Number of completed trades

## 🔍 Troubleshooting

### Yahoo Finance Issues:
1. **No data found**: Check internet connection
2. **Import error**: Install yfinance: `pip install yfinance`
3. **Symbol not found**: Verify symbol exists on Yahoo Finance

### CoinGecko Issues:
1. **Rate limit exceeded**: Wait 60 seconds and retry
2. **No data found**: Check internet connection
3. **Symbol not found**: Use search function to find correct symbol

## 🎯 Best Practices

1. **Start with Yahoo Finance** for quick testing
2. **Use CoinGecko** for comprehensive analysis
3. **Test both** before choosing your preferred source
4. **Consider rate limits** when running multiple backtests
5. **Cache data** when possible to avoid repeated API calls

---

**Happy Backtesting! 🚀📈** 