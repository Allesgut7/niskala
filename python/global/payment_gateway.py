# Niskala - Payment Gateway
# Multi-country payment methods

from typing import Dict, List, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class PaymentMethod:
    """Payment method"""
    code: str
    name: str
    country: str
    type: str  # bank_transfer, e_wallet, credit_card
    processing_time: str
    fees: Dict


class PaymentGateway:
    """Multi-country payment gateway"""
    
    PAYMENT_METHODS = {
        'ID': [
            PaymentMethod('bank_transfer', 'Bank Transfer', 'ID', 'bank_transfer', 'instant', {'min': 10000, 'fee': 0}),
            PaymentMethod('gopay', 'GoPay', 'ID', 'e_wallet', 'instant', {'min': 10000, 'fee': 0}),
            PaymentMethod('ovo', 'OVO', 'ID', 'e_wallet', 'instant', {'min': 10000, 'fee': 0}),
            PaymentMethod('dana', 'DANA', 'ID', 'e_wallet', 'instant', {'min': 10000, 'fee': 0}),
            PaymentMethod('qris', 'QRIS', 'ID', 'qr_code', 'instant', {'min': 10000, 'fee': 0}),
        ],
        'SG': [
            PaymentMethod('paynow', 'PayNow', 'SG', 'qr_code', 'instant', {'min': 1, 'fee': 0}),
            PaymentMethod('nets', 'NETS', 'SG', 'bank_transfer', 'instant', {'min': 1, 'fee': 0}),
            PaymentMethod('credit_card', 'Credit Card', 'SG', 'credit_card', 'instant', {'min': 1, 'fee': 0.03}),
        ],
        'MY': [
            PaymentMethod('fpx', 'FPX', 'MY', 'bank_transfer', 'instant', {'min': 1, 'fee': 0}),
            PaymentMethod('touch_n_go', 'Touch n Go', 'MY', 'e_wallet', 'instant', {'min': 1, 'fee': 0}),
            PaymentMethod('credit_card', 'Credit Card', 'MY', 'credit_card', 'instant', {'min': 1, 'fee': 0.03}),
        ],
        'TH': [
            PaymentMethod('promptpay', 'PromptPay', 'TH', 'qr_code', 'instant', {'min': 1, 'fee': 0}),
            PaymentMethod('true_money', 'TrueMoney', 'TH', 'e_wallet', 'instant', {'min': 1, 'fee': 0}),
            PaymentMethod('credit_card', 'Credit Card', 'TH', 'credit_card', 'instant', {'min': 1, 'fee': 0.03}),
        ],
        'PH': [
            PaymentMethod('gcash', 'GCash', 'PH', 'e_wallet', 'instant', {'min': 1, 'fee': 0}),
            PaymentMethod('maya', 'Maya', 'PH', 'e_wallet', 'instant', {'min': 1, 'fee': 0}),
            PaymentMethod('bank_transfer', 'Bank Transfer', 'PH', 'bank_transfer', '1-2 days', {'min': 1, 'fee': 0}),
        ],
        'VN': [
            PaymentMethod('momo', 'MoMo', 'VN', 'e_wallet', 'instant', {'min': 10000, 'fee': 0}),
            PaymentMethod('zalopay', 'ZaloPay', 'VN', 'e_wallet', 'instant', {'min': 10000, 'fee': 0}),
            PaymentMethod('bank_transfer', 'Bank Transfer', 'VN', 'bank_transfer', 'instant', {'min': 10000, 'fee': 0}),
        ],
    }
    
    def __init__(self):
        logger.info("PaymentGateway initialized")
    
    def get_payment_methods(self, country: str) -> List[PaymentMethod]:
        """Get available payment methods for country"""
        return self.PAYMENT_METHODS.get(country, [])
    
    def get_payment_method(self, country: str, method_code: str) -> Optional[PaymentMethod]:
        """Get specific payment method"""
        methods = self.get_payment_methods(country)
        for method in methods:
            if method.code == method_code:
                return method
        return None
    
    def calculate_fee(self, country: str, method_code: str, amount: float) -> float:
        """Calculate payment fee"""
        method = self.get_payment_method(country, method_code)
        if not method:
            return 0
        
        fee_rate = method.fees.get('fee', 0)
        return amount * fee_rate
    
    def get_supported_countries(self) -> List[str]:
        """Get list of supported countries"""
        return list(self.PAYMENT_METHODS.keys())
