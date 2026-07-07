# Niskala - Signal Generator
# Version: 1.0.0
# Technical + Fundamental + Sentiment signal combination

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import pandas as pd
import numpy as np
import logging


class SignalType(Enum):
    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"
    STRONG_SELL = "STRONG_SELL"


@dataclass
class Signal:
    """Trading signal"""
    symbol: str
    signal: SignalType
    score: int           # -100 to +100
    confidence: int      # 0-100
    technical_score: int
    fundamental_score: int
    sentiment_score: int
    reasons: List[str]
    timeframe: str       # short, medium, long
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None


class TechnicalSignals:
    """Technical analysis signal generators"""
    
    @staticmethod
    def ma_crossover(data: pd.DataFrame, fast: int = 20, slow: int = 50) -> Dict:
        """Moving average crossover signal
        
        Args:
            data: DataFrame with 'close' column
            fast: Fast MA period
            slow: Slow MA period
            
        Returns:
            Dict with score and reason
        """
        if len(data) < slow:
            return {'score': 0, 'reason': 'Insufficient data'}
        
        ma_fast = data['close'].rolling(fast).mean()
        ma_slow = data['close'].rolling(slow).mean()
        
        current_fast = ma_fast.iloc[-1]
        current_slow = ma_slow.iloc[-1]
        prev_fast = ma_fast.iloc[-2]
        prev_slow = ma_slow.iloc[-2]
        
        # Golden cross (bullish)
        if prev_fast <= prev_slow and current_fast > current_slow:
            return {'score': 60, 'reason': f'Golden cross (MA{fast}/MA{slow})'}
        
        # Death cross (bearish)
        if prev_fast >= prev_slow and current_fast < current_slow:
            return {'score': -60, 'reason': f'Death cross (MA{fast}/MA{slow})'}
        
        # Above MAs (bullish)
        if current_fast > current_slow:
            return {'score': 20, 'reason': f'Price above MA{fast}/MA{slow}'}
        
        # Below MAs (bearish)
        return {'score': -20, 'reason': f'Price below MA{fast}/MA{slow}'}
    
    @staticmethod
    def rsi_signal(data: pd.DataFrame, period: int = 14) -> Dict:
        """RSI overbought/oversold signal
        
        Args:
            data: DataFrame with 'close' column
            period: RSI period
            
        Returns:
            Dict with score and reason
        """
        if len(data) < period + 1:
            return {'score': 0, 'reason': 'Insufficient data'}
        
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        current_rsi = rsi.iloc[-1]
        
        if current_rsi < 30:
            return {'score': 50, 'reason': f'RSI oversold ({current_rsi:.0f})'}
        elif current_rsi < 40:
            return {'score': 20, 'reason': f'RSI low ({current_rsi:.0f})'}
        elif current_rsi > 70:
            return {'score': -50, 'reason': f'RSI overbought ({current_rsi:.0f})'}
        elif current_rsi > 60:
            return {'score': -20, 'reason': f'RSI high ({current_rsi:.0f})'}
        
        return {'score': 0, 'reason': f'RSI neutral ({current_rsi:.0f})'}
    
    @staticmethod
    def macd_signal(data: pd.DataFrame) -> Dict:
        """MACD signal
        
        Args:
            data: DataFrame with 'close' column
            
        Returns:
            Dict with score and reason
        """
        if len(data) < 26:
            return {'score': 0, 'reason': 'Insufficient data'}
        
        ema12 = data['close'].ewm(span=12).mean()
        ema26 = data['close'].ewm(span=26).mean()
        macd_line = ema12 - ema26
        signal_line = macd_line.ewm(span=9).mean()
        
        current_macd = macd_line.iloc[-1]
        current_signal = signal_line.iloc[-1]
        prev_macd = macd_line.iloc[-2]
        prev_signal = signal_line.iloc[-2]
        
        # Bullish crossover
        if prev_macd <= prev_signal and current_macd > current_signal:
            return {'score': 40, 'reason': 'MACD bullish crossover'}
        
        # Bearish crossover
        if prev_macd >= prev_signal and current_macd < current_signal:
            return {'score': -40, 'reason': 'MACD bearish crossover'}
        
        # Above zero line
        if current_macd > 0:
            return {'score': 15, 'reason': 'MACD above zero'}
        
        return {'score': -15, 'reason': 'MACD below zero'}
    
    @staticmethod
    def bollinger_signal(data: pd.DataFrame, period: int = 20) -> Dict:
        """Bollinger Bands signal
        
        Args:
            data: DataFrame with 'close' column
            
        Returns:
            Dict with score and reason
        """
        if len(data) < period:
            return {'score': 0, 'reason': 'Insufficient data'}
        
        sma = data['close'].rolling(period).mean()
        std = data['close'].rolling(period).std()
        
        upper = sma + 2 * std
        lower = sma - 2 * std
        
        current_price = data['close'].iloc[-1]
        
        # Near lower band (potential buy)
        if current_price <= lower.iloc[-1]:
            return {'score': 40, 'reason': 'Price at lower Bollinger Band'}
        
        # Near upper band (potential sell)
        if current_price >= upper.iloc[-1]:
            return {'score': -40, 'reason': 'Price at upper Bollinger Band'}
        
        # Middle band
        return {'score': 0, 'reason': 'Price at middle of Bollinger Bands'}
    
    @staticmethod
    def volume_signal(data: pd.DataFrame, period: int = 20) -> Dict:
        """Volume breakout signal
        
        Args:
            data: DataFrame with 'close' and 'volume' columns
            
        Returns:
            Dict with score and reason
        """
        if len(data) < period:
            return {'score': 0, 'reason': 'Insufficient data'}
        
        avg_volume = data['volume'].rolling(period).mean()
        current_volume = data['volume'].iloc[-1]
        volume_ratio = current_volume / avg_volume.iloc[-1]
        
        price_change = data['close'].pct_change().iloc[-1]
        
        # High volume + price up = bullish
        if volume_ratio > 1.5 and price_change > 0:
            return {'score': 35, 'reason': f'Volume breakout up ({volume_ratio:.1f}x avg)'}
        
        # High volume + price down = bearish
        if volume_ratio > 1.5 and price_change < 0:
            return {'score': -35, 'reason': f'Volume breakout down ({volume_ratio:.1f}x avg)'}
        
        return {'score': 0, 'reason': 'Normal volume'}


