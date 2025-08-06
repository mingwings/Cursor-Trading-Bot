import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

from src.data.coingecko_data_fetcher import CoinGeckoDataFetcher
from src.bot.strategy import BollingerBandStrategy
from src.ml.model import MLModel
from src.bot.risk_manager import RiskManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CoinGeckoBacktestEngine:
    def __init__(self, 
                 start_date: str,
                 end_date: str,
                 initial_balance: float = 1000.0,
                 trading_pair: str = "ETHUSDT"):
        self.start_date = start_date
        self.end_date = end_date
        self.initial_balance = initial_balance
        self.trading_pair = trading_pair
        self.data_fetcher = CoinGeckoDataFetcher()
        self.strategy = BollingerBandStrategy({
            'bb_window': 10,
            'bb_deviation': 0.5
        })
        self.ml_model = MLModel({
            'ml': {
                'window_size': 100,
                'feature_columns': ['close', 'volume'],
                'target_column': 'target',
                'min_samples_for_training': 100,
                'retrain_interval': 24
            }
        })
        self.risk_manager = RiskManager({
            'risk': {
                'max_daily_trades': 10,
                'max_daily_loss_percentage': 5.0,
                'position_sizing': {
                    'base_risk_per_trade': 1.0,
                    'max_risk_per_trade': 2.0
                }
            }
        })
        
        # Performance metrics
        self.trades: List[Dict] = []
        self.equity_curve: List[float] = []
        self.current_balance = initial_balance
        self.current_position = 0
        self.position_size = 0
        self.entry_price = 0
        
    def fetch_historical_data(self) -> pd.DataFrame:
        """
        Fetch historical data from CoinGecko
        """
        try:
            logger.info(f"Fetching historical data for {self.trading_pair} from {self.start_date} to {self.end_date}")
            
            data = self.data_fetcher.get_historical_data(
                symbol=self.trading_pair,
                start_date=self.start_date,
                end_date=self.end_date,
                interval='daily'  # CoinGecko free tier only supports daily data
            )
            
            if data is None or data.empty:
                raise ValueError(f"No data found for {self.trading_pair}")
            
            logger.info(f"Successfully fetched {len(data)} records")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching historical data: {str(e)}")
            raise
    
    def run_backtest(self) -> Dict:
        """Run the backtest and return performance metrics"""
        try:
            # Fetch historical data
            data = self.fetch_historical_data()
            
            # Initialize tracking variables
            self.current_balance = self.initial_balance
            self.current_position = 0
            self.position_size = 0
            self.entry_price = 0
            self.trades = []
            self.equity_curve = [self.initial_balance]
            
            logger.info(f"Starting backtest with {len(data)} data points")
            
            # Run simulation
            for i in range(len(data)):
                current_data = data.iloc[:i+1]
                if len(current_data) < 20:  # Need enough data for indicators
                    continue
                
                current_price = float(current_data['close'].iloc[-1])
                current_time = current_data['timestamp'].iloc[-1]
                
                # Calculate indicators and signals
                current_data = self.strategy.calculate_indicators(current_data)
                signal = self.strategy.generate_signal(current_data)
                
                # Execute trades based on signals
                self._execute_trade(signal, current_price, current_time)
                
                # Update equity curve
                self._update_equity_curve(current_price)
                
                # Log progress
                if i % 10 == 0:  # Log every 10 days for daily data
                    logger.info(f"Progress: {i}/{len(data)} - Balance: ${self.current_balance:.2f}")
            
            # Calculate final metrics
            metrics = self._calculate_metrics()
            logger.info("Backtest completed successfully")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error running backtest: {str(e)}")
            raise
    
    def _execute_trade(self, signal: int, current_price: float, current_time) -> None:
        """Execute a trade based on the signal"""
        try:
            if signal == 1 and self.current_position <= 0:  # Buy signal
                # Close short position if exists
                if self.current_position < 0:
                    pnl = (self.entry_price - current_price) * abs(self.position_size)
                    self.current_balance += pnl
                    self.trades.append({
                        'time': current_time,
                        'type': 'close_short',
                        'price': current_price,
                        'size': abs(self.position_size),
                        'pnl': pnl
                    })
                
                # Open long position
                position_value = self.current_balance * 0.1  # Use 10% of balance
                self.position_size = position_value / current_price
                self.entry_price = current_price
                self.current_position = 1
                
                self.trades.append({
                    'time': current_time,
                    'type': 'buy',
                    'price': current_price,
                    'size': self.position_size,
                    'pnl': 0
                })
                
            elif signal == -1 and self.current_position >= 0:  # Sell signal
                # Close long position if exists
                if self.current_position > 0:
                    pnl = (current_price - self.entry_price) * self.position_size
                    self.current_balance += pnl
                    self.trades.append({
                        'time': current_time,
                        'type': 'close_long',
                        'price': current_price,
                        'size': self.position_size,
                        'pnl': pnl
                    })
                
                # Open short position
                position_value = self.current_balance * 0.1  # Use 10% of balance
                self.position_size = position_value / current_price
                self.entry_price = current_price
                self.current_position = -1
                
                self.trades.append({
                    'time': current_time,
                    'type': 'sell',
                    'price': current_price,
                    'size': self.position_size,
                    'pnl': 0
                })
                
        except Exception as e:
            logger.error(f"Error executing trade: {str(e)}")
    
    def _update_equity_curve(self, current_price: float) -> None:
        """Update the equity curve"""
        try:
            if self.current_position > 0:  # Long position
                unrealized_pnl = (current_price - self.entry_price) * self.position_size
                equity = self.current_balance + unrealized_pnl
            elif self.current_position < 0:  # Short position
                unrealized_pnl = (self.entry_price - current_price) * abs(self.position_size)
                equity = self.current_balance + unrealized_pnl
            else:  # No position
                equity = self.current_balance
            
            self.equity_curve.append(equity)
            
        except Exception as e:
            logger.error(f"Error updating equity curve: {str(e)}")
    
    def _calculate_metrics(self) -> Dict:
        """Calculate performance metrics"""
        try:
            if not self.equity_curve:
                return {}
            
            # Calculate returns
            equity_array = np.array(self.equity_curve)
            returns = np.diff(equity_array) / equity_array[:-1]
            
            # Basic metrics
            total_return = (equity_array[-1] - equity_array[0]) / equity_array[0] * 100
            total_trades = len([t for t in self.trades if t['type'] in ['close_long', 'close_short']])
            
            # Calculate win rate
            profitable_trades = len([t for t in self.trades if t['pnl'] > 0])
            win_rate = (profitable_trades / total_trades * 100) if total_trades > 0 else 0
            
            # Calculate Sharpe ratio
            if len(returns) > 0 and np.std(returns) > 0:
                sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252)
            else:
                sharpe_ratio = 0
            
            # Calculate max drawdown
            peak = equity_array[0]
            max_drawdown = 0
            for value in equity_array:
                if value > peak:
                    peak = value
                drawdown = (peak - value) / peak * 100
                max_drawdown = max(max_drawdown, drawdown)
            
            return {
                'total_return': total_return,
                'total_trades': total_trades,
                'win_rate': win_rate,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown,
                'final_balance': equity_array[-1],
                'initial_balance': equity_array[0]
            }
            
        except Exception as e:
            logger.error(f"Error calculating metrics: {str(e)}")
            return {}
    
    def plot_results(self, save_path: str = None):
        """Plot backtest results"""
        try:
            if not self.equity_curve:
                logger.warning("No equity curve data to plot")
                return
            
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
            
            # Plot equity curve
            ax1.plot(self.equity_curve, label='Portfolio Value', color='blue')
            ax1.set_title('CoinGecko Backtest Results - Equity Curve')
            ax1.set_xlabel('Time')
            ax1.set_ylabel('Portfolio Value ($)')
            ax1.legend()
            ax1.grid(True)
            
            # Plot trade points
            if self.trades:
                trade_times = [i for i, _ in enumerate(self.equity_curve) if i % 10 == 0]
                trade_values = [self.equity_curve[i] for i in trade_times]
                ax1.scatter(trade_times, trade_values, color='red', alpha=0.6, label='Trades')
            
            # Plot returns distribution
            if len(self.equity_curve) > 1:
                returns = np.diff(self.equity_curve) / self.equity_curve[:-1]
                ax2.hist(returns, bins=50, alpha=0.7, color='green')
                ax2.set_title('Returns Distribution')
                ax2.set_xlabel('Returns')
                ax2.set_ylabel('Frequency')
                ax2.grid(True)
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"Plot saved to {save_path}")
            
            plt.show()
            
        except Exception as e:
            logger.error(f"Error plotting results: {str(e)}")

def main():
    """Example usage"""
    # Set up backtest parameters
    start_date = "2024-01-01"
    end_date = "2024-02-01"
    initial_balance = 1000.0
    trading_pair = "ETHUSDT"
    
    # Create and run backtest
    backtest = CoinGeckoBacktestEngine(
        start_date=start_date,
        end_date=end_date,
        initial_balance=initial_balance,
        trading_pair=trading_pair
    )
    
    # Run backtest
    results = backtest.run_backtest()
    
    # Print results
    print("\n📊 CoinGecko Backtest Results:")
    print(f"Total Return: {results['total_return']:.2f}%")
    print(f"Total Trades: {results['total_trades']}")
    print(f"Win Rate: {results['win_rate']:.1f}%")
    print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
    print(f"Max Drawdown: {results['max_drawdown']:.2f}%")
    print(f"Final Balance: ${results['final_balance']:.2f}")
    
    # Plot results
    backtest.plot_results()

if __name__ == "__main__":
    main() 