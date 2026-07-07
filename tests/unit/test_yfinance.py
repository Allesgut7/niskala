# Niskala - YFinance Client Tests
# Version: 1.0.0

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'python'))

from data_sources.yfinance_client import YFinanceClient


class TestYFinanceClient:
    """Test YFinance data provider"""
    
    def setup_method(self):
        self.client = YFinanceClient()
    
    def test_client_initialization(self):
        assert self.client is not None
        assert self.client.cache == {}
    
    def test_empty_stock_data(self):
        """Test empty data structure"""
        data = self.client._empty_stock_data("TEST")
        assert data['symbol'] == "TEST"
        assert data['price'] == 0.0
        assert data['change'] == 0.0
        assert data['change_pct'] == 0.0
        assert data['volume'] == 0
    
    def test_index_names(self):
        """Test index name mapping"""
        assert self.client._get_index_name("^JKSE") == "IHSG"
        assert self.client._get_index_name("^GSPC") == "S&P 500"
        assert self.client._get_index_name("^N225") == "Nikkei 225"
    
    @pytest.mark.slow
    def test_get_stock_real(self):
        """Test real stock data fetch (requires network)"""
        data = self.client.get_stock('BBCA')
        assert data['symbol'] == 'BBCA'
        assert isinstance(data['price'], float)
        assert isinstance(data['change'], float)
    
    @pytest.mark.slow
    def test_get_index_real(self):
        """Test real index data fetch (requires network)"""
        data = self.client.get_index('^JKSE')
        assert data['symbol'] == '^JKSE'
        assert data['name'] == 'IHSG'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