class FundamentalSignals:
    """Fundamental analysis signal generators"""
    
    @staticmethod
    def value_signal(pe_ratio: float, pb_ratio: float, sector_pe: float = 15.0) -> Dict:
        """Value signal based on PE/PB ratios"""
        score = 0
        reasons = []
        
        # PE ratio
        if pe_ratio > 0:
            if pe_ratio < sector_pe * 0.7:
                score += 30
                reasons.append(f'PE below sector avg ({pe_ratio:.1f}x vs {sector_pe:.1f}x)')
            elif pe_ratio > sector_pe * 1.3:
                score -= 30
                reasons.append(f'PE above sector avg ({pe_ratio:.1f}x vs {sector_pe:.1f}x)')
        
        # PB ratio
        if pb_ratio < 1.0:
            score += 20
            reasons.append(f'PB below 1.0 ({pb_ratio:.2f}x)')
        elif pb_ratio > 3.0:
            score -= 20
            reasons.append(f'PB high ({pb_ratio:.2f}x)')
        
        return {'score': score, 'reason': '; '.join(reasons) if reasons else 'Neutral valuation'}
    
    @staticmethod
    def quality_signal(roe: float, debt_equity: float, current_ratio: float) -> Dict:
        """Quality signal based on financial health"""
        score = 0
        reasons = []
        
        # ROE
        if roe > 20:
            score += 25
            reasons.append(f'High ROE ({roe:.1f}%)')
        elif roe < 10:
            score -= 15
            reasons.append(f'Low ROE ({roe:.1f}%)')
        
        # Debt/Equity
        if debt_equity < 0.5:
            score += 20
            reasons.append(f'Low debt ({debt_equity:.2f})')
        elif debt_equity > 1.5:
            score -= 25
            reasons.append(f'High debt ({debt_equity:.2f})')
        
        # Current Ratio
        if 1.5 <= current_ratio <= 3.0:
            score += 10
            reasons.append(f'Healthy liquidity ({current_ratio:.1f})')
        elif current_ratio < 1.0:
            score -= 20
            reasons.append(f'Poor liquidity ({current_ratio:.1f})')
        
        return {'score': score, 'reason': '; '.join(reasons) if reasons else 'Neutral quality'}


class SentimentSignals:
    """Sentiment-based signal generators"""
    
    @staticmethod
    def news_sentiment_signal(sentiment_score: int, article_count: int) -> Dict:
        """News sentiment signal"""
        if article_count == 0:
            return {'score': 0, 'reason': 'No news coverage'}
        
        if sentiment_score > 50:
            return {'score': 40, 'reason': f'Strong positive news ({sentiment_score:+d})'}
        elif sentiment_score > 20:
            return {'score': 20, 'reason': f'Positive news ({sentiment_score:+d})'}
        elif sentiment_score < -50:
            return {'score': -40, 'reason': f'Strong negative news ({sentiment_score:+d})'}
        elif sentiment_score < -20:
            return {'score': -20, 'reason': f'Negative news ({sentiment_score:+d})'}
        
        return {'score': 0, 'reason': f'Neutral news ({sentiment_score:+d})'}


