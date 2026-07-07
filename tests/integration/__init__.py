# Niskala - Integration Tests
# Version: 1.0.0

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'python'))


class TestDataPipeline:
    """Test data pipeline integration"""
    
    @pytest.mark.slow
    def test_yfinance_to_fear_greed(self):
        """Test YFinance data flowing into Fear & Greed calculation"""
        from data_sources.yfinance_client import YFinanceClient
        from fear_greed.calculator import FearGreedCalculator
        
        yf_client = YFinanceClient()
        fg_calc = FearGreedCalculator()
        
        # Get IHSG data
        ihsg = yf_client.get_index('^JKSE')
        assert ihsg['symbol'] == '^JKSE'
        assert isinstance(ihsg['price'], float)
        
        # Calculate Fear & Greed
        fg = fg_calc.calculate('indonesia')
        assert 0 <= fg['score'] <= 100
    
    @pytest.mark.slow
    def test_news_to_sentiment(self):
        """Test news collection flowing into sentiment analysis"""
        from ai.news_scraper import NewsCollector
        
        collector = NewsCollector()
        articles = collector.fetch_news(limit=3)
        
        # Check article structure
        for art in articles:
            assert 'title' in art
            assert 'source' in art
            assert 'sectors' in art
            assert 'tickers' in art
            assert isinstance(art['sectors'], list)
            assert isinstance(art['tickers'], list)
    
    @pytest.mark.slow
    def test_watchlist_data_flow(self):
        """Test watchlist data retrieval"""
        from data_sources.yfinance_client import YFinanceClient
        
        client = YFinanceClient()
        watchlist = ['BBCA', 'BBRI', 'BMRI']
        
        stocks = client.get_stocks_batch(watchlist)
        assert len(stocks) == len(watchlist)
        
        for stock in stocks:
            assert stock['symbol'] in watchlist
            assert isinstance(stock['price'], float)
            assert isinstance(stock['volume'], int)
    
    @pytest.mark.slow
    def test_multi_region_fg(self):
        """Test multi-region Fear & Greed calculation"""
        from fear_greed.calculator import FearGreedCalculator
        
        calc = FearGreedCalculator()
        results = calc.calculate_all()
        
        # All regions should be present
        assert 'indonesia' in results
        assert 'asia' in results
        assert 'global' in results
        assert 'overall' in results
        
        # Overall should be weighted
        overall = results['overall']
        assert 0 <= overall['score'] <= 100


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
