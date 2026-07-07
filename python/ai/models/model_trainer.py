# Niskala - Model Trainer
# ML model training pipeline

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


@dataclass
class TrainingConfig:
    """Training configuration"""
    model_type: str
    epochs: int = 100
    batch_size: int = 32
    learning_rate: float = 0.001
    validation_split: float = 0.2
    early_stopping: bool = True
    patience: int = 10
    parameters: Dict = None


@dataclass
class TrainingResult:
    """Training result"""
    model_path: str
    metrics: Dict
    training_time: float
    config: Dict
    timestamp: str


class ModelTrainer:
    """ML model training pipeline"""
    
    def __init__(self):
        self.trainers = {
            'lstm': self._train_lstm,
            'transformer': self._train_transformer,
            'rl': self._train_rl,
            'classification': self._train_classification,
        }
        logger.info("ModelTrainer initialized")
    
    async def train(self, config: TrainingConfig, data: pd.DataFrame,
                    symbol: str = '') -> TrainingResult:
        """Train model based on config"""
        start_time = datetime.now()
        
        trainer = self.trainers.get(config.model_type)
        if not trainer:
            raise ValueError(f"Unknown model type: {config.model_type}")
        
        logger.info(f"Training {config.model_type} model for {symbol}")
        
        result = await trainer(config, data, symbol)
        
        training_time = (datetime.now() - start_time).total_seconds()
        result.training_time = training_time
        
        logger.info(f"Training complete in {training_time:.1f}s")
        return result
    
    async def _train_lstm(self, config: TrainingConfig, 
                          data: pd.DataFrame, symbol: str) -> TrainingResult:
        """Train LSTM model"""
        try:
            from ..advanced.lstm_predictor import LSTMPredictor
            
            predictor = LSTMPredictor(
                sequence_length=config.parameters.get('sequence_length', 60),
                prediction_horizon=config.parameters.get('prediction_horizon', 5)
            )
            
            history = predictor.train(data, epochs=config.epochs)
            
            model_path = f"data/models/lstm_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pt"
            predictor.save_model(model_path)
            
            return TrainingResult(
                model_path=model_path,
                metrics=history,
                training_time=0,
                config=asdict(config) if hasattr(config, '__dict__') else config.__dict__,
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            logger.error(f"LSTM training failed: {e}")
            raise
    
    async def _train_transformer(self, config: TrainingConfig,
                                 data: pd.DataFrame, symbol: str) -> TrainingResult:
        """Train Transformer model"""
        try:
            from ..advanced.transformer_forecaster import TransformerForecaster
            
            forecaster = TransformerForecaster(
                d_model=config.parameters.get('d_model', 128),
                nhead=config.parameters.get('nhead', 8),
                num_layers=config.parameters.get('num_layers', 4)
            )
            
            history = forecaster.train(data, epochs=config.epochs)
            
            model_path = f"data/models/transformer_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pt"
            forecaster.save_model(model_path)
            
            return TrainingResult(
                model_path=model_path,
                metrics=history,
                training_time=0,
                config=config.__dict__,
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            logger.error(f"Transformer training failed: {e}")
            raise
    
    async def _train_rl(self, config: TrainingConfig,
                        data: pd.DataFrame, symbol: str) -> TrainingResult:
        """Train RL agent"""
        try:
            from ..advanced.rl_agent import TradingAgent
            
            agent = TradingAgent(
                state_size=config.parameters.get('state_size', 10),
                action_size=config.parameters.get('action_size', 3)
            )
            
            history = agent.train(data.values, episodes=config.epochs)
            
            model_path = f"data/models/rl_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pt"
            agent.save(model_path)
            
            return TrainingResult(
                model_path=model_path,
                metrics=history,
                training_time=0,
                config=config.__dict__,
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            logger.error(f"RL training failed: {e}")
            raise
    
    async def _train_classification(self, config: TrainingConfig,
                                    data: pd.DataFrame, symbol: str) -> TrainingResult:
        """Train classification model"""
        try:
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import accuracy_score, f1_score
            
            # Prepare features
            features = ['open', 'high', 'low', 'close', 'volume']
            X = data[features].values
            y = (data['close'].shift(-5) > data['close']).astype(int).values
            
            X_train, X_test, y_train, y_test = train_test_split(
                X[:-5], y[:-5], test_size=config.validation_split
            )
            
            model = RandomForestClassifier(
                n_estimators=config.parameters.get('n_estimators', 100),
                random_state=42
            )
            
            model.fit(X_train, y_train)
            predictions = model.predict(X_test)
            
            metrics = {
                'accuracy': accuracy_score(y_test, predictions),
                'f1_score': f1_score(y_test, predictions)
            }
            
            return TrainingResult(
                model_path='sklearn_model',
                metrics=metrics,
                training_time=0,
                config=config.__dict__,
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            logger.error(f"Classification training failed: {e}")
            raise
    
    def evaluate(self, model_path: str, test_data: pd.DataFrame) -> Dict:
        """Evaluate model performance"""
        # Placeholder for evaluation logic
        return {
            'mse': 0.0,
            'mae': 0.0,
            'accuracy': 0.0,
            'sharpe': 0.0
        }


def asdict(obj):
    """Convert dataclass to dict"""
    if hasattr(obj, '__dict__'):
        return obj.__dict__
    return {}
