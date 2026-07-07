# Niskala - Sentiment Analyzer Tests
# Version: 1.0.0

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'python'))


class TestFinBERTAnalyzer:
    """Test FinBERT sentiment analyzer"""
    
    @pytest.mark.slow
    def test_initialization(self):
        """Test model loading (requires model download)"""
        from ai.finbert_analyzer import FinBERTAnalyzer
        analyzer = FinBERTAnalyzer()
        assert analyzer is not None
        assert analyzer.model is not None
        assert analyzer.tokenizer is not None
    
    @pytest.mark.slow
    def test_positive_sentiment(self):
        """Test positive text analysis"""
        from ai.finbert_analyzer import FinBERTAnalyzer
        analyzer = FinBERTAnalyzer()
        result = analyzer.analyze("Bank BCA reports strong earnings growth")
        assert result['score'] > 0
        assert result['label'] == 'POSITIVE'
        assert result['confidence'] > 50
    
    @pytest.mark.slow
    def test_negative_sentiment(self):
        """Test negative text analysis"""
        from ai.finbert_analyzer import FinBERTAnalyzer
        analyzer = FinBERTAnalyzer()
        result = analyzer.analyze("Market crash amid global recession fears")
        assert result['score'] < 0
        assert result['label'] == 'NEGATIVE'
    
    @pytest.mark.slow
    def test_empty_text(self):
        """Test empty input handling"""
        from ai.finbert_analyzer import FinBERTAnalyzer
        analyzer = FinBERTAnalyzer()
        result = analyzer.analyze("")
        assert result['score'] == 0
        assert result['label'] == 'NEUTRAL'
    
    @pytest.mark.slow
    def test_batch_analysis(self):
        """Test batch analysis"""
        from ai.finbert_analyzer import FinBERTAnalyzer
        analyzer = FinBERTAnalyzer()
        texts = [
            "Strong growth in Q2",
            "Market decline continues"
        ]
        results = analyzer.analyze_batch(texts)
        assert len(results) == 2
        assert results[0]['score'] > results[1]['score']


class TestLLMInterpreter:
    """Test LLM interpreter"""
    
    def test_fallback_interpretation(self):
        """Test rule-based fallback"""
        from ai.llm_interpreter import LLMInterpreter
        interpreter = LLMInterpreter(provider="none")
        result = interpreter._fallback_interpretation("Bank BCA laba naik 15%")
        assert 'interpretation' in result
        assert 'sectors' in result
        assert 'tickers' in result
        assert 'Banking' in result['sectors']
    
    def test_fallback_negative(self):
        """Test negative detection"""
        from ai.llm_interpreter import LLMInterpreter
        interpreter = LLMInterpreter(provider="none")
        result = interpreter._fallback_interpretation("Market crash, stocks turun")
        assert result['impact'] == 'NEGATIVE'
    
    def test_empty_result(self):
        from ai.llm_interpreter import LLMInterpreter
        interpreter = LLMInterpreter(provider="none")
        result = interpreter.interpret("")
        assert result['impact'] == 'NEUTRAL'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
