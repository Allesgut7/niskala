# Niskala - LSTM Price Predictor
# Time-series deep learning for stock price prediction

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

try:
    import torch
    import torch.nn as nn
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

try:
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import accuracy_score, f1_score
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False


@dataclass
class Prediction:
    """Price prediction result"""
    symbol: str
    direction: str  # 'up', 'down', 'neutral'
    confidence: float
    target_price: float
    stop_loss: float
    take_profit: float
    prediction_horizon: int  # days
    timestamp: str


if HAS_TORCH:
    class LSTMModel(nn.Module):
        """LSTM model with attention mechanism"""
        
        def __init__(self, input_size: int, hidden_size: int = 128, 
                     num_layers: int = 2, dropout: float = 0.2):
            super().__init__()
            self.hidden_size = hidden_size
            self.num_layers = num_layers
            
            self.lstm = nn.LSTM(
                input_size=input_size,
                hidden_size=hidden_size,
                num_layers=num_layers,
                dropout=dropout,
                batch_first=True
            )
            
            self.attention = nn.MultiheadAttention(
                embed_dim=hidden_size,
                num_heads=4,
                dropout=dropout,
                batch_first=True
            )
            
            self.fc = nn.Sequential(
                nn.Linear(hidden_size, 64),
                nn.ReLU(),
                nn.Dropout(dropout),
                nn.Linear(64, 32),
                nn.ReLU(),
                nn.Linear(32, 3)  # direction, magnitude, confidence
            )
        
        def forward(self, x):
            # LSTM
            lstm_out, _ = self.lstm(x)
            
            # Attention
            attn_out, _ = self.attention(lstm_out, lstm_out, lstm_out)
            
            # Take last time step
            out = attn_out[:, -1, :]
            
            # Fully connected
            return self.fc(out)


