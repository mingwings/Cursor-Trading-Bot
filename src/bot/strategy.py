import pandas as pd
from ta.volatility import BollingerBands
import logging

logger = logging.getLogger(__name__)

class BollingerBandStrategy:
    def __init__(self, config=None):
        self.config = config
        self.window = 10  # Decreased from 20 to 10 for faster signals
        self.window_dev = 0.5  # Decreased from 1.0 to 0.5 for more signals

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        bb = BollingerBands(close=df['close'], window=self.window, window_dev=self.window_dev)
        df['bb_upper'] = bb.bollinger_hband()
        df['bb_lower'] = bb.bollinger_lband()
        df['bb_middle'] = bb.bollinger_mavg()
        return df

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = self.calculate_indicators(df)
        df['signal'] = 0
        
        # Buy signal when price is below middle band
        df.loc[df['close'] <= df['bb_middle'], 'signal'] = 1
        
        # Sell signal when price is above upper band
        df.loc[df['close'] >= df['bb_upper'], 'signal'] = -1

        logger.info(
            f"Index {df.index[-1] if hasattr(df, 'index') else 'N/A'} | "
            f"Time: {df.index[-1] if hasattr(df, 'index') else 'N/A'} | "
            f"Close: {df.iloc[-1]['close']} | "
            f"Signal: {df.iloc[-1]['signal']}"
        )
        return df

    def get_trade_recommendation(self, df: pd.DataFrame):
        if df.empty:
            return 0, 0.0
        latest_signal = df['signal'].iloc[-1]
        confidence = 1.0 if latest_signal != 0 else 0.0
        return latest_signal, confidence

    def generate_signal(self, df: pd.DataFrame) -> int:
        """
        Generate a single trading signal based on the latest data.
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            int: 1 for buy, -1 for sell, 0 for no action
        """
        df = self.generate_signals(df)
        return df['signal'].iloc[-1]

    def run_backtest(self, df: pd.DataFrame):
        # This method is not provided in the original file or the new code block
        # It's assumed to exist as it's called in the new code block
        pass

    def execute_trade(self, final_signal, current_data):
        if final_signal != 0 and self.current_position == 0:
            logger.info(f"Opening {'long' if final_signal > 0 else 'short'} position at {current_data.iloc[-1]['close']} on {current_data.index[-1]}")
        elif self.current_position != 0 and ((self.current_position > 0 and final_signal < 0) or (self.current_position < 0 and final_signal > 0)):
            logger.info(f"Closing position at {current_data.iloc[-1]['close']} on {current_data.index[-1]}")
