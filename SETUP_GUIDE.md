# 🚀 Trading Bot Dashboard Setup Guide

This guide will help you set up the trading bot dashboard with real API credentials and data.

## 📋 Prerequisites

1. **Python 3.8+** installed
2. **Bybit API Account** (for real trading data)
3. **All dependencies** installed (see requirements.txt)

## 🔧 Step-by-Step Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up API Credentials

#### Option A: Using .env file (Recommended)
1. Copy the template file:
   ```bash
   cp env.template .env
   ```

2. Edit the `.env` file with your Bybit API credentials:
   ```env
   BYBIT_API_KEY=your_actual_api_key_here
   BYBIT_API_SECRET=your_actual_api_secret_here
   ```

#### Option B: Environment Variables
Set environment variables directly:
```bash
# Windows
set BYBIT_API_KEY=your_api_key
set BYBIT_API_SECRET=your_api_secret

# Linux/Mac
export BYBIT_API_KEY=your_api_key
export BYBIT_API_SECRET=your_api_secret
```

### 3. Get Bybit Testnet API Credentials

1. **Create Bybit Testnet Account** (if you don't have one)
   - Go to [Bybit Testnet](https://testnet.bybit.com/)
   - Sign up for a testnet account

2. **Generate Testnet API Keys**:
   - Log into your Bybit testnet account
   - Go to **API Management**
   - Click **Create New Key**
   - Set permissions:
     - ✅ **Read** (for market data)
     - ✅ **Trade** (for paper trading)
     - ✅ **Transfer** (if needed)
   - Save your API Key and Secret

3. **Testnet Features**:
   - Free testnet USDT for paper trading
   - Real market data but simulated trading
   - No real money involved
   - Perfect for testing strategies

### 4. Test Your Setup

First, test the imports:
```bash
python test_imports.py
```

Then, test the Bybit API connection:
```bash
python test_bybit_api.py
```

You should see:
```
✅ streamlit imported successfully
✅ pandas imported successfully
✅ numpy imported successfully
✅ plotly imported successfully
✅ TradingBot imported successfully
✅ BollingerBandStrategy imported successfully
✅ DataFetcher imported successfully
✅ BacktestEngine imported successfully

🔗 Testing Bybit API connection...
✅ DataFetcher initialized successfully
✅ Current ETHUSDT price: $1,234.56
✅ Successfully fetched 10 klines
   Latest close price: $1,234.56
✅ Successfully fetched account balance
🎉 Bybit API connection test completed successfully!
```

### 5. Launch the Dashboard

```bash
streamlit run trading_dashboard.py
```

The dashboard will open at `http://localhost:8501`

## 🔍 Troubleshooting

### Common Issues

#### 1. Import Errors
**Problem**: `ImportError: attempted relative import beyond top-level package`

**Solution**: 
- Ensure you're running from the project root directory
- Check that all dependencies are installed
- Verify the src directory structure

#### 2. API Connection Errors
**Problem**: `Failed to initialize DataFetcher`

**Solutions**:
- Check your `.env` file exists and has correct credentials
- Verify API keys are from testnet.bybit.com (not mainnet)
- Ensure API keys have proper permissions (Read, Trade)
- Test API connection manually:
  ```python
  from src.data.data_fetcher import DataFetcher
  df = DataFetcher()
  price = df.get_current_price('ETHUSDT')
  print(f"ETHUSDT price: ${price}")
  ```

#### 3. Missing Dependencies
**Problem**: `ModuleNotFoundError`

**Solution**:
```bash
pip install streamlit plotly pandas numpy pybit python-dotenv
```

#### 4. Network Issues
**Problem**: Timeout or connection errors

**Solutions**:
- Check internet connection
- Verify firewall settings
- Try using a VPN if needed
- Check if Bybit API is accessible from your location

### Debug Mode

Enable debug logging to see detailed error messages:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🔒 Security Best Practices

### API Key Security
1. **Never commit API keys** to version control
2. **Use environment variables** or `.env` files
3. **Set IP restrictions** on your API keys
4. **Use testnet** for development
5. **Regularly rotate** your API keys

### Production Deployment
1. **Use secure credential storage** (not .env files)
2. **Enable authentication** on the dashboard
3. **Use HTTPS** for web access
4. **Monitor API usage** and set rate limits
5. **Backup configurations** regularly

## 📊 Dashboard Features

Once set up, you'll have access to:

### 📈 Live Performance
- Real-time P&L tracking
- Live market data
- Portfolio performance charts
- Risk metrics

### 📊 Historical Analysis
- Custom date range backtesting
- Performance comparison
- Strategy optimization
- Risk assessment

### ⚙️ Strategy Management
- Parameter adjustment
- Strategy comparison
- Performance benchmarking
- Configuration management

### 📋 Trade History
- Complete trade log
- Filtering and sorting
- Export functionality
- Performance analytics

## 🚨 Important Notes

### Risk Disclaimer
- **This is for educational purposes only**
- **Cryptocurrency trading involves significant risk**
- **Never invest more than you can afford to lose**
- **Test thoroughly before using real money**

### API Limits
- Bybit has rate limits on API calls
- Monitor your usage to avoid hitting limits
- Consider implementing caching for frequently accessed data

### Data Accuracy
- Market data may have delays
- Verify critical data before making trading decisions
- Use multiple data sources for confirmation

## 🆘 Getting Help

If you encounter issues:

1. **Check the troubleshooting section** above
2. **Review error messages** carefully
3. **Test individual components** separately
4. **Check API documentation** for updates
5. **Verify your setup** step by step

## 🔄 Updates

Keep your dashboard updated:
```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

---

**Happy Trading! 🚀📈** 