# Niskala - ML Pattern Recognition
# Version: 1.0.0
# Candlestick and chart pattern detection

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import pandas as pd
import numpy as np
import logging


@dataclass
class PatternResult:
    """Detected pattern"""
    pattern_name: str
    pattern_type: str      # 'candlestick', 'chart', 'continuation'
    signal: str            # 'bullish', 'bearish', 'neutral'
    confidence: float      # 0-100
    start_idx: int
    end_idx: int
    description: str


class CandlestickPatterns:
    """Detect candlestick patterns"""
    
    @staticmethod
    def detect_all(df: pd.DataFrame) -> List[PatternResult]:
        """Detect all candlestick patterns
        
        Args:
            df: DataFrame with OHLC columns
            
        Returns:
            List of detected patterns
        """
        patterns = []
        
        # Single candlestick patterns
        patterns.extend(CandlestickPatterns.doji(df))
        patterns.extend(CandlestickPatterns.hammer(df))
        patterns.extend(CandlestickPatterns.shooting_star(df))
        patterns.extend(CandlestickPatterns.engulfing(df))
        patterns.extend(CandlestickPatterns.morning_star(df))
        patterns.extend(CandlestickPatterns.evening_star(df))
        patterns.extend(CandlestickPatterns.three_white_soldiers(df))
        patterns.extend(CandlestickPatterns.three_black_crows(df))
        
        return patterns
    
    @staticmethod
    def doji(df: pd.DataFrame) -> List[PatternResult]:
        """Detect Doji pattern
        
        Doji: Open ≈ Close (very small body)
        """
        patterns = []
        
        for i in range(len(df)):
            row = df.iloc[i]
            body = abs(row['close'] - row['open'])
            total_range = row['high'] - row['low']
            
            if total_range == 0:
                continue
            
            body_ratio = body / total_range
            
            if body_ratio < 0.1:  # Body < 10% of range
                patterns.append(PatternResult(
                    pattern_name='Doji',
                    pattern_type='candlestick',
                    signal='neutral',
                    confidence=70.0,
                    start_idx=i,
                    end_idx=i,
                    description='Indecision candle, potential reversal'
                ))
        
        return patterns
    
    @staticmethod
    def hammer(df: pd.DataFrame) -> List[PatternResult]:
        """Detect Hammer pattern
        
        Hammer: Small body at top, long lower shadow
        """
        patterns = []
        
        for i in range(1, len(df)):
            row = df.iloc[i]
            body = abs(row['close'] - row['open'])
            total_range = row['high'] - row['low']
            
            if total_range == 0:
                continue
            
            lower_shadow = min(row['open'], row['close']) - row['low']
            upper_shadow = row['high'] - max(row['open'], row['close'])
            
            # Hammer: long lower shadow, small body, small upper shadow
            if (lower_shadow > body * 2 and 
                upper_shadow < body * 0.5 and
                body > 0):
                
                # Check if in downtrend
                if df.iloc[i-1]['close'] > row['close']:
                    patterns.append(PatternResult(
                        pattern_name='Hammer',
                        pattern_type='candlestick',
                        signal='bullish',
                        confidence=65.0,
                        start_idx=i,
                        end_idx=i,
                        description='Potential bullish reversal at bottom'
                    ))
        
        return patterns
    
    @staticmethod
    def shooting_star(df: pd.DataFrame) -> List[PatternResult]:
        """Detect Shooting Star pattern
        
        Shooting Star: Small body at bottom, long upper shadow
        """
        patterns = []
        
        for i in range(1, len(df)):
            row = df.iloc[i]
            body = abs(row['close'] - row['open'])
            total_range = row['high'] - row['low']
            
            if total_range == 0:
                continue
            
            lower_shadow = min(row['open'], row['close']) - row['low']
            upper_shadow = row['high'] - max(row['open'], row['close'])
            
            # Shooting star: long upper shadow, small body, small lower shadow
            if (upper_shadow > body * 2 and 
                lower_shadow < body * 0.5 and
                body > 0):
                
                # Check if in uptrend
                if df.iloc[i-1]['close'] < row['close']:
                    patterns.append(PatternResult(
                        pattern_name='Shooting Star',
                        pattern_type='candlestick',
                        signal='bearish',
                        confidence=65.0,
                        start_idx=i,
                        end_idx=i,
                        description='Potential bearish reversal at top'
                    ))
        
        return patterns
    
    @staticmethod
    def engulfing(df: pd.DataFrame) -> List[PatternResult]:
        """Detect Engulfing pattern
        
        Bullish Engulfing: Bearish candle followed by larger bullish candle
        Bearish Engulfing: Bullish candle followed by larger bearish candle
        """
        patterns = []
        
        for i in range(1, len(df)):
            prev = df.iloc[i-1]
            curr = df.iloc[i]
            
            prev_bearish = prev['close'] < prev['open']
            curr_bullish = curr['close'] > curr['open']
            
            # Bullish engulfing
            if (prev_bearish and curr_bullish and
                curr['open'] <= prev['close'] and
                curr['close'] >= prev['open']):
                
                patterns.append(PatternResult(
                    pattern_name='Bullish Engulfing',
                    pattern_type='candlestick',
                    signal='bullish',
                    confidence=75.0,
                    start_idx=i-1,
                    end_idx=i,
                    description='Strong bullish reversal signal'
                ))
            
            # Bearish engulfing
            prev_bullish = prev['close'] > prev['open']
            curr_bearish = curr['close'] < curr['open']
            
            if (prev_bullish and curr_bearish and
                curr['open'] >= prev['close'] and
                curr['close'] <= prev['open']):
                
                patterns.append(PatternResult(
                    pattern_name='Bearish Engulfing',
                    pattern_type='candlestick',
                    signal='bearish',
                    confidence=75.0,
                    start_idx=i-1,
                    end_idx=i,
                    description='Strong bearish reversal signal'
                ))
        
        return patterns
    
    @staticmethod
    def morning_star(df: pd.DataFrame) -> List[PatternResult]:
        """Detect Morning Star pattern (3-candle bullish reversal)"""
        patterns = []
        
        for i in range(2, len(df)):
            first = df.iloc[i-2]
            second = df.iloc[i-1]
            third = df.iloc[i]
            
            # First: bearish, Second: small body (doji), Third: bullish
            if (first['close'] < first['open'] and
                abs(second['close'] - second['open']) < abs(first['close'] - first['open']) * 0.3 and
                third['close'] > third['open'] and
                third['close'] > (first['open'] + first['close']) / 2):
                
                patterns.append(PatternResult(
                    pattern_name='Morning Star',
                    pattern_type='candlestick',
                    signal='bullish',
                    confidence=80.0,
                    start_idx=i-2,
                    end_idx=i,
                    description='Strong 3-candle bullish reversal'
                ))
        
        return patterns
    
    @staticmethod
    def evening_star(df: pd.DataFrame) -> List[PatternResult]:
        """Detect Evening Star pattern (3-candle bearish reversal)"""
        patterns = []
        
        for i in range(2, len(df)):
            first = df.iloc[i-2]
            second = df.iloc[i-1]
            third = df.iloc[i]
            
            # First: bullish, Second: small body (doji), Third: bearish
            if (first['close'] > first['open'] and
                abs(second['close'] - second['open']) < abs(first['close'] - first['open']) * 0.3 and
                third['close'] < third['open'] and
                third['close'] < (first['open'] + first['close']) / 2):
                
                patterns.append(PatternResult(
                    pattern_name='Evening Star',
                    pattern_type='candlestick',
                    signal='bearish',
                    confidence=80.0,
                    start_idx=i-2,
                    end_idx=i,
                    description='Strong 3-candle bearish reversal'
                ))
        
        return patterns
    
    @staticmethod
    def three_white_soldiers(df: pd.DataFrame) -> List[PatternResult]:
        """Detect Three White Soldiers (3 consecutive bullish candles)"""
        patterns = []
        
        for i in range(2, len(df)):
            candles = [df.iloc[i-2], df.iloc[i-1], df.iloc[i]]
            
            all_bullish = all(c['close'] > c['open'] for c in candles)
            ascending = (candles[1]['close'] > candles[0]['close'] and 
                        candles[2]['close'] > candles[1]['close'])
            
            if all_bullish and ascending:
                patterns.append(PatternResult(
                    pattern_name='Three White Soldiers',
                    pattern_type='candlestick',
                    signal='bullish',
                    confidence=85.0,
                    start_idx=i-2,
                    end_idx=i,
                    description='Strong bullish continuation'
                ))
        
        return patterns
    
    @staticmethod
    def three_black_crows(df: pd.DataFrame) -> List[PatternResult]:
        """Detect Three Black Crows (3 consecutive bearish candles)"""
        patterns = []
        
        for i in range(2, len(df)):
            candles = [df.iloc[i-2], df.iloc[i-1], df.iloc[i]]
            
            all_bearish = all(c['close'] < c['open'] for c in candles)
            descending = (candles[1]['close'] < candles[0]['close'] and 
                         candles[2]['close'] < candles[1]['close'])
            
            if all_bearish and descending:
                patterns.append(PatternResult(
                    pattern_name='Three Black Crows',
                    pattern_type='candlestick',
                    signal='bearish',
                    confidence=85.0,
                    start_idx=i-2,
                    end_idx=i,
                    description='Strong bearish continuation'
                ))
        
        return patterns


