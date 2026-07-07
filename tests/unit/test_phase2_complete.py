# Niskala - Phase 2 Complete Tests
# Version: 1.0.0

import pytest
import sys
import os
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'python'))


class TestPatternRecognition:
    """Test pattern detection"""
    
    def setup_method(self):
        from analytics.pattern_recognition import PatternDetector
        self.detector = PatternDetector()
    
    def test_doji_detection(self):
        from analytics.pattern_recognition import CandlestickPatterns
        df = pd.DataFrame({
            'open': [100.0],
            'high': [105.0],
            'low': [95.0],
            'close': [100.1]  # Open ≈ Close = Doji
        })
        patterns = CandlestickPatterns.doji(df)
        assert len(patterns) == 1
        assert patterns[0].pattern_name == 'Doji'
    
    def test_engulfing_detection(self):
        from analytics.pattern_recognition import CandlestickPatterns
        df = pd.DataFrame({
            'open': [105.0, 98.0],
            'high': [106.0, 108.0],
            'low': [99.0, 97.0],
            'close': [100.0, 107.0]  # Bearish then Bullish engulfing
        })
        patterns = CandlestickPatterns.engulfing(df)
        assert any(p.pattern_name == 'Bullish Engulfing' for p in patterns)
    
    def test_detect_all(self):
        np.random.seed(42)
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        close = 4500 + np.cumsum(np.random.randn(100) * 30)
        
        df = pd.DataFrame({
            'open': close * 0.999,
            'high': close * 1.01,
            'low': close * 0.99,
            'close': close,
        }, index=dates)
        
        patterns = self.detector.detect(df)
        assert isinstance(patterns, list)
    
    def test_signal_summary(self):
        np.random.seed(42)
        dates = pd.date_range('2023-01-01', periods=50, freq='D')
        close = 4500 + np.cumsum(np.random.randn(50) * 30)
        
        df = pd.DataFrame({
            'open': close * 0.999,
            'high': close * 1.01,
            'low': close * 0.99,
            'close': close,
        }, index=dates)
        
        summary = self.detector.get_signal_summary(df)
        assert 'total_patterns' in summary
        assert 'overall_signal' in summary


class TestCorrelation:
    """Test correlation analysis"""
    
    def setup_method(self):
        from analytics.correlation import CorrelationAnalyzer
        self.analyzer = CorrelationAnalyzer()
        
        np.random.seed(42)
        dates = pd.date_range('2023-01-01', periods=100, freq='B')
        base = np.random.randn(100) * 0.02
        
        self.returns = pd.DataFrame({
            'A': base + np.random.randn(100) * 0.005,
            'B': base + np.random.randn(100) * 0.006,
            'C': np.random.randn(100) * 0.02,
        }, index=dates)
    
    def test_correlation_matrix(self):
        corr = self.analyzer.calculate_correlation_matrix(self.returns)
        assert corr.shape == (3, 3)
        assert corr.loc['A', 'A'] == 1.0
    
    def test_find_correlated_pairs(self):
        pairs = self.analyzer.find_correlated_pairs(self.returns, threshold=0.5)
        assert isinstance(pairs, list)
        # A and B should be correlated (same base)
        if pairs:
            assert any(p.symbol1 in ['A', 'B'] and p.symbol2 in ['A', 'B'] for p in pairs)
    
    def test_cluster_stocks(self):
        clusters = self.analyzer.cluster_stocks(self.returns, n_clusters=2)
        assert len(clusters) <= 2
        total_symbols = sum(len(c.symbols) for c in clusters)
        assert total_symbols == 3
    
    def test_diversification_pairs(self):
        pairs = self.analyzer.find_diversification_pairs(self.returns, n_pairs=2)
        assert len(pairs) <= 2


class TestPatternAlerts:
    """Test pattern alert system"""
    
    def setup_method(self):
        from analytics.pattern_alerts import PatternAlertManager
        self.manager = PatternAlertManager(db_path='/tmp/test_alerts_phase2.db')
    
    def test_create_alert(self):
        alert_id = self.manager.create_alert('BBRI', min_confidence=70.0)
        assert alert_id is not None
        
        alerts = self.manager.list_alerts()
        assert len(alerts) >= 1
    
    def test_delete_alert(self):
        alert_id = self.manager.create_alert('BBCA')
        deleted = self.manager.delete_alert(alert_id)
        assert deleted is True
    
    def test_list_alerts(self):
        self.manager.create_alert('TLKM')
        alerts = self.manager.list_alerts()
        assert isinstance(alerts, list)


class TestFearGreedHistory:
    """Test Fear & Greed historical tracking"""
    
    def setup_method(self):
        from fear_greed.history import FearGreedHistory, FearGreedSnapshot
        self.tracker = FearGreedHistory(db_path='/tmp/test_fg_history.db')
        self.Snapshot = FearGreedSnapshot
    
    def test_save_and_retrieve(self):
        snapshot = self.Snapshot(
            timestamp='2024-01-01T00:00:00',
            region='indonesia',
            score=65,
            status='Greed',
            components={'volatility': 60, 'momentum': 70}
        )
        
        self.tracker.save_snapshot(snapshot)
        latest = self.tracker.get_latest('indonesia')
        
        assert latest is not None
        assert latest.score == 65
    
    def test_statistics(self):
        stats = self.tracker.get_statistics('indonesia', 30)
        assert 'avg_score' in stats
        assert 'trend' in stats


class TestPerformanceUtils:
    """Test performance utilities"""
    
    def test_lru_cache(self):
        from utils.performance import LRUCache
        cache = LRUCache(max_size=3, ttl=60)
        
        cache.put('a', 1)
        cache.put('b', 2)
        cache.put('c', 3)
        
        assert cache.get('a') == 1
        assert cache.size == 3
        
        # Add one more (should evict oldest)
        cache.put('d', 4)
        assert cache.size == 3
    
    def test_data_cache(self):
        from utils.performance import DataCache
        dc = DataCache()
        
        dc.put_quote('TEST', {'price': 1000})
        assert dc.get_quote('TEST') == {'price': 1000}
        assert dc.get_quote('MISSING') is None
    
    def test_rate_limiter(self):
        from utils.performance import RateLimiter
        limiter = RateLimiter(max_calls=2, period=1.0)
        
        assert limiter.acquire() is True
        assert limiter.acquire() is True
        assert limiter.acquire() is False  # Rate limited
    
    def test_cache_stats(self):
        from utils.performance import LRUCache
        cache = LRUCache(max_size=10, ttl=60)
        
        cache.put('x', 1)
        cache.get('x')  # Hit
        cache.get('y')  # Miss
        
        stats = cache.stats()
        assert stats['hits'] == 1
        assert stats['misses'] == 1
        assert stats['hit_rate'] == 0.5


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
