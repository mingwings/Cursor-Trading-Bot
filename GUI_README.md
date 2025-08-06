# 🤖 Trading Bot Dashboard

A comprehensive web-based dashboard for monitoring and controlling your cryptocurrency trading bot, built with Streamlit.

## 🚀 Features

### 📊 Live Performance Dashboard
- **Real-time P&L tracking** with visual indicators
- **Win rate analysis** with trend visualization
- **Trade frequency monitoring**
- **Sharpe ratio calculation**
- **Equity curve visualization**
- **P&L distribution charts**

### 📈 Historical Analysis
- **Custom date range selection** for backtesting
- **Performance metrics comparison**
- **Interactive charts** with price and equity data
- **Drawdown analysis**
- **Risk-adjusted returns**

### ⚙️ Strategy Comparison
- **Multi-strategy comparison** (Bollinger Bands, MACD, RSI, etc.)
- **Performance benchmarking**
- **Strategy parameter optimization**
- **Visual comparison charts**

### 📋 Trade History
- **Comprehensive trade log** with filtering options
- **Trade status tracking** (FILLED, CANCELLED, PENDING)
- **P&L analysis per trade**
- **Export functionality**

### 🔧 Settings & Configuration
- **Strategy parameter adjustment** through GUI
- **Risk management settings**
- **API credential management**
- **Configuration import/export**

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Trading bot dependencies (see `requirements.txt`)

### Setup
1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   ```bash
   cp env.template .env
   # Edit .env with your API credentials
   ```

3. **Run the dashboard:**
   ```bash
   streamlit run trading_dashboard.py
   ```

## 🎯 Usage

### Starting the Dashboard
```bash
streamlit run trading_dashboard.py
```

The dashboard will open in your browser at `http://localhost:8501`

### Key Features

#### 🎛️ Sidebar Controls
- **Bot Status**: Start/stop the trading bot
- **Trading Configuration**: Select trading pairs and timeframes
- **Strategy Parameters**: Adjust Bollinger Bands and risk settings
- **Data Source**: Toggle between live trading and backtest data

#### 📊 Live Performance Tab
- Real-time performance metrics
- Interactive equity curve
- P&L distribution analysis
- Live market data refresh

#### 📈 Historical Analysis Tab
- Custom date range selection
- Backtest execution
- Performance visualization
- Risk metrics calculation

#### ⚙️ Strategy Comparison Tab
- Multi-strategy selection
- Performance benchmarking
- Visual comparison charts
- Strategy optimization

#### 📋 Trade History Tab
- Filterable trade log
- Trade statistics
- Export functionality
- Status tracking

#### 🔧 Settings Tab
- Configuration management
- API credential setup
- Import/export settings
- System preferences

## 🔧 Configuration

### Strategy Parameters
- **Bollinger Bands Window**: 5-50 (default: 10)
- **Standard Deviation**: 0.1-2.0 (default: 0.5)
- **Max Daily Trades**: 1-50 (default: 10)
- **Max Daily Loss**: 1.0-20.0% (default: 5.0%)
- **Base Risk per Trade**: 0.5-5.0% (default: 1.0%)

### Trading Pairs
Supported trading pairs:
- ETHUSDT
- BTCUSDT
- ADAUSDT
- DOTUSDT
- LINKUSDT

### Timeframes
Available timeframes:
- 1m (1 minute)
- 5m (5 minutes)
- 15m (15 minutes)
- 1h (1 hour)
- 4h (4 hours)
- 1d (1 day)

## 📊 Performance Metrics

### Key Indicators
- **Total P&L**: Overall profit/loss
- **Win Rate**: Percentage of profitable trades
- **Total Trades**: Number of executed trades
- **Sharpe Ratio**: Risk-adjusted return measure
- **Max Drawdown**: Largest peak-to-trough decline
- **Average P&L per Trade**: Mean profit/loss per trade

### Charts and Visualizations
- **Equity Curve**: Portfolio value over time
- **P&L Distribution**: Histogram of trade outcomes
- **Price Charts**: Asset price with indicators
- **Strategy Comparison**: Bar charts for strategy performance

## 🔒 Security Features

### API Credentials
- Secure credential input
- Environment variable support
- Encrypted storage (recommended for production)

### Risk Management
- Daily loss limits
- Position sizing controls
- Trade frequency limits
- Stop-loss and take-profit settings

## 🚀 Deployment

### Local Development
```bash
streamlit run trading_dashboard.py
```

### Production Deployment
For production deployment, consider:
- Using Streamlit Cloud
- Setting up proper authentication
- Implementing secure credential storage
- Adding monitoring and logging

### Environment Variables
Required environment variables:
```bash
BYBIT_API_KEY=your_api_key
BYBIT_API_SECRET=your_api_secret
```

## 🔄 Auto-refresh

The dashboard supports automatic data refresh:
- Enable auto-refresh for real-time updates
- Configurable refresh intervals
- Background data processing

## 📈 Data Sources

### Live Trading Data
- Real-time market data from Bybit API
- Live trade execution
- Current portfolio status

### Backtest Results
- Historical performance analysis
- Strategy optimization
- Risk assessment

### Combined View
- Toggle between live and historical data
- Comparative analysis
- Performance validation

## 🛠️ Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure all dependencies are installed
   - Check Python path configuration

2. **API Connection Issues**
   - Verify API credentials in `.env` file
   - Check network connectivity
   - Ensure API permissions are correct

3. **Data Loading Problems**
   - Check internet connection
   - Verify trading pair availability
   - Review API rate limits

### Debug Mode
Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## ⚠️ Disclaimer

This trading bot and dashboard are for educational purposes only. Cryptocurrency trading involves significant risk and can result in the loss of your invested capital. You should not invest more than you can afford to lose.

## 📞 Support

For issues and questions:
- Check the troubleshooting section
- Review the documentation
- Open an issue on GitHub

## 🔄 Updates

The dashboard is actively maintained with regular updates for:
- New features and improvements
- Bug fixes and security patches
- Performance optimizations
- UI/UX enhancements

---

**Happy Trading! 🚀📈** 