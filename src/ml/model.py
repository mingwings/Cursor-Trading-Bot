import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import logging
from datetime import datetime, timedelta
import ta

class MLModel:
    def __init__(self, config: Dict):
        """
        Initialize the ML model with configuration parameters.
        
        Args:
            config: Dictionary containing ML model parameters
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        self.window_size = config['ml']['window_size']
        self.feature_columns = [
            'returns', 'log_returns', 'volatility', 'volume_ma', 'price_ma',
            'rsi', 'macd', 'macd_signal', 'bb_upper', 'bb_lower',
            'volume', 'close'
        ]
        self.target_column = config['ml']['target_column']
        self.min_samples = config['ml']['min_samples_for_training']
        
        self.model = DecisionTreeClassifier(
            max_depth=5,
            min_samples_split=50,
            min_samples_leaf=25,
            random_state=42
        )
        
        self.scaler = StandardScaler()
        self.last_training_time = None
        self.is_trained = False

    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare features for the ML model.
        
        Args:
            df: DataFrame with price data and indicators
            
        Returns:
            DataFrame with prepared features
        """
        try:
            # Create future returns as target
            df[self.target_column] = df['close'].pct_change(periods=5).shift(-5)
            
            # Create binary target (1 if price goes up, 0 if down)
            df[self.target_column] = (df[self.target_column] > 0).astype(int)
            
            # Calculate technical indicators
            df['returns'] = df['close'].pct_change()
            df['log_returns'] = np.log(df['close']).diff()
            df['volatility'] = df['returns'].rolling(window=20).std()
            df['volume_ma'] = df['volume'].rolling(window=20).mean()
            df['price_ma'] = df['close'].rolling(window=20).mean()
            df['rsi'] = ta.momentum.RSIIndicator(close=df['close']).rsi()
            df['macd'] = ta.trend.MACD(close=df['close']).macd()
            df['macd_signal'] = ta.trend.MACD(close=df['close']).macd_signal()
            df['bb_upper'] = ta.volatility.BollingerBands(close=df['close']).bollinger_hband()
            df['bb_lower'] = ta.volatility.BollingerBands(close=df['close']).bollinger_lband()
            
            # Select features
            features = df[self.feature_columns].copy()
            
            # Handle missing values
            features = features.fillna(method='ffill').fillna(0)
            
            return features
            
        except Exception as e:
            self.logger.error(f"Error preparing features: {str(e)}")
            raise

    def prepare_target(self, df: pd.DataFrame) -> pd.Series:
        """
        Prepare target variable for the ML model.
        
        Args:
            df: DataFrame with price data and indicators
            
        Returns:
            Series containing target variable
        """
        try:
            return df[self.target_column].dropna()
            
        except Exception as e:
            self.logger.error(f"Error preparing target: {str(e)}")
            raise

    def should_retrain(self) -> bool:
        """
        Check if the model should be retrained based on time interval.
        
        Returns:
            Boolean indicating if retraining is needed
        """
        if self.last_training_time is None:
            return True
            
        hours_since_training = (
            datetime.now() - self.last_training_time
        ).total_seconds() / 3600
        
        return hours_since_training >= self.config['ml']['retrain_interval']

    def train(self, df: pd.DataFrame) -> None:
        """
        Train the ML model on the given data.
        
        Args:
            df: DataFrame with price data and indicators
        """
        try:
            if len(df) < self.min_samples:
                self.logger.warning(
                    f"Not enough samples for training. Need {self.min_samples}, got {len(df)}"
                )
                return
                
            # Prepare features and target
            features = self.prepare_features(df)
            target = self.prepare_target(df)
            
            # Align features and target
            features = features.iloc[:-5]  # Remove last 5 rows as they don't have target
            target = target.iloc[:-5]
            
            # Scale features
            features_scaled = self.scaler.fit_transform(features)
            
            # Train model
            self.model.fit(features_scaled, target)
            
            self.last_training_time = datetime.now()
            self.is_trained = True
            
            # Log model performance
            train_predictions = self.model.predict(features_scaled)
            train_accuracy = (train_predictions == target).mean()
            self.logger.info(f"Model training completed. Training accuracy: {train_accuracy:.2%}")
            
        except Exception as e:
            self.logger.error(f"Error training model: {str(e)}")
            raise

    def predict(self, df: pd.DataFrame) -> Tuple[float, float]:
        """
        Make predictions using the trained model.
        
        Args:
            df: DataFrame with price data and indicators
            
        Returns:
            Tuple of (prediction, probability)
            prediction: -1 for sell, 0 for hold, 1 for buy
            probability: confidence score between 0 and 1
        """
        try:
            if not self.is_trained:
                self.logger.warning("Model not trained yet")
                return 0.0, 0.0
                
            # Prepare features
            features = self.prepare_features(df)
            
            # Get latest data point
            latest_features = features.iloc[-1:].copy()
            
            # Scale features
            latest_features_scaled = self.scaler.transform(latest_features)
            
            # Make prediction
            prediction = self.model.predict(latest_features_scaled)[0]
            probabilities = self.model.predict_proba(latest_features_scaled)[0]
            
            # Convert binary prediction to trading signal
            if prediction == 1 and probabilities[1] > 0.6:  # Strong buy signal
                return 1.0, probabilities[1]
            elif prediction == 0 and probabilities[0] > 0.6:  # Strong sell signal
                return -1.0, probabilities[0]
            else:  # Weak or uncertain signal
                return 0.0, max(probabilities)
            
        except Exception as e:
            self.logger.error(f"Error making prediction: {str(e)}")
            return 0.0, 0.0

    def save_model(self, path: str) -> None:
        """
        Save the trained model to disk.
        
        Args:
            path: Path to save the model
        """
        try:
            if not self.is_trained:
                self.logger.warning("No trained model to save")
                return
                
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'last_training_time': self.last_training_time
            }
            joblib.dump(model_data, path)
            self.logger.info(f"Model saved to {path}")
            
        except Exception as e:
            self.logger.error(f"Error saving model: {str(e)}")
            raise

    def load_model(self, path: str) -> None:
        """
        Load a trained model from disk.
        
        Args:
            path: Path to load the model from
        """
        try:
            model_data = joblib.load(path)
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.last_training_time = model_data['last_training_time']
            self.is_trained = True
            self.logger.info(f"Model loaded from {path}")
            
        except Exception as e:
            self.logger.error(f"Error loading model: {str(e)}")
            raise 