import pytest
import pandas as pd
import numpy as np
from src.bot.strategy import BollingerBandStrategy

@pytest.fixture
def config():
    return {
        'macd': {
            'fast_period': 12,
            'slow_period': 26,
            'signal_period': 9
        },
        'ml': {
            'prediction_threshold': 0.6
        }
    }

@pytest.fixture
def sample_data():
    # Create sample price data
    dates = pd.date_range(start='2023-01-01', periods=100, freq='H')
    prices = np.random.normal(100, 1, 100).cumsum()  # Random walk
    volumes = np.random.normal(1000, 100, 100)
    
    return pd.DataFrame({
        'timestamp': dates,
        'open': prices,
        'high': prices * 1.01,
        'low': prices * 0.99,
        'close': prices,
        'volume': volumes
    })

def test_strategy_initialization(config):
    strategy = BollingerBandStrategy(config)
    assert strategy.fast_period == 12
    assert strategy.slow_period == 26
    assert strategy.signal_period == 9

def test_calculate_indicators(config, sample_data):
    strategy = BollingerBandStrategy(config)
    df = strategy.calculate_indicators(sample_data)
    
    # Check if indicators are calculated
    assert 'macd' in df.columns
    assert 'macd_signal' in df.columns
    assert 'macd_hist' in df.columns
    assert 'rsi' in df.columns
    assert 'bollinger_upper' in df.columns
    assert 'bollinger_lower' in df.columns

def test_generate_signals(config, sample_data):
    strategy = BollingerBandStrategy(config)
    df = strategy.calculate_indicators(sample_data)
    df = strategy.generate_signals(df)
    
    # Check if signals are generated
    assert 'signal' in df.columns
    assert 'macd_crossover' in df.columns
    assert 'macd_crossunder' in df.columns
    assert 'rsi_oversold' in df.columns
    assert 'rsi_overbought' in df.columns
    assert 'bb_lower_touch' in df.columns
    assert 'bb_upper_touch' in df.columns
    
    # Check signal values
    assert df['signal'].isin([-1, 0, 1]).all()

def test_get_trade_recommendation(config, sample_data):
    strategy = BollingerBandStrategy(config)
    df = strategy.calculate_indicators(sample_data)
    df = strategy.generate_signals(df)
    
    # Test with ML prediction
    signal, confidence = strategy.get_trade_recommendation(df, 0.8)
    assert signal in [-1, 0, 1]
    assert 0 <= confidence <= 1
    
    # Test without ML prediction
    signal, confidence = strategy.get_trade_recommendation(df)
    assert signal in [-1, 0, 1]
    assert 0 <= confidence <= 1 