# Niskala - Fear & Greed Calculator
# Version: 1.0.0

import yfinance as yf
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import logging


class FearGreedCalculator:
    """Calculate Fear & Greed Index for multiple regions
    
    Indicators:
    - Volatility (25%): 50-day MA vs historical volatility
    - Breadth (15%): Advancing vs declining stocks
    - Momentum (25%): S&P/IHSG 125-day vs 50-day MA
    - Volume (15%): Current vs avg volume on up/down days
    - Sentiment (10%): Put/Call ratio or market breadth
    - Safe Haven (10%): Gold vs equities spread
    """
    
    WEIGHTS = {
        'volatility': 0.25,
        'breadth': 0.15,
        'momentum': 0.25,
        'volume': 0.15,
        'sentiment': 0.10,
        'safe_haven': 0.10
    }
    
    # Index mappings per region
    REGION_INDICES = {
        'indonesia': {
            'primary': '^JKSE',
            'stocks': ['BBCA.JK', 'BBRI.JK', 'BMRI.JK', 'TLKM.JK', 'GOTO.JK'],
            'safe_haven': 'GC=F'
        },
        'asia': {
            'primary': '^N225',
            'stocks': ['^N225', '^HSI', '^KS11', '^STI'],
            'safe_haven': 'GC=F'
        },
        'global': {
            'primary': '^GSPC',
            'stocks': ['^GSPC', '^IXIC', '^DJI'],
            'safe_haven': 'GC=F'
        }
    }
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = timedelta(minutes=5)
    
    def calculate(self, region: str) -> Dict:
        """Calculate Fear & Greed for a specific region
        
        Args:
            region: 'indonesia', 'asia', or 'global'
            
        Returns:
            Dict with:
                - score: 0-100 (0=Extreme Fear, 100=Extreme Greed)
                - status: Extreme Fear / Fear / Neutral / Greed / Extreme Greed
                - components: Dict of component scores
                - timestamp: ISO timestamp
        """
        if region not in self.REGION_INDICES:
            logging.error(f"Unknown region: {region}")
            return self._empty_result()
        
        try:
            indices = self.REGION_INDICES[region]
            
            # Calculate each component
            volatility = self._calc_volatility(indices['primary'])
            breadth    = self._calc_breadth(indices['stocks'])
            momentum   = self._calc_momentum(indices['primary'])
            volume     = self._calc_volume(indices['primary'])
            sentiment  = self._calc_sentiment(region)
            safe_haven = self._calc_safe_haven(indices['primary'], indices['safe_haven'])
            
            components = {
                'volatility': volatility,
                'breadth':    breadth,
                'momentum':   momentum,
                'volume':     volume,
                'sentiment':  sentiment,
                'safe_haven': safe_haven
            }
            
            # Weighted score
            score = int(sum(
                components[k] * self.WEIGHTS[k]
                for k in self.WEIGHTS
            ))
            
            return {
                'score': score,
                'status': self._classify(score),
                'components': components,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Fear & Greed calculation error for {region}: {e}")
            return self._empty_result()
    
    def calculate_all(self) -> Dict:
        """Calculate Fear & Greed for all regions
        
        Returns:
            Dict with results for each region
        """
        results = {}
        for region in self.REGION_INDICES:
            results[region] = self.calculate(region)
        
        # Overall (weighted: Indonesia 40%, Asia 30%, Global 30%)
        if all(r['score'] > 0 for r in results.values()):
            overall_score = int(
                results['indonesia']['score'] * 0.4 +
                results['asia']['score'] * 0.3 +
                results['global']['score'] * 0.3
            )
            results['overall'] = {
                'score': overall_score,
                'status': self._classify(overall_score),
                'components': {},
                'timestamp': datetime.now().isoformat()
            }
        
        return results
    
    def _calc_volatility(self, symbol: str) -> int:
        """Lower volatility = higher score (more greed)"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period='3mo')
            
            if hist.empty:
                return 50
            
            # Calculate 50-day historical volatility
            returns = hist['Close'].pct_change().dropna()
            vol_50 = returns.tail(50).std() * np.sqrt(252)
            
            # Normalize: lower vol = higher score
            # Typical range: 0.10 (low vol) to 0.40 (high vol)
            score = 100 - min(100, int(vol_50 * 250))
            return max(0, min(100, score))
            
        except Exception:
            return 50
    
    def _calc_breadth(self, symbols: List[str]) -> int:
        """More advancing stocks = higher score"""
        try:
            advancing = 0
            total = 0
            
            for sym in symbols:
                ticker = yf.Ticker(sym)
                hist = ticker.history(period='5d')
                
                if not hist.empty and len(hist) >= 2:
                    total += 1
                    if hist['Close'].iloc[-1] > hist['Close'].iloc[0]:
                        advancing += 1
            
            if total == 0:
                return 50
            
            return int((advancing / total) * 100)
            
        except Exception:
            return 50
    
    def _calc_momentum(self, symbol: str) -> int:
        """Price above MAs = higher score"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period='6mo')
            
            if hist.empty or len(hist) < 125:
                return 50
            
            current_price = hist['Close'].iloc[-1]
            ma_50  = hist['Close'].tail(50).mean()
            ma_125 = hist['Close'].tail(125).mean()
            
            score = 50
            if current_price > ma_50:
                score += 20
            if current_price > ma_125:
                score += 15
            if ma_50 > ma_125:
                score += 15
            
            return max(0, min(100, score))
            
        except Exception:
            return 50
    
    def _calc_volume(self, symbol: str) -> int:
        """Higher volume during uptrend = higher score"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period='3mo')
            
            if hist.empty:
                return 50
            
            avg_vol = hist['Volume'].mean()
            
            # Up days vs down days volume
            up_days = hist[hist['Close'] > hist['Close'].shift(1)]
            down_days = hist[hist['Close'] < hist['Close'].shift(1)]
            
            up_vol   = up_days['Volume'].mean() if not up_days.empty else 0
            down_vol = down_days['Volume'].mean() if not down_days.empty else 0
            
            if down_vol == 0:
                return 70
            if up_vol == 0:
                return 30
            
            ratio = up_vol / down_vol
            return int(min(100, ratio * 40))
            
        except Exception:
            return 50
    
    def _calc_sentiment(self, region: str) -> int:
        """Placeholder for sentiment component"""
        # TODO: integrate with real sentiment data (Stockbit, news)
        return 50
    
    def _calc_safe_haven(self, index_symbol: str, haven_symbol: str) -> int:
        """Gold down vs equities = higher score (Greed)"""
        try:
            idx = yf.Ticker(index_symbol)
            gold = yf.Ticker(haven_symbol)
            
            idx_5d = idx.history(period='5d')
            gold_5d = gold.history(period='5d')
            
            if idx_5d.empty or gold_5d.empty:
                return 50
            
            idx_chg = idx_5d['Close'].pct_change().dropna().sum()
            gold_chg = gold_5d['Close'].pct_change().dropna().sum()
            
            # Equities up, gold down = Greed
            spread = idx_chg - gold_chg
            
            score = 50 + int(spread * 200)
            return max(0, min(100, score))
            
        except Exception:
            return 50
    
    def _classify(self, score: int) -> str:
        if score <= 25:   return "Extreme Fear"
        if score <= 45:   return "Fear"
        if score <= 55:   return "Neutral"
        if score <= 75:   return "Greed"
        return "Extreme Greed"
    
    def _empty_result(self) -> Dict:
        return {
            'score': 0,
            'status': 'Unknown',
            'components': {},
            'timestamp': datetime.now().isoformat()
        }


# Test
if __name__ == '__main__':
    calc = FearGreedCalculator()
    
    print("Calculating Fear & Greed Index...\n")
    results = calc.calculate_all()
    
    for region, data in results.items():
        print(f"{region.upper()}: {data['score']} ({data['status']})")
        if data['components']:
            for comp, val in data['components'].items():
                print(f"  {comp}: {val}")
