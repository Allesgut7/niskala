# Niskala - Revenue Sharing
# Revenue split between platform and creators

from typing import Dict, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class RevenueSplit:
    """Revenue split configuration"""
    strategy_id: str
    creator_share: float  # e.g., 0.70 = 70%
    platform_share: float  # e.g., 0.30 = 30%


class RevenueSharing:
    """Revenue sharing between platform and strategy creators"""
    
    DEFAULT_SPLIT = 0.70  # Creator gets 70%
    
    def __init__(self, db_path: str = 'data/marketplace.db'):
        self.db_path = db_path
        logger.info("RevenueSharing initialized")
    
    def calculate_split(self, amount: float, creator_share: float = None) -> Dict:
        """Calculate revenue split"""
        share = creator_share or self.DEFAULT_SPLIT
        
        return {
            'total': amount,
            'creator': amount * share,
            'platform': amount * (1 - share),
            'creator_pct': share * 100,
            'platform_pct': (1 - share) * 100,
        }
    
    def process_payment(self, strategy_id: str, amount: float, 
                       creator_id: str) -> Dict:
        """Process payment and split revenue"""
        split = self.calculate_split(amount)
        
        # In production: process payments via Stripe/Midtrans
        # For now, return the split calculation
        
        logger.info(f"Payment processed: {amount} for strategy {strategy_id}")
        
        return {
            'strategy_id': strategy_id,
            'creator_id': creator_id,
            'amount': amount,
            'creator_payout': split['creator'],
            'platform_fee': split['platform'],
            'status': 'processed',
        }
    
    def get_creator_earnings(self, creator_id: str) -> Dict:
        """Get total earnings for creator"""
        # In production: query from database
        
        return {
            'creator_id': creator_id,
            'total_earned': 0,
            'pending_payout': 0,
            'payouts_completed': 0,
        }
