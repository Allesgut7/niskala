# Niskala - Factor Analysis
# Version: 1.0.0
# Multi-factor analysis: Value, Momentum, Quality, Size

from typing import Dict, List, Optional
from dataclasses import dataclass
import pandas as pd
import numpy as np
import logging


@dataclass
class FactorScore:
    """Factor score for a stock"""
    symbol: str
    value_score: float = 0.0
    momentum_score: float = 0.0
    quality_score: float = 0.0
    size_score: float = 0.0
    composite_score: float = 0.0
    rank: int = 0


class FactorAnalyzer:
    """Multi-factor analysis for stock screening"""
    
    # Factor weights
    DEFAULT_WEIGHTS = {
        'value': 0.3,
        'momentum': 0.3,
        'quality': 0.25,
        'size': 0.15
    }
    
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """Initialize factor analyzer
        
        Args:
            weights: Custom factor weights (value, momentum, quality, size)
        """
        self.weights = weights or self.DEFAULT_WEIGHTS
        
        # Validate weights sum to 1.0
        total = sum(self.weights.values())
        if not np.isclose(total, 1.0):
            logging.warning(f"Weights sum to {total}, normalizing...")
            for k in self.weights:
                self.weights[k] /= total
        
        logging.info(f"Factor analyzer initialized with weights: {self.weights}")
    
    def analyze(self, stocks_data: pd.DataFrame) -> List[FactorScore]:
        """Analyze stocks using multi-factor model
        
        Args:
            stocks_data: DataFrame with columns:
                - symbol: Stock ticker
                - price: Current price
                - pe_ratio: Price/Earnings
                - pb_ratio: Price/Book
                - dividend_yield: Dividend yield %
                - return_1m: 1-month return %
                - return_3m: 3-month return %
                - return_6m: 6-month return %
                - return_12m: 12-month return %
                - roe: Return on Equity %
                - roa: Return on Assets %
                - debt_equity: Debt/Equity ratio
                - current_ratio: Current ratio
                - market_cap: Market cap (IDR)
                
        Returns:
            List of FactorScore objects, sorted by composite score
        """
        if stocks_data.empty:
            return []
        
        logging.info(f"Analyzing {len(stocks_data)} stocks with multi-factor model")
        
        # Calculate individual factor scores
        stocks_data['value_score'] = self._calculate_value_score(stocks_data)
        stocks_data['momentum_score'] = self._calculate_momentum_score(stocks_data)
        stocks_data['quality_score'] = self._calculate_quality_score(stocks_data)
        stocks_data['size_score'] = self._calculate_size_score(stocks_data)
        
        # Calculate composite score
        stocks_data['composite_score'] = (
            stocks_data['value_score'] * self.weights['value'] +
            stocks_data['momentum_score'] * self.weights['momentum'] +
            stocks_data['quality_score'] * self.weights['quality'] +
            stocks_data['size_score'] * self.weights['size']
        )
        
        # Rank stocks
        stocks_data['rank'] = stocks_data['composite_score'].rank(ascending=False, method='dense')
        
        # Convert to FactorScore objects
        scores = []
        for _, row in stocks_data.iterrows():
            scores.append(FactorScore(
                symbol=row['symbol'],
                value_score=row['value_score'],
                momentum_score=row['momentum_score'],
                quality_score=row['quality_score'],
                size_score=row['size_score'],
                composite_score=row['composite_score'],
                rank=int(row['rank'])
            ))
        
        # Sort by rank
        scores.sort(key=lambda x: x.rank)
        
        return scores
    
    def _calculate_value_score(self, df: pd.DataFrame) -> pd.Series:
        """Calculate Value factor score
        
        Metrics:
        - PE Ratio (lower is better)
        - PB Ratio (lower is better)
        - Dividend Yield (higher is better)
        """
        # Normalize each metric to 0-100 scale
        pe_score = self._normalize_inverse(df['pe_ratio'])
        pb_score = self._normalize_inverse(df['pb_ratio'])
        div_score = self._normalize_direct(df['dividend_yield'])
        
        # Average
        value_score = (pe_score + pb_score + div_score) / 3
        
        return value_score
    
    def _calculate_momentum_score(self, df: pd.DataFrame) -> pd.Series:
        """Calculate Momentum factor score
        
        Metrics:
        - 1M return
        - 3M return
        - 6M return
        - 12M return (skipping recent month to avoid reversal)
        """
        # Weight recent performance more
        momentum_score = (
            df['return_1m'] * 0.4 +
            df['return_3m'] * 0.3 +
            df['return_6m'] * 0.2 +
            df['return_12m'] * 0.1
        )
        
        # Normalize to 0-100
        momentum_score = self._normalize_direct(momentum_score)
        
        return momentum_score
    
    def _calculate_quality_score(self, df: pd.DataFrame) -> pd.Series:
        """Calculate Quality factor score
        
        Metrics:
        - ROE (higher is better)
        - ROA (higher is better)
        - Debt/Equity (lower is better)
        - Current Ratio (higher is better, but not too high)
        """
        roe_score = self._normalize_direct(df['roe'])
        roa_score = self._normalize_direct(df['roa'])
        debt_score = self._normalize_inverse(df['debt_equity'])
        
        # Current ratio: optimal around 1.5-2.5
        current_optimal = 2.0
        current_score = 100 - np.abs(df['current_ratio'] - current_optimal) * 25
        current_score = current_score.clip(0, 100)
        
        quality_score = (roe_score + roa_score + debt_score + current_score) / 4
        
        return quality_score
    
    def _calculate_size_score(self, df: pd.DataFrame) -> pd.Series:
        """Calculate Size factor score
        
        Smaller companies often have higher returns (size premium)
        """
        # Inverse normalization (smaller = higher score)
        size_score = self._normalize_inverse(df['market_cap'])
        
        return size_score
    
    def _normalize_direct(self, series: pd.Series) -> pd.Series:
        """Normalize series where higher is better (0-100 scale)"""
        min_val = series.min()
        max_val = series.max()
        
        if max_val == min_val:
            return pd.Series([50.0] * len(series))
        
        normalized = ((series - min_val) / (max_val - min_val)) * 100
        return normalized
    
    def _normalize_inverse(self, series: pd.Series) -> pd.Series:
        """Normalize series where lower is better (0-100 scale)"""
        min_val = series.min()
        max_val = series.max()
        
        if max_val == min_val:
            return pd.Series([50.0] * len(series))
        
        normalized = ((max_val - series) / (max_val - min_val)) * 100
        return normalized
    
    def get_top_stocks(
        self,
        scores: List[FactorScore],
        n: int = 10,
        factor: Optional[str] = None
    ) -> List[FactorScore]:
        """Get top N stocks by factor
        
        Args:
            scores: List of FactorScore objects
            n: Number of stocks to return
            factor: Specific factor to sort by, or None for composite
            
        Returns:
            Top N stocks
        """
        if factor and factor in ['value', 'momentum', 'quality', 'size']:
            key = f'{factor}_score'
            sorted_scores = sorted(scores, key=lambda x: getattr(x, key), reverse=True)
        else:
            sorted_scores = sorted(scores, key=lambda x: x.composite_score, reverse=True)
        
        return sorted_scores[:n]
    
    def get_factor_exposure(self, portfolio: List[str], scores: List[FactorScore]) -> Dict:
        """Calculate portfolio's factor exposures
        
        Args:
            portfolio: List of stock symbols
            scores: List of FactorScore objects
            
        Returns:
            Dict with average factor scores
        """
        portfolio_scores = [s for s in scores if s.symbol in portfolio]
        
        if not portfolio_scores:
            return {
                'value': 0.0,
                'momentum': 0.0,
                'quality': 0.0,
                'size': 0.0,
                'composite': 0.0
            }
        
        return {
            'value': np.mean([s.value_score for s in portfolio_scores]),
            'momentum': np.mean([s.momentum_score for s in portfolio_scores]),
            'quality': np.mean([s.quality_score for s in portfolio_scores]),
            'size': np.mean([s.size_score for s in portfolio_scores]),
            'composite': np.mean([s.composite_score for s in portfolio_scores])
        }


