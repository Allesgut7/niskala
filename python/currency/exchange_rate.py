# Niskala - Exchange Rate Engine
# Real-time exchange rates from Frankfurter API

import json
from typing import Dict, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False


class ExchangeRateEngine:
    """Exchange rate fetching and caching"""
    
    BASE_URL = "https://api.frankfurter.app"
    
    SUPPORTED_CURRENCIES = ['IDR', 'SGD', 'MYR', 'THB', 'PHP', 'VND', 'USD', 'EUR', 'GBP', 'JPY']
    
    def __init__(self):
        self.rates: Dict[str, float] = {}
        self.last_update: Optional[datetime] = None
        self.cache_ttl = timedelta(hours=1)
    
    async def fetch_rates(self, base: str = 'USD') -> Dict[str, float]:
        """Fetch rates from Frankfurter API"""
        if not HAS_HTTPX:
            logger.warning("httpx not installed, using mock rates")
            return self._get_mock_rates(base)
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                currencies = ','.join(c for c in self.SUPPORTED_CURRENCIES if c != base)
                response = await client.get(
                    f"{self.BASE_URL}/latest",
                    params={'from': base, 'to': currencies}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.rates = data.get('rates', {})
                    self.rates[base] = 1.0
                    self.last_update = datetime.now()
                    logger.info(f"Exchange rates updated: {len(self.rates)} currencies")
                    return self.rates
                else:
                    logger.error(f"Failed to fetch rates: {response.status_code}")
                    return self._get_mock_rates(base)
        except Exception as e:
            logger.error(f"Exchange rate fetch error: {e}")
            return self._get_mock_rates(base)
    
    def _get_mock_rates(self, base: str = 'USD') -> Dict[str, float]:
        """Get mock rates for testing"""
        mock_rates = {
            'USD': 1.0,
            'IDR': 15800,
            'SGD': 1.35,
            'MYR': 4.75,
            'THB': 35.5,
            'PHP': 56.0,
            'VND': 24500,
            'EUR': 0.92,
            'GBP': 0.79,
            'JPY': 149.5,
        }
        
        if base in mock_rates:
            base_rate = mock_rates[base]
            return {k: v / base_rate for k, v in mock_rates.items()}
        
        return mock_rates
    
    def get_rate(self, from_currency: str, to_currency: str) -> float:
        """Get exchange rate"""
        if not self.rates:
            self.rates = self._get_mock_rates()
        
        if from_currency == to_currency:
            return 1.0
        
        from_rate = self.rates.get(from_currency, 1.0)
        to_rate = self.rates.get(to_currency, 1.0)
        
        return to_rate / from_rate
    
    def convert(self, amount: float, from_currency: str, to_currency: str) -> float:
        """Convert amount between currencies"""
        rate = self.get_rate(from_currency, to_currency)
        return amount * rate
    
    def get_all_rates(self, base: str = 'USD') -> Dict[str, float]:
        """Get all rates with base currency"""
        if not self.rates:
            self.rates = self._get_mock_rates()
        
        return self.rates
    
    def is_stale(self) -> bool:
        """Check if rates are stale"""
        if self.last_update is None:
            return True
        return datetime.now() - self.last_update > self.cache_ttl


# Singleton
_rate_engine: Optional[ExchangeRateEngine] = None


def get_rate_engine() -> ExchangeRateEngine:
    """Get global exchange rate engine"""
    global _rate_engine
    if _rate_engine is None:
        _rate_engine = ExchangeRateEngine()
    return _rate_engine