class LSTMPredictor:
    """LSTM-based stock price predictor"""
    
    def __init__(self, sequence_length: int = 60, prediction_horizon: int = 5):
        self.sequence_length = sequence_length
        self.prediction_horizon = prediction_horizon
        self.model = None
        self.scaler = StandardScaler() if HAS_SKLEARN else None
        self.feature_columns = [
            'open', 'high', 'low', 'close', 'volume',
            'sma_20', 'sma_50', 'rsi', 'macd', 'bb_upper', 'bb_lower',
            'atr', 'obv', 'ema_12', 'ema_26'
        ]
        logger.info(f"LSTMPredictor initialized (seq={sequence_length}, horizon={prediction_horizon})")
    
    def _build_model(self) -> Optional['nn.Module']:
        """Build LSTM model"""
        if not HAS_TORCH:
            logger.warning("PyTorch not installed")
            return None
        
        return LSTMModel(
            input_size=len(self.feature_columns),
            hidden_size=128,
            num_layers=2,
            dropout=0.2
        )
    
    def prepare_features(self, df: pd.DataFrame) -> np.ndarray:
        """Prepare features from OHLCV data"""
        features = df.copy()
        
        # Moving averages
        features['sma_20'] = features['close'].rolling(20).mean()
        features['sma_50'] = features['close'].rolling(50).mean()
        features['ema_12'] = features['close'].ewm(span=12).mean()
        features['ema_26'] = features['close'].ewm(span=26).mean()
        
        # RSI
        delta = features['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        features['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        features['macd'] = features['ema_12'] - features['ema_26']
        
        # Bollinger Bands
        features['bb_upper'] = features['sma_20'] + 2 * features['close'].rolling(20).std()
        features['bb_lower'] = features['sma_20'] - 2 * features['close'].rolling(20).std()
        
        # ATR
        high_low = features['high'] - features['low']
        high_close = np.abs(features['high'] - features['close'].shift())
        low_close = np.abs(features['low'] - features['close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        features['atr'] = tr.rolling(14).mean()
        
        # OBV
        obv = [0]
        for i in range(1, len(features)):
            if features['close'].iloc[i] > features['close'].iloc[i-1]:
                obv.append(obv[-1] + features['volume'].iloc[i])
            elif features['close'].iloc[i] < features['close'].iloc[i-1]:
                obv.append(obv[-1] - features['volume'].iloc[i])
            else:
                obv.append(obv[-1])
        features['obv'] = obv
        
        # Drop NaN
        features = features.dropna()
        
        return features[self.feature_columns].values
    
    def create_sequences(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Create sequences for LSTM"""
        X, y = [], []
        
        for i in range(len(data) - self.sequence_length - self.prediction_horizon):
            X.append(data[i:i + self.sequence_length])
            # Target: price direction
            future_return = (data[i + self.sequence_length + self.prediction_horizon - 1, 3] - 
                           data[i + self.sequence_length - 1, 3]) / data[i + self.sequence_length - 1, 3]
            y.append(1 if future_return > 0 else 0)
        
        return np.array(X), np.array(y)
    
    def train(self, df: pd.DataFrame, epochs: int = 100, 
              validation_split: float = 0.2) -> Dict:
        """Train LSTM model"""
        if not HAS_TORCH or not HAS_SKLEARN:
            return {"error": "PyTorch and scikit-learn required"}
        
        # Prepare data
        data = self.prepare_features(df)
        data_scaled = self.scaler.fit_transform(data)
        X, y = self.create_sequences(data_scaled)
        
        if len(X) == 0:
            return {"error": "Not enough data for training"}
        
        # Split data
        split_idx = int(len(X) * (1 - validation_split))
        X_train, X_val = X[:split_idx], X[split_idx:]
        y_train, y_val = y[:split_idx], y[split_idx:]
        
        # Convert to tensors
        X_train = torch.FloatTensor(X_train)
        y_train = torch.FloatTensor(y_train)
        X_val = torch.FloatTensor(X_val)
        y_val = torch.FloatTensor(y_val)
        
        # Build model
        self.model = self._build_model()
        criterion = nn.BCEWithLogitsLoss()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001)
        
        # Training loop
        train_losses = []
        val_losses = []
        val_accuracies = []
        
        for epoch in range(epochs):
            self.model.train()
            optimizer.zero_grad()
            output = self.model(X_train).squeeze()
            loss = criterion(output, y_train)
            loss.backward()
            optimizer.step()
            train_losses.append(loss.item())
            
            # Validation
            self.model.eval()
            with torch.no_grad():
                val_output = self.model(X_val).squeeze()
                val_loss = criterion(val_output, y_val)
                val_losses.append(val_loss.item())
                
                val_pred = (torch.sigmoid(val_output) > 0.5).float()
                val_acc = accuracy_score(y_val.numpy(), val_pred.numpy())
                val_accuracies.append(val_acc)
            
            if (epoch + 1) % 10 == 0:
                logger.info(f"Epoch {epoch+1}/{epochs} - Train Loss: {loss.item():.4f}, Val Loss: {val_loss.item():.4f}, Val Acc: {val_acc:.4f}")
        
        return {
            "train_losses": train_losses,
            "val_losses": val_losses,
            "val_accuracies": val_accuracies,
            "final_accuracy": val_accuracies[-1] if val_accuracies else 0,
            "epochs": epochs
        }
    
    def predict(self, df: pd.DataFrame) -> Optional[Prediction]:
        """Make prediction"""
        if not HAS_TORCH or self.model is None:
            return None
        
        # Prepare data
        data = self.prepare_features(df)
        if len(data) < self.sequence_length:
            return None
        
        data_scaled = self.scaler.transform(data)
        sequence = data_scaled[-self.sequence_length:]
        sequence = torch.FloatTensor(sequence).unsqueeze(0)
        
        # Predict
        self.model.eval()
        with torch.no_grad():
            output = self.model(sequence)
            probs = torch.sigmoid(output).numpy()[0]
        
        direction = 'up' if probs[0] > 0.5 else 'down'
        confidence = abs(probs[0] - 0.5) * 2
        
        # Calculate target prices
        current_price = df['close'].iloc[-1]
        atr = df['high'].sub(df['low']).rolling(14).mean().iloc[-1]
        
        if direction == 'up':
            target_price = current_price + (atr * 2)
            stop_loss = current_price - atr
            take_profit = current_price + (atr * 3)
        else:
            target_price = current_price - (atr * 2)
            stop_loss = current_price + atr
            take_profit = current_price - (atr * 3)
        
        return Prediction(
            symbol='',
            direction=direction,
            confidence=float(confidence),
            target_price=float(target_price),
            stop_loss=float(stop_loss),
            take_profit=float(take_profit),
            prediction_horizon=self.prediction_horizon,
            timestamp=pd.Timestamp.now().isoformat()
        )
    
    def save_model(self, path: str):
        """Save model to file"""
        if self.model and HAS_TORCH:
            torch.save({
                'model_state': self.model.state_dict(),
                'scaler': self.scaler,
                'sequence_length': self.sequence_length,
                'prediction_horizon': self.prediction_horizon,
            }, path)
            logger.info(f"Model saved to {path}")
    
    def load_model(self, path: str):
        """Load model from file"""
        if not HAS_TORCH:
            return
        
        checkpoint = torch.load(path)
        self.sequence_length = checkpoint['sequence_length']
        self.prediction_horizon = checkpoint['prediction_horizon']
        self.scaler = checkpoint['scaler']
        self.model = self._build_model()
        self.model.load_state_dict(checkpoint['model_state'])
        logger.info(f"Model loaded from {path}")