# Test
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    # Generate sample data
    np.random.seed(42)
    n_stocks = 50
    
    data = pd.DataFrame({
        'symbol': [f'STK{i:02d}' for i in range(n_stocks)],
        'price': np.random.uniform(1000, 10000, n_stocks),
        'pe_ratio': np.random.uniform(5, 30, n_stocks),
        'pb_ratio': np.random.uniform(0.5, 5, n_stocks),
        'dividend_yield': np.random.uniform(0, 8, n_stocks),
        'return_1m': np.random.uniform(-10, 15, n_stocks),
        'return_3m': np.random.uniform(-15, 25, n_stocks),
        'return_6m': np.random.uniform(-20, 40, n_stocks),
        'return_12m': np.random.uniform(-30, 80, n_stocks),
        'roe': np.random.uniform(5, 30, n_stocks),
        'roa': np.random.uniform(2, 15, n_stocks),
        'debt_equity': np.random.uniform(0.2, 2.5, n_stocks),
        'current_ratio': np.random.uniform(0.8, 3.5, n_stocks),
        'market_cap': np.random.uniform(1e12, 100e12, n_stocks)
    })
    
    # Run factor analysis
    analyzer = FactorAnalyzer()
    scores = analyzer.analyze(data)
    
    print("\n=== Top 10 Stocks by Composite Score ===")
    top10 = analyzer.get_top_stocks(scores, n=10)
    for i, s in enumerate(top10, 1):
        print(f"{i:2d}. {s.symbol}: {s.composite_score:.2f} "
              f"(V:{s.value_score:.1f} M:{s.momentum_score:.1f} "
              f"Q:{s.quality_score:.1f} S:{s.size_score:.1f})")
    
    print("\n=== Top 5 by Value ===")
    top_value = analyzer.get_top_stocks(scores, n=5, factor='value')
    for s in top_value:
        print(f"  {s.symbol}: {s.value_score:.2f}")
    
    print("\n=== Top 5 by Momentum ===")
    top_momentum = analyzer.get_top_stocks(scores, n=5, factor='momentum')
    for s in top_momentum:
        print(f"  {s.symbol}: {s.momentum_score:.2f}")
    
    # Portfolio exposure
    portfolio = [s.symbol for s in top10]
    exposure = analyzer.get_factor_exposure(portfolio, scores)
    print(f"\n=== Portfolio Factor Exposure ===")
    for factor, score in exposure.items():
        print(f"  {factor.capitalize():12s}: {score:.2f}")
