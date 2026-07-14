# Niskala - IDX BEI Data Provider
# Version: 1.0.0

import requests
try:
    from curl_cffi import requests as curl_requests
    _use_curl = True
except ImportError:
    _use_curl = False
    curl_requests = None
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
from datetime import datetime
import json


class IdxBeiClient:
    """IDX (Indonesia Stock Exchange) official data scraper"""
    
    BASE_URL = "https://www.idx.co.id"
    
    def __init__(self):
        self._use_curl = _use_curl
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def _get(self, url: str, timeout: int = 10):
        """GET request using curl_cffi (bypasses Cloudflare) or fallback to requests"""
        if self._use_curl and curl_requests:
            return curl_requests.get(url, impersonate='chrome', timeout=timeout)
        return self.session.get(url, timeout=timeout)
        
    def get_market_summary(self) -> Dict:
        """Get market summary from IDX
        
        Returns:
            Dict with IHSG, volume, value, etc.
        """
        try:
            # IDX API endpoint for market data
            url = f"{self.BASE_URL}/api/v1/index/summary"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'ihsg': data.get('index_value', 0),
                    'change': data.get('change', 0),
                    'change_pct': data.get('change_pct', 0),
                    'volume': data.get('volume', 0),
                    'value': data.get('value', 0),
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return self._empty_market_summary()
                
        except Exception as e:
            print(f"IDX market summary error: {e}")
            return self._empty_market_summary()
    
    def get_stock_detail(self, symbol: str) -> Dict:
        """Get detailed stock information
        
        Args:
            symbol: Stock code (e.g., 'BBCA')
            
        Returns:
            Dict with stock details
        """
        try:
            url = f"{self.BASE_URL}/api/v1/stock/{symbol}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'symbol': symbol,
                    'name': data.get('name', symbol),
                    'price': data.get('price', 0),
                    'change': data.get('change', 0),
                    'change_pct': data.get('change_pct', 0),
                    'volume': data.get('volume', 0),
                    'value': data.get('value', 0),
                    'frequency': data.get('frequency', 0),
                    'previous': data.get('previous', 0),
                    'open': data.get('open', 0),
                    'high': data.get('high', 0),
                    'low': data.get('low', 0),
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return self._empty_stock_data(symbol)
                
        except Exception as e:
            print(f"IDX stock detail error for {symbol}: {e}")
            return self._empty_stock_data(symbol)
    
    def get_top_gainers(self, limit: int = 7) -> List[Dict]:
        """Get top gaining stocks from IDX
        
        Uses IDX endpoint: primary/Home/GetTopGainer?resultCount=N
        
        Args:
            limit: Number of stocks to return
            
        Returns:
            List of stock dicts with Code, Name, Price, Change, ChangePct
        """
        try:
            url = f"{self.BASE_URL}/primary/Home/GetTopGainer?resultCount={limit}"
            response = self._get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                items = data if isinstance(data, list) else data.get('data', [])
                return items[:limit]
            else:
                return []
                
        except Exception as e:
            print(f"IDX top gainers error: {e}")
            return []
    
    def get_top_losers(self, limit: int = 7) -> List[Dict]:
        """Get top losing stocks from IDX
        
        Uses IDX endpoint: primary/Home/GetTopLoser?resultCount=N
        
        Args:
            limit: Number of stocks to return
            
        Returns:
            List of stock dicts with Code, Name, Price, Change, ChangePct
        """
        try:
            url = f"{self.BASE_URL}/primary/Home/GetTopLoser?resultCount={limit}"
            response = self._get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                items = data if isinstance(data, list) else data.get('data', [])
                return items[:limit]
            else:
                return []
                
        except Exception as e:
            print(f"IDX top losers error: {e}")
            return []
    
    def get_most_active(self, limit: int = 10) -> List[Dict]:
        """Get most active stocks by volume
        
        Args:
            limit: Number of stocks to return
            
        Returns:
            List of stock dicts
        """
        try:
            url = f"{self.BASE_URL}/api/v1/top/active"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])[:limit]
            else:
                return []
                
        except Exception as e:
            print(f"IDX most active error: {e}")
            return []
    
    def get_sector_summary(self) -> List[Dict]:
        """Get sector performance summary
        
        Returns:
            List of sector performance dicts
        """
        try:
            url = f"{self.BASE_URL}/api/v1/sector/summary"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
            else:
                return []
                
        except Exception as e:
            print(f"IDX sector summary error: {e}")
            return []
    
    def get_stock_list(self) -> List[Dict]:
        """Get complete list of all IDX listed stocks
        
        Returns:
            List of dicts with Code, Name, ListingDate, Shares, ListingBoard
        """
        try:
            url = f"{self.BASE_URL}/api/v1/stock/list"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                stocks = data.get('data', [])
                return [{
                    'Code': s.get('Code', ''),
                    'Name': s.get('Name', ''),
                    'ListingDate': s.get('ListingDate', ''),
                    'Shares': s.get('Shares', 0),
                    'ListingBoard': s.get('ListingBoard', '')
                } for s in stocks if s.get('Code')]
            else:
                return []
                
        except Exception as e:
            print(f"IDX stock list error: {e}")
            return []
    
    def _empty_market_summary(self) -> Dict:
        """Return empty market summary"""
        return {
            'ihsg': 0,
            'change': 0,
            'change_pct': 0,
            'volume': 0,
            'value': 0,
            'timestamp': datetime.now().isoformat()
        }
    
    def _empty_stock_data(self, symbol: str) -> Dict:
        """Return empty stock data"""
        return {
            'symbol': symbol,
            'name': symbol,
            'price': 0,
            'change': 0,
            'change_pct': 0,
            'volume': 0,
            'timestamp': datetime.now().isoformat()
        }


# Test function
if __name__ == '__main__':
    client = IdxBeiClient()
    
    print("Testing IDX BEI Client...")
    
    # Market summary
    print("\nMarket Summary:")
    summary = client.get_market_summary()
    print(f"IHSG: {summary['ihsg']} ({summary['change_pct']:.2f}%)")
    
    # Top gainers
    print("\nTop Gainers:")
    gainers = client.get_top_gainers(5)
    for stock in gainers:
        print(f"{stock.get('symbol', 'N/A')}: +{stock.get('change_pct', 0):.2f}%")
