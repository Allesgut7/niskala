# Niskala - Anomaly Detector
# Detection of unusual price/volume patterns

import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

try:
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False


@dataclass
class Anomaly:
    """Detected anomaly"""
    symbol: str
    anomaly_type: str
    severity: str  # low, medium, high, critical
    confidence: float
    description: str
    timestamp: str
    metrics: Dict


class AnomalyDetector:
    """ML-based anomaly detection for stocks"""
    
    def __init__(self):
        self.isolation_forest = None
        self.scaler = StandardScaler() if HAS_SKLEARN else None
        self.threshold = 0.1
        logger.info("AnomalyDetector initialized")
    
    def _extract_features(self, df: pd.DataFrame) -> np.ndarray:
        """Extract features for anomaly detection"""
        features = pd.DataFrame()
        
        # Returns
        features['return'] = df['close'].pct_change()
        
        # Volatility
        features['volatility'] = df['close'].rolling(20).std() / df['close'].rolling(20).mean()
        
        # Volume ratio
        features['volume_ratio'] = df['volume'] / df['volume'].rolling(20).mean()
        
        # Price range
        features['range'] = (df['high'] - df['low']) / df['close']
        
        # Gap
        features['gap'] = df['open'] / df['close'].shift(1) - 1
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        features['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD divergence
        ema12 = df['close'].ewm(span=12).mean()
        ema26 = df['close'].ewm(span=26).mean()
        macd = ema12 - ema26
        features['macd_divergence'] = macd / df['close']
        
        return features.dropna().values
    
    def fit(self, df: pd.DataFrame):
        """Fit anomaly detector on historical data"""
        if not HAS_SKLEARN:
            logger.warning("scikit-learn not installed")
            return
        
        features = self._extract_features(df)
        features_scaled = self.scaler.fit_transform(features)
        
        self.isolation_forest = IsolationForest(
            n_estimators=100,
            contamination=0.1,
            random_state=42
        )
        self.isolation_forest.fit(features_scaled)
        logger.info("Anomaly detector fitted")
    
    def detect(self, df: pd.DataFrame, symbol: str = '') -> List[Anomaly]:
        """Detect anomalies in data"""
        if not HAS_SKLEARN or self.isolation_forest is None:
            return []
        
        features = self._extract_features(df)
        if len(features) == 0:
            return []
        
        features_scaled = self.scaler.transform(features)
        scores = self.isolation_forest.decision_function(features_scaled)
        predictions = self.isolation_forest.predict(features_scaled)
        
        anomalies = []
        
        for i, (score, pred) in enumerate(zip(scores, predictions)):
            if pred == -1:  # Anomaly
                severity = self._get_severity(score)
                anomaly_type = self._classify_anomaly(df, i)
                
                anomaly = Anomaly(
                    symbol=symbol,
                    anomaly_type=anomaly_type,
                    severity=severity,
                    confidence=float(abs(score)),
                    description=self._generate_description(anomaly_type, df, i),
                    timestamp=df.index[i].isoformat() if hasattr(df.index[i], 'isoformat') else str(df.index[i]),
                    metrics={
                        'score': float(score),
                        'return': float(df['close'].pct_change().iloc[i]),
                        'volume_ratio': float(df['volume'].iloc[i] / df['volume'].rolling(20).mean().iloc[i]),
                    }
                )
                anomalies.append(anomaly)
        
        return anomalies
    
    def _get_severity(self, score: float) -> str:
        """Get anomaly severity"""
        abs_score = abs(score)
        if abs_score > 0.5:
            return 'critical'
        elif abs_score > 0.3:
            return 'high'
        elif abs_score > 0.15:
            return 'medium'
        return 'low'
    
    def _classify_anomaly(self, df: pd.DataFrame, idx: int) -> str:
        """Classify anomaly type"""
        row = df.iloc[idx]
        
        # Check volume spike
        vol_ratio = row['volume'] / df['volume'].rolling(20).mean().iloc[idx]
        if vol_ratio > 3:
            return 'volume_spike'
        
        # Check price gap
        if idx > 0:
            gap = abs(row['open'] / df['close'].iloc[idx-1] - 1)
            if gap > 0.05:
                return 'price_gap'
        
        # Check extreme return
        ret = abs(row['close'] / df['close'].iloc[idx-1] - 1) if idx > 0 else 0
        if ret > 0.05:
            return 'extreme_return'
        
        # Check unusual range
        range_pct = (row['high'] - row['low']) / row['close']
        if range_pct > 0.05:
            return 'high_volatility'
        
        return 'pattern_anomaly'
    
    def _generate_description(self, anomaly_type: str, df: pd.DataFrame, idx: int) -> str:
        """Generate human-readable description"""
        row = df.iloc[idx]
        
        descriptions = {
            'volume_spike': f"Unusual volume: {row['volume']:,.0f} ({row['volume']/df['volume'].rolling(20).mean().iloc[idx]:.1f}x average)",
            'price_gap': f"Price gap: {row['open']:,.0f} from previous close",
            'extreme_return': f"Extreme price movement: {row['close']/df['close'].iloc[idx-1]-1:+.2%}" if idx > 0 else "Extreme price movement",
            'high_volatility': f"High volatility: {(row['high']-row['low'])/row['close']:.2%} range",
            'pattern_anomaly': "Unusual pattern detected"
        }
        
        return descriptions.get(anomaly_type, "Anomaly detected")
    
    def real_time_check(self, symbol: str, current_data: Dict, 
                       historical_df: pd.DataFrame) -> Optional[Anomaly]:
        """Check real-time data for anomalies"""
        if len(historical_df) < 20:
            return None
        
        # Create temporary dataframe with new data
        new_row = pd.DataFrame([current_data])
        temp_df = pd.concat([historical_df, new_row], ignore_index=True)
        
        # Detect anomalies on last row
        anomalies = self.detect(temp_df, symbol)
        
        # Return only the latest anomaly
        if anomalies and anomalies[-1].timestamp == new_row.index[0].isoformat():
            return anomalies[-1]
        
        return None
