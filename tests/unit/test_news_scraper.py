# Niskala - News Scraper Tests
# Version: 1.0.0

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'python'))

from ai.news_scraper import NewsCollector


class TestNewsCollector:
    """Test RSS news collector"""
    
    def setup_method(self):
        self.collector = NewsCollector()
    
    def test_initialization(self):
        assert self.collector is not None
        assert len(self.collector.RSS_FEEDS) > 0
    
    def test_sector_keywords(self):
        assert 'Banking' in self.collector.sector_keywords
        assert 'Mining' in self.collector.sector_keywords
        assert 'Telecommunications' in self.collector.sector_keywords
    
    def test_detect_sectors(self):
        """Test sector detection from text"""
        sectors = self.collector._detect_sectors("Bank BCA melaporkan laba")
        assert 'Banking' in sectors
    
    def test_detect_tickers(self):
        """Test ticker detection from text"""
        tickers = self.collector._detect_tickers("BBCA dan BBRI naik 3%")
        assert 'BBCA' in tickers
        assert 'BBRI' in tickers
    
    def test_clean_text(self):
        """Test HTML cleaning"""
        result = self.collector._clean_text("<p>Hello <b>World</b></p>")
        assert result == "Hello World"
    
    def test_clean_text_empty(self):
        assert self.collector._clean_text("") == ""
        assert self.collector._clean_text(None) == ""
    
    @pytest.mark.slow
    def test_fetch_news(self):
        """Test news fetching (requires network)"""
        articles = self.collector.fetch_news(limit=3)
        assert isinstance(articles, list)
        # At least one source should work
        for art in articles:
            assert 'title' in art
            assert 'source' in art
            assert 'timestamp' in art


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
