import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

from src.data.data_fetcher import DataFetcher
from src.bot.strategy import BollingerBandStrategy
from src.ml.model import MLModel
from src.bot.risk_manager import RiskManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BacktestEngine:
    def __init__(self, 
                 start_date: str,
                 end_date: str,
                 initial_balance: float = 1000.0,
                 trading_pair: str = "ETHUSDT"):
        self.start_date = start_date
        self.end_date = end_date
        self.initial_balance = initial_balance
        self.trading_pair = trading_pair
        self.data_fetcher = DataFetcher()
        self.macd_strategy = BollingerBandStrategy({
            'macd': {
                'fast_period': 6,
                'slow_period': 18,
                'signal_period': 6
            },
            'ml': {
                'prediction_threshold': 0.3
            }
        })
        self.ml_model = MLModel({
            'ml': {
                'window_size': 1000,
                'feature_columns': ['close', 'volume'],
                'target_column': 'target',
                'min_samples_for_training': 100,
                'retrain_interval': 24
            }
        })
        self.position_sizer = RiskManager({
            'risk': {
                'max_daily_trades': 100,
                'max_daily_loss_percentage': 10,
                'position_sizing': {
                    'base_risk_per_trade': 1,
                    'max_risk_per_trade': 5
                }
            }
        })
        
        # Performance metrics
        self.trades: List[Dict] = []
        self.equity_curve: List[float] = []
        self.current_balance = initial_balance
        self.current_position = 0
        
    def fetch_historical_data(self):
        """
        Fetch historical data from Bybit for the last 1000 5-minute candles.
        """
        try:
            # Calculate start_time as 1000 * 5 minutes ago
            end_time = int(datetime.now().timestamp() * 1000)
            start_time = end_time - (1000 * 5 * 60 * 1000)  # 1000 candles * 5 minutes * 60 seconds * 1000 milliseconds

            df = self.data_fetcher.get_historical_klines(
                symbol=self.trading_pair,
                kline_type='5',  # Bybit expects '5' for 5-minute candles
                start_time=start_time,
                end_time=end_time,
                limit=1000
            )
            return df
        except Exception as e:
            self.logger.error(f"Error fetching historical data: {str(e)}")
            raise
    
    def run_backtest(self) -> Dict:
        """Run the backtest and return performance metrics"""
        # Fetch historical data
        data = self.fetch_historical_data()
        
        # Initialize tracking variables
        self.current_balance = self.initial_balance
        self.current_position = 0
        self.trades = []
        self.equity_curve = [self.initial_balance]
        
        # Run simulation
        for i in range(len(data)):
            current_data = data.iloc[:i+1]
            if len(current_data) < 26:  # Need enough data for MACD
                continue
                
            # Train ML model periodically
            if i % self.ml_model.config['ml']['retrain_interval'] == 0 and len(current_data) >= self.ml_model.min_samples:
                logger.info(f"Training ML model at index {i}")
                self.ml_model.train(current_data)
                
            # Calculate indicators and signals
            current_data = self.macd_strategy.calculate_indicators(current_data)
            current_data = self.macd_strategy.generate_signals(current_data)
            macd_signal, macd_confidence = self.macd_strategy.get_trade_recommendation(current_data)
            ml_signal, ml_confidence = self.ml_model.predict(current_data)
            
            # Log signals for debugging
            logger.debug(f"Index {i}: MACD signal={macd_signal}, confidence={macd_confidence:.2f}, ML signal={ml_signal:.2f}, confidence={ml_confidence:.2f}")
            
            # Combine signals - force trades for testing
            final_signal = 0
            
            # Buy conditions: any positive MACD or ML signal
            if macd_signal > 0 or ml_signal > 0:
                final_signal = 1
                logger.info(f"[FORCE] Buy signal at index {i}: MACD={macd_signal}, ML={ml_signal}")
            # Sell conditions: any negative MACD or ML signal
            elif macd_signal < 0 or ml_signal < 0:
                final_signal = -1
                logger.info(f"[FORCE] Sell signal at index {i}: MACD={macd_signal}, ML={ml_signal}")
            else:
                logger.info(f"[FORCE] No trade at index {i}: MACD={macd_signal}, ML={ml_signal}")
            
            # Execute trades
            if final_signal != 0 and self.current_position == 0:
                # Calculate position size
                position_size = self.position_sizer.calculate_position_size(
                    self.current_balance,
                    current_data.iloc[-1]['close'],
                    1.0
                )
                
                # Record trade
                trade = {
                    'entry_date': current_data.index[-1],
                    'entry_price': current_data.iloc[-1]['close'],
                    'position_size': position_size,
                    'direction': 'long' if final_signal > 0 else 'short'
                }
                
                # Update position
                self.current_position = position_size if final_signal > 0 else -position_size
                logger.info(f"Opening {'long' if final_signal > 0 else 'short'} position of size {position_size}")
                
            elif self.current_position != 0:
                # Check for exit conditions
                if (self.current_position > 0 and final_signal < 0) or \
                   (self.current_position < 0 and final_signal > 0):
                    # Calculate P&L
                    pnl = self.current_position * (current_data.iloc[-1]['close'] - trade['entry_price'])
                    self.current_balance += pnl
                    
                    # Update trade record
                    trade['exit_date'] = current_data.index[-1]
                    trade['exit_price'] = current_data.iloc[-1]['close']
                    trade['pnl'] = pnl
                    trade['return_pct'] = (pnl / (abs(self.current_position) * trade['entry_price'])) * 100
                    
                    self.trades.append(trade)
                    logger.info(f"Closing position with P&L: {pnl:.2f} ({trade['return_pct']:.2f}%)")
                    self.current_position = 0
            
            # Update equity curve
            self.equity_curve.append(self.current_balance)
        
        return self.calculate_metrics()
    
    def calculate_metrics(self) -> Dict:
        """Calculate performance metrics"""
        if not self.trades:
            logger.warning("No trades were executed during the backtest period")
            return {
                'total_trades': 0,
                'win_rate': 0,
                'profit_factor': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0,
                'total_return': 0
            }
        
        # Basic metrics
        total_trades = len(self.trades)
        winning_trades = len([t for t in self.trades if t['pnl'] > 0])
        win_rate = winning_trades / total_trades
        
        # Profit metrics
        total_profit = sum([t['pnl'] for t in self.trades if t['pnl'] > 0])
        total_loss = abs(sum([t['pnl'] for t in self.trades if t['pnl'] < 0]))
        profit_factor = total_profit / total_loss if total_loss != 0 else float('inf')
        
        # Risk metrics
        returns = pd.Series([t['return_pct'] for t in self.trades])
        sharpe_ratio = returns.mean() / returns.std() if returns.std() != 0 else 0
        
        # Drawdown
        equity_curve = pd.Series(self.equity_curve)
        rolling_max = equity_curve.expanding().max()
        drawdowns = (equity_curve - rolling_max) / rolling_max
        max_drawdown = drawdowns.min()
        
        # Total return
        total_return = ((self.current_balance - self.initial_balance) / self.initial_balance) * 100
        
        logger.info(f"Backtest completed with {total_trades} trades")
        logger.info(f"Win rate: {win_rate*100:.2f}%")
        logger.info(f"Profit factor: {profit_factor:.2f}")
        logger.info(f"Total Return: {total_return:.2f}%")
        logger.info(f"Total Trades: {total_trades}")
        
        return {
            'total_trades': total_trades,
            'win_rate': win_rate * 100,
            'profit_factor': profit_factor,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown * 100,
            'total_return': total_return
        }
    
    def plot_results(self, save_path: str = None):
        """Plot backtest results"""
        # Create figure with subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [2, 1]})
        
        # Plot equity curve
        equity_curve = pd.Series(self.equity_curve)
        equity_curve.plot(ax=ax1, label='Equity Curve')
        ax1.set_title('Equity Curve')
        ax1.set_ylabel('Balance')
        ax1.grid(True)
        
        # Plot drawdown
        rolling_max = equity_curve.expanding().max()
        drawdowns = (equity_curve - rolling_max) / rolling_max
        drawdowns.plot(ax=ax2, label='Drawdown', color='red')
        ax2.set_title('Drawdown')
        ax2.set_ylabel('Drawdown %')
        ax2.grid(True)
        
        # Add metrics to plot
        metrics = self.calculate_metrics()
        metrics_text = f"""
        Total Return: {metrics['total_return']:.2f}%
        Win Rate: {metrics['win_rate']:.2f}%
        Profit Factor: {metrics['profit_factor']:.2f}
        Sharpe Ratio: {metrics['sharpe_ratio']:.2f}
        Max Drawdown: {metrics['max_drawdown']:.2f}%
        Total Trades: {metrics['total_trades']}
        """
        ax1.text(0.02, 0.98, metrics_text,
                transform=ax1.transAxes,
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
        plt.show()

def main():
    # Set up backtest parameters
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=5*365)).strftime('%Y-%m-%d')
    
    # Initialize and run backtest
    backtest = BacktestEngine(
        start_date=start_date,
        end_date=end_date,
        initial_balance=1000.0
    )
    
    # Run backtest
    metrics = backtest.run_backtest()
    
    # Print results
    logger.info("\nBacktest Results:")
    logger.info(f"Total Trades: {metrics['total_trades']}")
    logger.info(f"Win Rate: {metrics['win_rate']:.2f}%")
    logger.info(f"Profit Factor: {metrics['profit_factor']:.2f}")
    logger.info(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
    logger.info(f"Max Drawdown: {metrics['max_drawdown']:.2f}%")
    logger.info(f"Total Return: {metrics['total_return']:.2f}%")

    # Write summary to file
    with open('backtest_summary.txt', 'w') as f:
        f.write("Backtest Results:\n")
        f.write(f"Total Trades: {metrics['total_trades']}\n")
        f.write(f"Win Rate: {metrics['win_rate']:.2f}%\n")
        f.write(f"Profit Factor: {metrics['profit_factor']:.2f}\n")
        f.write(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}\n")
        f.write(f"Max Drawdown: {metrics['max_drawdown']:.2f}%\n")
        f.write(f"Total Return: {metrics['total_return']:.2f}%\n")

    # Plot results
    backtest.plot_results('backtest_results.png')

if __name__ == "__main__":
    main() 