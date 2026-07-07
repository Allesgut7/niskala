# Niskala - Currency Converter
# Multi-currency conversion and formatting

from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

from .exchange_rate import get_rate_engine


class CurrencyConverter:
    """Multi-currency conversion and formatting"""
    
    SUPPORTED_CURRENCIES = {
        'IDR': {'symbol': 'Rp', 'decimals': 0, 'name': 'Indonesian Rupiah'},
        'SGD': {'symbol': 'S$', 'decimals': 2, 'name': 'Singapore Dollar'},
        'MYR': {'symbol': 'RM', 'decimals': 2, 'name': 'Malaysian Ringgit'},
        'THB': {'symbol': '฿', 'decimals': 2, 'name': 'Thai Baht'},
        'PHP': {'symbol': '₱', 'decimals': 2, 'name': 'Philippine Peso'},
        'VND': {'symbol': '₫', 'decimals': 0, 'name': 'Vietnamese Dong'},
        'USD': {'symbol': '$', 'decimals': 2, 'name': 'US Dollar'},
        'EUR': {'symbol': '€', 'decimals': 2, 'name': 'Euro'},
        'GBP': {'symbol': '£', 'decimals': 2, 'name': 'British Pound'},
        'JPY': {'symbol': '¥', 'decimals': 0, 'name': 'Japanese Yen'},
    }
    
    def __init__(self):
        self.rate_engine = get_rate_engine()
    
    def convert(self, amount: float, from_currency: str, to_currency: str) -> float:
        """Convert amount between currencies"""
        return self.rate_engine.convert(amount, from_currency, to_currency)
    
    def format(self, amount: float, currency: str, show_symbol: bool = True) -> str:
        """Format amount with currency symbol"""
        currency_info = self.SUPPORTED_CURRENCIES.get(currency, {'symbol': currency, 'decimals': 2})
        
        decimals = currency_info['decimals']
        symbol = currency_info['symbol'] if show_symbol else ''
        
        formatted = f"{amount:,.{decimals}f}"
        
        if show_symbol:
            if currency in ['IDR', 'VND', 'JPY']:
                return f"{symbol}{formatted}"
            else:
                return f"{symbol} {formatted}"
        
        return formatted
    
    def get_symbol(self, currency: str) -> str:
        """Get currency symbol"""
        return self.SUPPORTED_CURRENCIES.get(currency, {}).get('symbol', currency)
    
    def get_decimals(self, currency: str) -> int:
        """Get decimal places for currency"""
        return self.SUPPORTED_CURRENCIES.get(currency, {}).get('decimals', 2)
    
    def get_currency_name(self, currency: str) -> str:
        """Get currency name"""
        return self.SUPPORTED_CURRENCIES.get(currency, {}).get('name', currency)
    
    def list_supported(self) -> list:
        """List all supported currencies"""
        return [
            {'code': code, 'symbol': info['symbol'], 'name': info['name']}
            for code, info in self.SUPPORTED_CURRENCIES.items()
        ]
    
    def format_change(self, change: float, currency: str = 'USD') -> str:
        """Format price change with sign"""
        sign = '+' if change >= 0 else ''
        return f"{sign}{self.format(change, currency)}"
    
    def format_percent(self, percent: float) -> str:
        """Format percentage"""
        sign = '+' if percent >= 0 else ''
        return f"{sign}{percent:.2f}%"
    
    def convert_portfolio(self, portfolio: Dict, target_currency: str) -> Dict:
        """Convert entire portfolio to target currency"""
        result = {
            'cash': {},
            'positions': {},
            'total_value': 0,
        }
        
        # Convert cash
        for currency, amount in portfolio.get('cash', {}).items():
            converted = self.convert(amount, currency, target_currency)
            result['cash'][currency] = converted
            result['total_value'] += converted
        
        # Convert positions
        for symbol, position in portfolio.get('positions', {}).items():
            pos_currency = position.get('currency', target_currency)
            market_value = position.get('market_value', 0)
            converted_value = self.convert(market_value, pos_currency, target_currency)
            
            result['positions'][symbol] = {
                **position,
                'market_value_original': market_value,
                'market_value_converted': converted_value,
            }
            result['total_value'] += converted_value
        
        return result


# Singleton
_converter: Optional[CurrencyConverter] = None


def get_converter() -> CurrencyConverter:
    """Get global currency converter"""
    global _converter
    if _converter is None:
        _converter = CurrencyConverter()
    return _converter
