# Niskala - Transformer Forecaster
# Attention-based model for multi-step price prediction

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

try:
    import torch
    import torch.nn as nn
    import math
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False


if HAS_TORCH:
    class PositionalEncoding(nn.Module):
        """Positional encoding for transformer"""
        
        def __init__(self, d_model: int, max_len: int = 5000):
            super().__init__()
            pe = torch.zeros(max_len, d_model)
            position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
            div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
            pe[:, 0::2] = torch.sin(position * div_term)
            pe[:, 1::2] = torch.cos(position * div_term)
            pe = pe.unsqueeze(0)
            self.register_buffer('pe', pe)
        
        def forward(self, x):
            return x + self.pe[:, :x.size(1)]


    class TransformerModel(nn.Module):
        """Transformer encoder for time series"""
        
        def __init__(self, input_size: int, d_model: int = 128, 
                     nhead: int = 8, num_layers: int = 4, 
                     dropout: float = 0.1, output_size: int = 3):
            super().__init__()
            self.d_model = d_model
            
            self.input_projection = nn.Linear(input_size, d_model)
            self.pos_encoder = PositionalEncoding(d_model)
            
            encoder_layer = nn.TransformerEncoderLayer(
                d_model=d_model,
                nhead=nhead,
                dim_feedforward=d_model * 4,
                dropout=dropout,
                batch_first=True
            )
            self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
            
            self.fc = nn.Sequential(
                nn.Linear(d_model, 64),
                nn.ReLU(),
                nn.Dropout(dropout),
                nn.Linear(64, output_size)
            )
        
        def forward(self, x):
            x = self.input_projection(x)
            x = self.pos_encoder(x)
            x = self.transformer(x)
            x = x[:, -1, :]
            return self.fc(x)


class TransformerForecaster:
    """Transformer-based stock price forecaster"""
    
    def __init__(self, d_model: int = 128, nhead: int = 8, 
                 num_layers: int = 4, sequence_length: int = 60):
        self.d_model = d_model
        self.nhead = nhead
        self.num_layers = num_layers
        self.sequence_length = sequence_length
        self.model = None
        self.feature_columns = [
            'open', 'high', 'low', 'close', 'volume',
            'sma_20', 'sma_50', 'rsi', 'macd', 'atr'
        ]
        logger.info(f"TransformerForecaster initialized (d={d_model}, heads={nhead}, layers={num_layers})")
    
    def _build_model(self, input_size: int) -> Optional['nn.Module']:
        """Build transformer model"""
        if not HAS_TORCH:
            return None
        
        return TransformerModel(
            input_size=input_size,
            d_model=self.d_model,
            nhead=self.nhead,
            num_layers=self.num_layers,
            output_size=3  # direction, magnitude, confidence
        )
    
    def prepare_features(self, df: pd.DataFrame) -> np.ndarray:
        """Prepare features"""
        features = df.copy()
        features['sma_20'] = features['close'].rolling(20).mean()
        features['sma_50'] = features['close'].rolling(50).mean()
        
        delta = features['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        features['rsi'] = 100 - (100 / (1 + rs))
        
        features['macd'] = features['close'].ewm(span=12).mean() - features['close'].ewm(span=26).mean()
        
        high_low = features['high'] - features['low']
        high_close = np.abs(features['high'] - features['close'].shift())
        low_close = np.abs(features['low'] - features['close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        features['atr'] = tr.rolling(14).mean()
        
        features = features.dropna()
        return features[self.feature_columns].values
    
    def train(self, df: pd.DataFrame, epochs: int = 100) -> Dict:
        """Train transformer model"""
        if not HAS_TORCH:
            return {"error": "PyTorch required"}
        
        from sklearn.preprocessing import StandardScaler
        
        data = self.prepare_features(df)
        scaler = StandardScaler()
        data_scaled = scaler.fit_transform(data)
        
        X, y = [], []
        for i in range(len(data_scaled) - self.sequence_length - 5):
            X.append(data_scaled[i:i + self.sequence_length])
            future_return = (data_scaled[i + self.sequence_length + 4, 3] - 
                           data_scaled[i + self.sequence_length - 1, 3])
            y.append([1 if future_return > 0 else 0, abs(future_return), 0.5])
        
        if len(X) == 0:
            return {"error": "Not enough data"}
        
        X = torch.FloatTensor(np.array(X))
        y = torch.FloatTensor(np.array(y))
        
        split = int(len(X) * 0.8)
        X_train, X_val = X[:split], X[split:]
        y_train, y_val = y[:split], y[split:]
        
        self.model = self._build_model(len(self.feature_columns))
        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001)
        
        history = {'train_loss': [], 'val_loss': []}
        
        for epoch in range(epochs):
            self.model.train()
            optimizer.zero_grad()
            output = self.model(X_train)
            loss = criterion(output, y_train)
            loss.backward()
            optimizer.step()
            history['train_loss'].append(loss.item())
            
            self.model.eval()
            with torch.no_grad():
                val_output = self.model(X_val)
                val_loss = criterion(val_output, y_val)
                history['val_loss'].append(val_loss.item())
        
        return history
    
    def predict(self, df: pd.DataFrame) -> Optional[Dict]:
        """Make prediction"""
        if not HAS_TORCH or self.model is None:
            return None
        
        from sklearn.preprocessing import StandardScaler
        
        data = self.prepare_features(df)
        if len(data) < self.sequence_length:
            return None
        
        scaler = StandardScaler()
        data_scaled = scaler.fit_transform(data)
        sequence = torch.FloatTensor(data_scaled[-self.sequence_length:]).unsqueeze(0)
        
        self.model.eval()
        with torch.no_grad():
            output = self.model(sequence).numpy()[0]
        
        return {
            'direction': 'up' if output[0] > 0.5 else 'down',
            'magnitude': float(abs(output[1])),
            'confidence': float(abs(output[0] - 0.5) * 2),
            'timestamp': pd.Timestamp.now().isoformat()
        }
    
    def save_model(self, path: str):
        """Save model"""
        if self.model and HAS_TORCH:
            torch.save(self.model.state_dict(), path)
    
    def load_model(self, path: str, input_size: int):
        """Load model"""
        if HAS_TORCH:
            self.model = self._build_model(input_size)
            self.model.load_state_dict(torch.load(path))
