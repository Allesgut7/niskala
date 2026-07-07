# Niskala - Fraud Detector
# Detection of suspicious trading patterns

import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@dataclass
class FraudAlert:
    """Fraud detection alert"""
    alert_type: str
    severity: str
    confidence: float
    description: str
    evidence: List[Dict]
    timestamp: str
    recommended_action: str


class FraudDetector:
    """Fraud detection for trading patterns"""
    
    def __init__(self):
        self.rules = self._load_rules()
        logger.info("FraudDetector initialized")
    
    def _load_rules(self) -> Dict:
        """Load fraud detection rules"""
        return {
            'wash_trading': {
                'description': 'Wash trading pattern detected',
                'severity': 'high',
                'threshold': 0.7
            },
            'pump_dump': {
                'description': 'Pump and dump pattern detected',
                'severity': 'critical',
                'threshold': 0.8
            },
            'insider_trading': {
                'description': 'Potential insider trading signals',
                'severity': 'critical',
                'threshold': 0.9
            },
            'unusual_volume': {
                'description': 'Unusual volume pattern',
                'severity': 'medium',
                'threshold': 0.6
            },
            'layering': {
                'description': 'Spoofing/layering pattern',
                'severity': 'high',
                'threshold': 0.75
            }
        }
    
    def check_trade(self, trade_data: Dict, historical_data: Optional[pd.DataFrame] = None) -> List[FraudAlert]:
        """Check trade for fraud indicators"""
        alerts = []
        
        # Check for wash trading
        wash_alert = self._check_wash_trading(trade_data)
        if wash_alert:
            alerts.append(wash_alert)
        
        # Check for pump and dump
        if historical_data is not None:
            pd_alert = self._check_pump_dump(trade_data, historical_data)
            if pd_alert:
                alerts.append(pd_alert)
        
        # Check for unusual patterns
        unusual_alert = self._check_unusual_patterns(trade_data, historical_data)
        if unusual_alert:
            alerts.append(unusual_alert)
        
        # Check for layering/spoofing
        layering_alert = self._check_layering(trade_data)
        if layering_alert:
            alerts.append(layering_alert)
        
        return alerts
    
    def _check_wash_trading(self, trade_data: Dict) -> Optional[FraudAlert]:
        """Check for wash trading (buying and selling to self)"""
        # Simplified detection: check if same account is on both sides
        buyer = trade_data.get('buyer_id')
        seller = trade_data.get('seller_id')
        
        if buyer and seller and buyer == seller:
            return FraudAlert(
                alert_type='wash_trading',
                severity='high',
                confidence=0.95,
                description='Same account appears on both sides of trade',
                evidence=[{'buyer': buyer, 'seller': seller}],
                timestamp=datetime.now().isoformat(),
                recommended_action='Block trade and investigate'
            )
        
        return None
    
    def _check_pump_dump(self, trade_data: Dict, historical: pd.DataFrame) -> Optional[FraudAlert]:
        """Check for pump and dump pattern"""
        if len(historical) < 20:
            return None
        
        symbol = trade_data.get('symbol', '')
        
        # Check for rapid price increase followed by sharp decline
        recent_returns = historical['close'].pct_change().tail(10).values
        
        # Pump: >20% increase in 5 days
        pump = any(r > 0.2 for r in recent_returns[:5])
        
        # Dump: >15% decrease in 5 days after pump
        dump = any(r < -0.15 for r in recent_returns[5:])
        
        # Volume spike during pump
        vol_ratio = historical['volume'].tail(5).mean() / historical['volume'].tail(20).mean()
        vol_spike = vol_ratio > 3
        
        if pump and dump and vol_spike:
            return FraudAlert(
                alert_type='pump_dump',
                severity='critical',
                confidence=0.85,
                description=f'Pump and dump pattern: {sum(recent_returns[:5]):.1%} increase followed by {sum(recent_returns[5:]):.1%} decline',
                evidence=[
                    {'pump_return': sum(recent_returns[:5])},
                    {'dump_return': sum(recent_returns[5:])},
                    {'volume_ratio': vol_ratio}
                ],
                timestamp=datetime.now().isoformat(),
                recommended_action='Suspend trading and investigate'
            )
        
        return None
    
    def _check_unusual_patterns(self, trade_data: Dict, 
                               historical: Optional[pd.DataFrame]) -> Optional[FraudAlert]:
        """Check for unusual trading patterns"""
        if historical is None or len(historical) < 20:
            return None
        
        # Check for abnormal order size
        trade_size = trade_data.get('quantity', 0)
        avg_size = historical['volume'].mean()
        
        if trade_size > avg_size * 10:
            return FraudAlert(
                alert_type='unusual_volume',
                severity='medium',
                confidence=0.7,
                description=f'Abnormal trade size: {trade_size:,.0f} shares ({trade_size/avg_size:.1f}x average)',
                evidence=[
                    {'trade_size': trade_size},
                    {'avg_size': avg_size},
                    {'ratio': trade_size / avg_size}
                ],
                timestamp=datetime.now().isoformat(),
                recommended_action='Review trade'
            )
        
        return None
    
    def _check_layering(self, trade_data: Dict) -> Optional[FraudAlert]:
        """Check for spoofing/layering pattern"""
        # Check for rapid order placement and cancellation
        orders = trade_data.get('recent_orders', [])
        
        if len(orders) < 5:
            return None
        
        # Count cancellations
        cancellations = sum(1 for o in orders if o.get('status') == 'cancelled')
        cancel_rate = cancellations / len(orders)
        
        if cancel_rate > 0.8 and len(orders) > 10:
            return FraudAlert(
                alert_type='layering',
                severity='high',
                confidence=0.8,
                description=f'High cancellation rate: {cancel_rate:.0%} ({cancellations}/{len(orders)})',
                evidence=[
                    {'total_orders': len(orders)},
                    {'cancellations': cancellations},
                    {'cancel_rate': cancel_rate}
                ],
                timestamp=datetime.now().isoformat(),
                recommended_action='Investigate for spoofing'
            )
        
        return None
    
    def check_portfolio(self, portfolio_data: Dict) -> List[FraudAlert]:
        """Check portfolio for fraud indicators"""
        alerts = []
        
        # Check for concentration risk
        positions = portfolio_data.get('positions', {})
        total_value = portfolio_data.get('total_value', 0)
        
        if total_value > 0:
            for symbol, position in positions.items():
                pos_value = position.get('market_value', 0)
                concentration = pos_value / total_value
                
                if concentration > 0.5:
                    alerts.append(FraudAlert(
                        alert_type='concentration_risk',
                        severity='medium',
                        confidence=0.9,
                        description=f'High concentration in {symbol}: {concentration:.1%}',
                        evidence=[{'symbol': symbol, 'concentration': concentration}],
                        timestamp=datetime.now().isoformat(),
                        recommended_action='Review position limits'
                    ))
        
        return alerts
    
    def generate_report(self, alerts: List[FraudAlert]) -> Dict:
        """Generate fraud detection report"""
        if not alerts:
            return {'status': 'clean', 'alerts': []}
        
        severity_counts = {}
        for alert in alerts:
            severity_counts[alert.severity] = severity_counts.get(alert.severity, 0) + 1
        
        return {
            'status': 'alerts_detected',
            'total_alerts': len(alerts),
            'severity_breakdown': severity_counts,
            'highest_severity': max(alerts, key=lambda a: {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}.get(a.severity, 0)).severity,
            'alerts': [
                {
                    'type': a.alert_type,
                    'severity': a.severity,
                    'confidence': a.confidence,
                    'description': a.description,
                    'timestamp': a.timestamp,
                    'action': a.recommended_action
                }
                for a in alerts
            ]
        }