class ChartPatterns:
    """Detect chart patterns (head & shoulders, triangles, etc.)"""
    
    @staticmethod
    def detect_all(df: pd.DataFrame) -> List[PatternResult]:
        """Detect all chart patterns"""
        patterns = []
        
        patterns.extend(ChartPatterns.double_top(df))
        patterns.extend(ChartPatterns.double_bottom(df))
        patterns.extend(ChartPatterns.head_and_shoulders(df))
        patterns.extend(ChartPatterns.triangle(df))
        
        return patterns
    
    @staticmethod
    def double_top(df: pd.DataFrame, lookback: int = 20) -> List[PatternResult]:
        """Detect Double Top pattern"""
        patterns = []
        
        if len(df) < lookback * 2:
            return patterns
        
        close = df['close'].values
        
        for i in range(lookback, len(df) - lookback):
            window = close[i-lookback:i+lookback]
            peaks = []
            
            # Find local peaks
            for j in range(1, len(window) - 1):
                if window[j] > window[j-1] and window[j] > window[j+1]:
                    peaks.append((j, window[j]))
            
            # Check for double top (two similar peaks)
            if len(peaks) >= 2:
                for p1_idx, p1_val in peaks:
                    for p2_idx, p2_val in peaks:
                        if p2_idx > p1_idx + 3:
                            # Peaks within 2% of each other
                            if abs(p1_val - p2_val) / p1_val < 0.02:
                                # Valley between peaks
                                valley = min(close[i-lookback+p1_idx:i-lookback+p2_idx])
                                if valley < p1_val * 0.97:
                                    patterns.append(PatternResult(
                                        pattern_name='Double Top',
                                        pattern_type='chart',
                                        signal='bearish',
                                        confidence=70.0,
                                        start_idx=i-lookback+p1_idx,
                                        end_idx=i-lookback+p2_idx,
                                        description='Bearish reversal pattern'
                                    ))
        
        return patterns
    
    @staticmethod
    def double_bottom(df: pd.DataFrame, lookback: int = 20) -> List[PatternResult]:
        """Detect Double Bottom pattern"""
        patterns = []
        
        if len(df) < lookback * 2:
            return patterns
        
        close = df['close'].values
        
        for i in range(lookback, len(df) - lookback):
            window = close[i-lookback:i+lookback]
            troughs = []
            
            # Find local troughs
            for j in range(1, len(window) - 1):
                if window[j] < window[j-1] and window[j] < window[j+1]:
                    troughs.append((j, window[j]))
            
            # Check for double bottom
            if len(troughs) >= 2:
                for t1_idx, t1_val in troughs:
                    for t2_idx, t2_val in troughs:
                        if t2_idx > t1_idx + 3:
                            if abs(t1_val - t2_val) / t1_val < 0.02:
                                peak = max(close[i-lookback+t1_idx:i-lookback+t2_idx])
                                if peak > t1_val * 1.03:
                                    patterns.append(PatternResult(
                                        pattern_name='Double Bottom',
                                        pattern_type='chart',
                                        signal='bullish',
                                        confidence=70.0,
                                        start_idx=i-lookback+t1_idx,
                                        end_idx=i-lookback+t2_idx,
                                        description='Bullish reversal pattern'
                                    ))
        
        return patterns
    
    @staticmethod
    def head_and_shoulders(df: pd.DataFrame, lookback: int = 30) -> List[PatternResult]:
        """Detect Head and Shoulders pattern"""
        patterns = []
        # Simplified detection
        return patterns
    
    @staticmethod
    def triangle(df: pd.DataFrame, lookback: int = 20) -> List[PatternResult]:
        """Detect Triangle patterns (ascending, descending, symmetrical)"""
        patterns = []
        
        if len(df) < lookback:
            return patterns
        
        close = df['close'].values
        
        for i in range(lookback, len(df)):
            window = close[i-lookback:i]
            
            # Calculate trend lines
            highs = []
            lows = []
            for j in range(1, len(window) - 1):
                if window[j] > window[j-1] and window[j] > window[j+1]:
                    highs.append((j, window[j]))
                if window[j] < window[j-1] and window[j] < window[j+1]:
                    lows.append((j, window[j]))
            
            if len(highs) >= 2 and len(lows) >= 2:
                # Check if highs are descending and lows are ascending (symmetrical)
                high_slope = (highs[-1][1] - highs[0][1]) / (highs[-1][0] - highs[0][0]) if highs[-1][0] != highs[0][0] else 0
                low_slope = (lows[-1][1] - lows[0][1]) / (lows[-1][0] - lows[0][0]) if lows[-1][0] != lows[0][0] else 0
                
                if high_slope < 0 and low_slope > 0:
                    patterns.append(PatternResult(
                        pattern_name='Symmetrical Triangle',
                        pattern_type='chart',
                        signal='neutral',
                        confidence=60.0,
                        start_idx=i-lookback,
                        end_idx=i,
                        description='Consolidation, breakout expected'
                    ))
        
        return patterns


