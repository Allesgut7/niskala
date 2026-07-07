# Niskala - Fear & Greed Calculator Tests
# Version: 1.0.0

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'python'))

from fear_greed.calculator import FearGreedCalculator


class TestFearGreedCalculator:
    """Test Fear & Greed Index calculator"""
    
    def setup_method(self):
        self.calc = FearGreedCalculator()
    
    def test_classify_extreme_fear(self):
        assert self.calc._classify(10) == "Extreme Fear"
    
    def test_classify_fear(self):
        assert self.calc._classify(35) == "Fear"
    
    def test_classify_neutral(self):
        assert self.calc._classify(50) == "Neutral"
    
    def test_classify_greed(self):
        assert self.calc._classify(65) == "Greed"
    
    def test_classify_extreme_greed(self):
        assert self.calc._classify(90) == "Extreme Greed"
    
    def test_empty_result(self):
        result = self.calc._empty_result()
        assert result['score'] == 0
        assert result['status'] == 'Unknown'
        assert 'timestamp' in result
    
    def test_weights_sum_to_one(self):
        total = sum(self.calc.WEIGHTS.values())
        assert abs(total - 1.0) < 0.001
    
    def test_weight_values(self):
        assert self.calc.WEIGHTS['volatility'] == 0.25
        assert self.calc.WEIGHTS['breadth'] == 0.15
        assert self.calc.WEIGHTS['momentum'] == 0.25
        assert self.calc.WEIGHTS['volume'] == 0.15
        assert self.calc.WEIGHTS['sentiment'] == 0.10
        assert self.calc.WEIGHTS['safe_haven'] == 0.10
    
    @pytest.mark.slow
    def test_calculate_indonesia(self):
        """Test Indonesia F&G calculation (requires network)"""
        result = self.calc.calculate('indonesia')
        assert 0 <= result['score'] <= 100
        assert result['status'] in [
            'Extreme Fear', 'Fear', 'Neutral', 'Greed', 'Extreme Greed'
        ]
        assert 'components' in result
        assert 'timestamp' in result
    
    @pytest.mark.slow
    def test_calculate_all(self):
        """Test all regions calculation (requires network)"""
        results = self.calc.calculate_all()
        assert 'indonesia' in results
        assert 'asia' in results
        assert 'global' in results
        assert 'overall' in results
    
    def test_score_range(self):
        """All scores should be in 0-100 range"""
        for score in [0, 25, 50, 75, 100]:
            result = self.calc._classify(score)
            assert isinstance(result, str)
            assert len(result) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
