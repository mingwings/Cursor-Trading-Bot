import pandas as pd
from typing import Dict, Optional
import logging
from datetime import datetime, timedelta

class RiskManager:
    def __init__(self, config: Dict):
        """
        Initialize the risk manager with configuration parameters.
        
        Args:
            config: Dictionary containing risk management parameters
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Risk parameters
        self.max_daily_trades = config['risk']['max_daily_trades']
        self.max_daily_loss = config['risk']['max_daily_loss_percentage']
        self.base_risk = config['risk']['position_sizing']['base_risk_per_trade']
        self.max_risk = config['risk']['position_sizing']['max_risk_per_trade']
        
        # Trading state
        self.daily_trades = 0
        self.daily_pnl = 0.0
        self.last_reset = datetime.now()
        self.open_positions = {}

    def reset_daily_metrics(self) -> None:
        """Reset daily trading metrics."""
        self.daily_trades = 0
        self.daily_pnl = 0.0
        self.last_reset = datetime.now()
        self.logger.info("Daily metrics reset")

    def update_daily_metrics(self) -> None:
        """Update daily metrics and reset if necessary."""
        if datetime.now().date() > self.last_reset.date():
            self.reset_daily_metrics()

    def calculate_position_size(
        self,
        account_balance: float,
        current_price: float,
        confidence: float
    ) -> float:
        """
        Calculate the position size based on account balance and risk parameters.
        
        Args:
            account_balance: Current account balance
            current_price: Current price of the asset
            confidence: Trade confidence score (0-1)
            
        Returns:
            Position size in base currency
        """
        try:
            # Update daily metrics
            self.update_daily_metrics()
            
            # Check daily trade limit
            if self.daily_trades >= self.max_daily_trades:
                self.logger.warning("Daily trade limit reached")
                return 0.0
                
            # Calculate risk-adjusted position size
            risk_percentage = self.base_risk + (
                (self.max_risk - self.base_risk) * confidence
            )
            
            position_size = account_balance * (risk_percentage / 100)
            
            # Ensure position size doesn't exceed account balance
            position_size = min(position_size, account_balance)
            
            return position_size
            
        except Exception as e:
            self.logger.error(f"Error calculating position size: {str(e)}")
            raise

    def can_open_position(
        self,
        symbol: str,
        account_balance: float,
        current_price: float
    ) -> bool:
        """
        Check if a new position can be opened.
        
        Args:
            symbol: Trading pair symbol
            account_balance: Current account balance
            current_price: Current price of the asset
            
        Returns:
            Boolean indicating if position can be opened
        """
        try:
            # Update daily metrics
            self.update_daily_metrics()
            
            # Check if symbol already has an open position
            if symbol in self.open_positions:
                self.logger.warning(f"Position already open for {symbol}")
                return False
                
            # Check daily trade limit
            if self.daily_trades >= self.max_daily_trades:
                self.logger.warning("Daily trade limit reached")
                return False
                
            # Check daily loss limit
            if self.daily_pnl <= -self.max_daily_loss * account_balance / 100:
                self.logger.warning("Daily loss limit reached")
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking position opening: {str(e)}")
            raise

    def update_position(
        self,
        symbol: str,
        entry_price: float,
        current_price: float,
        position_size: float
    ) -> None:
        """
        Update position information.
        
        Args:
            symbol: Trading pair symbol
            entry_price: Position entry price
            current_price: Current price
            position_size: Position size in base currency
        """
        try:
            self.open_positions[symbol] = {
                'entry_price': entry_price,
                'current_price': current_price,
                'position_size': position_size,
                'entry_time': datetime.now()
            }
            
            self.daily_trades += 1
            
        except Exception as e:
            self.logger.error(f"Error updating position: {str(e)}")
            raise

    def close_position(
        self,
        symbol: str,
        exit_price: float
    ) -> Optional[float]:
        """
        Close a position and calculate P&L.
        
        Args:
            symbol: Trading pair symbol
            exit_price: Position exit price
            
        Returns:
            P&L in base currency
        """
        try:
            if symbol not in self.open_positions:
                self.logger.warning(f"No open position for {symbol}")
                return None
                
            position = self.open_positions[symbol]
            
            # Calculate P&L
            pnl = position['position_size'] * (
                (exit_price - position['entry_price']) / position['entry_price']
            )
            
            # Update daily P&L
            self.daily_pnl += pnl
            
            # Remove position
            del self.open_positions[symbol]
            
            return pnl
            
        except Exception as e:
            self.logger.error(f"Error closing position: {str(e)}")
            raise

    def get_position_info(self, symbol: str) -> Optional[Dict]:
        """
        Get information about an open position.
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            Dictionary containing position information
        """
        return self.open_positions.get(symbol)

    def get_daily_metrics(self) -> Dict:
        """
        Get current daily trading metrics.
        
        Returns:
            Dictionary containing daily metrics
        """
        return {
            'trades': self.daily_trades,
            'pnl': self.daily_pnl,
            'open_positions': len(self.open_positions)
        } 