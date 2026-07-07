# Niskala - Regional Compliance
# Regional compliance rules

from typing import Dict, List, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ComplianceRule:
    """Compliance rule for a market"""
    market: str
    regulator: str
    reporting_frequency: str
    max_position_pct: float
    requires_disclosure: bool
    trading_restrictions: List[str]
    tax_rules: Dict


class RegionalCompliance:
    """Regional compliance rules"""
    
    COMPLIANCE_RULES = {
        'IDX': ComplianceRule(
            market='IDX',
            regulator='OJK (Otoritas Jasa Keuangan)',
            reporting_frequency='quarterly',
            max_position_pct=0.20,
            requires_disclosure=True,
            trading_restrictions=['no_short_selling', 't_plus_2_settlement'],
            tax_rules={
                'capital_gains_tax': 0.001,
                'dividend_tax': 0.10,
                'foreign_ownership_limit': 0.49,
            }
        ),
        'SGX': ComplianceRule(
            market='SGX',
            regulator='MAS (Monetary Authority of Singapore)',
            reporting_frequency='quarterly',
            max_position_pct=0.20,
            requires_disclosure=True,
            trading_restrictions=['t_plus_2_settlement'],
            tax_rules={
                'capital_gains_tax': 0.0,
                'dividend_tax': 0.0,
                'foreign_ownership_limit': 1.0,
            }
        ),
        'Bursa': ComplianceRule(
            market='Bursa',
            regulator='SC (Securities Commission Malaysia)',
            reporting_frequency='quarterly',
            max_position_pct=0.20,
            requires_disclosure=True,
            trading_restrictions=['no_short_selling', 't_plus_2_settlement'],
            tax_rules={
                'capital_gains_tax': 0.0,
                'dividend_tax': 0.0,
                'foreign_ownership_limit': 1.0,
            }
        ),
        'SET': ComplianceRule(
            market='SET',
            regulator='SEC (Securities and Exchange Commission Thailand)',
            reporting_frequency='quarterly',
            max_position_pct=0.20,
            requires_disclosure=True,
            trading_restrictions=['t_plus_2_settlement'],
            tax_rules={
                'capital_gains_tax': 0.0,
                'dividend_tax': 0.10,
                'foreign_ownership_limit': 0.49,
            }
        ),
        'PSE': ComplianceRule(
            market='PSE',
            regulator='SEC (Securities and Exchange Commission Philippines)',
            reporting_frequency='quarterly',
            max_position_pct=0.20,
            requires_disclosure=True,
            trading_restrictions=['t_plus_2_settlement'],
            tax_rules={
                'capital_gains_tax': 0.006,
                'dividend_tax': 0.10,
                'foreign_ownership_limit': 1.0,
            }
        ),
        'HOSE': ComplianceRule(
            market='HOSE',
            regulator='SSC (State Securities Commission of Vietnam)',
            reporting_frequency='quarterly',
            max_position_pct=0.20,
            requires_disclosure=True,
            trading_restrictions=['t_plus_2_settlement'],
            tax_rules={
                'capital_gains_tax': 0.001,
                'dividend_tax': 0.05,
                'foreign_ownership_limit': 0.49,
            }
        ),
    }
    
    def __init__(self):
        logger.info("RegionalCompliance initialized")
    
    def get_compliance(self, market: str) -> Optional[ComplianceRule]:
        """Get compliance rules for market"""
        return self.COMPLIANCE_RULES.get(market)
    
    def check_position_limit(self, market: str, position_pct: float) -> Dict:
        """Check if position exceeds limit"""
        rule = self.get_compliance(market)
        if not rule:
            return {'allowed': True, 'reason': 'Unknown market'}
        
        if position_pct > rule.max_position_pct:
            return {
                'allowed': False,
                'reason': f'Position {position_pct:.1%} exceeds limit {rule.max_position_pct:.1%}',
                'limit': rule.max_position_pct,
            }
        
        return {'allowed': True}
    
    def check_foreign_ownership(self, market: str, foreign_ownership_pct: float) -> Dict:
        """Check foreign ownership limit"""
        rule = self.get_compliance(market)
        if not rule:
            return {'allowed': True, 'reason': 'Unknown market'}
        
        limit = rule.tax_rules.get('foreign_ownership_limit', 1.0)
        
        if foreign_ownership_pct > limit:
            return {
                'allowed': False,
                'reason': f'Foreign ownership {foreign_ownership_pct:.1%} exceeds limit {limit:.1%}',
                'limit': limit,
            }
        
        return {'allowed': True}
    
    def get_trading_restrictions(self, market: str) -> List[str]:
        """Get trading restrictions for market"""
        rule = self.get_compliance(market)
        if rule:
            return rule.trading_restrictions
        return []
    
    def get_tax_rules(self, market: str) -> Dict:
        """Get tax rules for market"""
        rule = self.get_compliance(market)
        if rule:
            return rule.tax_rules
        return {}