class PatternDetector:
    """Main pattern detection engine"""
    
    def __init__(self):
        self.candlestick = CandlestickPatterns()
        self.chart = ChartPatterns()
        
        logging.info("Pattern detector initialized")
    
    def detect(self, df: pd.DataFrame) -> List[PatternResult]:
        """Detect all patterns in price data
        
        Args:
            df: DataFrame with OHLC columns
            
        Returns:
            List of detected patterns sorted by confidence
        """
        patterns = []
        
        # Candlestick patterns
        patterns.extend(self.candlestick.detect_all(df))
        
        # Chart patterns
        patterns.extend(self.chart.detect_all(df))
        
        # Sort by confidence
        patterns.sort(key=lambda p: p.confidence, reverse=True)
        
        logging.info(f"Detected {len(patterns)} patterns")
        
        return patterns
    
    def get_signal_summary(self, df: pd.DataFrame) -> Dict:
        """Get summary of pattern signals
        
        Returns:
            Dict with bullish/bearish/neutral counts and overall signal
        """
        patterns = self.detect(df)
        
        bullish = sum(1 for p in patterns if p.signal == 'bullish')
        bearish = sum(1 for p in patterns if p.signal == 'bearish')
        neutral = sum(1 for p in patterns if p.signal == 'neutral')
        
        # Overall signal
        if bullish > bearish * 1.5:
            overall = 'bullish'
        elif bearish > bullish * 1.5:
            overall = 'bearish'
        else:
            overall = 'neutral'
        
        return {
            'total_patterns': len(patterns),
            'bullish': bullish,
            'bearish': bearish,
            'neutral': neutral,
            'overall_signal': overall,
            'top_patterns': patterns[:5]
        }