class SignalGenerator:
    """Combine all signal sources into unified signal"""
    
    # Signal weights
    WEIGHTS = {
        'technical': 0.40,
        'fundamental': 0.35,
        'sentiment': 0.25
    }
    
    def generate(
        self,
        symbol: str,
        price_data: pd.DataFrame,
        fundamentals: Dict,
        sentiment_score: int = 0,
        sentiment_count: int = 0
    ) -> Signal:
        """Generate combined signal
        
        Args:
            symbol: Stock ticker
            price_data: Historical price DataFrame
            fundamentals: Dict with pe_ratio, pb_ratio, roe, etc.
            sentiment_score: News sentiment score (-100 to +100)
            sentiment_count: Number of news articles
            
        Returns:
            Signal object
        """
        reasons = []
        
        # Technical signals
        tech_signals = [
            TechnicalSignals.ma_crossover(price_data),
            TechnicalSignals.rsi_signal(price_data),
            TechnicalSignals.macd_signal(price_data),
            TechnicalSignals.bollinger_signal(price_data),
            TechnicalSignals.volume_signal(price_data)
        ]
        
        technical_score = int(np.mean([s['score'] for s in tech_signals]))
        reasons.extend([s['reason'] for s in tech_signals if s['score'] != 0])
        
        # Fundamental signals
        fund_signals = [
            FundamentalSignals.value_signal(
                fundamentals.get('pe_ratio', 0),
                fundamentals.get('pb_ratio', 0),
                fundamentals.get('sector_pe', 15.0)
            ),
            FundamentalSignals.quality_signal(
                fundamentals.get('roe', 0),
                fundamentals.get('debt_equity', 0),
                fundamentals.get('current_ratio', 0)
            )
        ]
        
        fundamental_score = int(np.mean([s['score'] for s in fund_signals]))
        reasons.extend([s['reason'] for s in fund_signals if s['score'] != 0])
        
        # Sentiment signal
        sent_signal = SentimentSignals.news_sentiment_signal(sentiment_score, sentiment_count)
        sentiment_signal_score = sent_signal['score']
        if sent_signal['score'] != 0:
            reasons.append(sent_signal['reason'])
        
        # Combined score
        combined = int(
            technical_score * self.WEIGHTS['technical'] +
            fundamental_score * self.WEIGHTS['fundamental'] +
            sentiment_signal_score * self.WEIGHTS['sentiment']
        )
        
        # Determine signal type
        if combined >= 50:
            signal_type = SignalType.STRONG_BUY
        elif combined >= 25:
            signal_type = SignalType.BUY
        elif combined <= -50:
            signal_type = SignalType.STRONG_SELL
        elif combined <= -25:
            signal_type = SignalType.SELL
        else:
            signal_type = SignalType.HOLD
        
        # Confidence based on agreement
        scores = [technical_score, fundamental_score, sentiment_signal_score]
        agreement = sum(1 for s in scores if s > 0) - sum(1 for s in scores if s < 0)
        confidence = min(100, 50 + abs(agreement) * 15 + abs(combined) * 0.3)
        
        # Calculate target price and stop loss
        current_price = price_data['close'].iloc[-1]
        target_price = None
        stop_loss = None
        
        if signal_type in [SignalType.BUY, SignalType.STRONG_BUY]:
            target_price = current_price * 1.10  # 10% target
            stop_loss = current_price * 0.95     # 5% stop loss
        elif signal_type in [SignalType.SELL, SignalType.STRONG_SELL]:
            target_price = current_price * 0.90
            stop_loss = current_price * 1.05
        
        return Signal(
            symbol=symbol,
            signal=signal_type,
            score=combined,
            confidence=int(confidence),
            technical_score=technical_score,
            fundamental_score=fundamental_score,
            sentiment_score=sentiment_signal_score,
            reasons=reasons,
            timeframe='medium',
            target_price=target_price,
            stop_loss=stop_loss
        )


# Test
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    # Generate sample data
    np.random.seed(42)
    dates = pd.date_range('2023-06-01', '2024-01-01', freq='B')
    prices = 4500 + np.cumsum(np.random.randn(len(dates)) * 30)
    
    price_data = pd.DataFrame({
        'open': prices * 0.99,
        'high': prices * 1.01,
        'low': prices * 0.98,
        'close': prices,
        'volume': np.random.randint(1000000, 5000000, len(dates))
    }, index=dates)
    
    fundamentals = {
        'pe_ratio': 12.5,
        'pb_ratio': 1.8,
        'roe': 18.5,
        'debt_equity': 0.8,
        'current_ratio': 2.1,
        'sector_pe': 15.0
    }
    
    # Generate signal
    generator = SignalGenerator()
    signal = generator.generate(
        symbol='BBRI',
        price_data=price_data,
        fundamentals=fundamentals,
        sentiment_score=35,
        sentiment_count=5
    )
    
    print(f"\n=== Signal for {signal.symbol} ===")
    print(f"Signal: {signal.signal.value}")
    print(f"Score: {signal.score:+d}")
    print(f"Confidence: {signal.confidence}%")
    print(f"\nComponent Scores:")
    print(f"  Technical: {signal.technical_score:+d}")
    print(f"  Fundamental: {signal.fundamental_score:+d}")
    print(f"  Sentiment: {signal.sentiment_score:+d}")
    print(f"\nReasons:")
    for reason in signal.reasons:
        print(f"  - {reason}")
    if signal.target_price:
        print(f"\nTarget Price: {signal.target_price:,.0f}")
    if signal.stop_loss:
        print(f"Stop Loss: {signal.stop_loss:,.0f}")
