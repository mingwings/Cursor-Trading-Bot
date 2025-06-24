# KuCoin Trading Bot with MACD and ML Strategy

A sophisticated cryptocurrency trading bot that implements a MACD (Moving Average Convergence Divergence) strategy enhanced with machine learning decision making. The bot uses a sliding window approach with decision trees to optimize trading decisions based on historical patterns.

## Features

- MACD-based trading strategy
- Machine learning component using sliding window decision trees
- Real-time market data processing
- Automated trade execution
- Risk management system
- Performance tracking and analytics
- Configurable parameters
- Comprehensive logging system

## Prerequisites

- Python 3.8+
- KuCoin API credentials
- Basic understanding of cryptocurrency trading

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/kucoin-trading-bot.git
cd kucoin-trading-bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your environment variables:
   - Copy the template file: `cp env.template .env`
   - Edit `.env` file with your actual KuCoin API credentials:
```
KUCOIN_API_KEY=your_actual_api_key
KUCOIN_API_SECRET=your_actual_api_secret
KUCOIN_API_PASSPHRASE=your_actual_passphrase
```

## Security Best Practices

⚠️ **IMPORTANT**: Never commit your `.env` file to version control!

- The `.env` file is already included in `.gitignore` to prevent accidental commits
- Keep your API credentials secure and never share them publicly
- Consider using environment variables in production deployments
- Regularly rotate your API keys for enhanced security
- Use API keys with minimal required permissions (read-only for testing)

## Project Structure

```
kucoin-trading-bot/
├── src/
│   ├── bot/
│   │   ├── __init__.py
│   │   ├── trading_bot.py
│   │   ├── strategy.py
│   │   └── risk_manager.py
│   ├── ml/
│   │   ├── __init__.py
│   │   ├── model.py
│   │   └── feature_engineering.py
│   ├── data/
│   │   ├── __init__.py
│   │   └── data_fetcher.py
│   └── utils/
│       ├── __init__.py
│       └── logger.py
├── tests/
│   ├── __init__.py
│   ├── test_strategy.py
│   └── test_ml_model.py
├── config/
│   └── config.yaml
├── requirements.txt
├── .gitignore
├── env.template
└── README.md
```

## Usage

1. Configure your trading parameters in `config/config.yaml`
2. Run the bot:
```bash
python src/bot/trading_bot.py
```

## Configuration

The bot can be configured through the `config/config.yaml` file. Key parameters include:

- Trading pairs
- MACD parameters
- Risk management settings
- ML model parameters
- Trading limits

## Testing

Run the test suite:
```bash
pytest tests/
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This trading bot is for educational purposes only. Use at your own risk. Cryptocurrency trading involves significant risk and can result in the loss of your invested capital. You should not invest more than you can afford to lose.

## Acknowledgments

- KuCoin API for providing the trading interface
- TA-Lib for technical analysis indicators
- Scikit-learn for machine learning capabilities 