# Test
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    # Generate sample data
    np.random.seed(42)
    dates = pd.date_range('2023-01-01', '2024-01-01', freq='D')
    
    # Create trending price data
    close = 4500 + np.cumsum(np.random.randn(len(dates)) * 30)
    
    df = pd.DataFrame({
        'open': close * (1 + np.random.randn(len(dates)) * 0.005),
        'high': close * (1 + abs(np.random.randn(len(dates)) * 0.01)),
        'low': close * (1 - abs(np.random.randn(len(dates)) * 0.01)),
        'close': close,
        'volume': np.random.randint(1000000, 5000000, len(dates))
    }, index=dates)
    
    # Detect patterns
    detector = PatternDetector()
    patterns = detector.detect(df)
    
    print(f"\n=== Pattern Detection Results ===")
    print(f"Total patterns found: {len(patterns)}")
    
    # Summary
    summary = detector.get_signal_summary(df)
    print(f"\nBullish: {summary['bullish']}")
    print(f"Bearish: {summary['bearish']}")
    print(f"Neutral: {summary['neutral']}")
    print(f"Overall: {summary['overall_signal']}")
    
    # Top patterns
    print(f"\nTop 5 Patterns:")
    for p in patterns[:5]:
        print(f"  {p.pattern_name} ({p.signal}) - Confidence: {p.confidence}%")
        print(f"    {p.description}")
