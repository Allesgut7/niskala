# Niskala - Billing Manager
# Payment and subscription management

import uuid
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class Subscription:
    """Strategy subscription"""
    id: str
    user_id: str
    strategy_id: str
    status: str
    amount: float
    payment_method: str
    start_date: str
    end_date: str


class BillingManager:
    """Billing and payment manager"""
    
    def __init__(self, db_path: str = 'data/marketplace.db'):
        self.db_path = db_path
        logger.info("BillingManager initialized")
    
    async def create_subscription(self, user_id: str, strategy_id: str,
                                 payment_method: str = 'card') -> Dict:
        """Create subscription"""
        subscription_id = str(uuid.uuid4())
        now = datetime.now()
        
        # Get strategy price
        from .strategy_manager import StrategyManager
        sm = StrategyManager(self.db_path)
        strategy = sm.get_strategy(strategy_id)
        
        if not strategy:
            return {'error': 'Strategy not found'}
        
        # Create subscription
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO strategy_subscriptions 
            (id, user_id, strategy_id, status, start_date, end_date, payment_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            subscription_id, user_id, strategy_id, 'active',
            now.isoformat(), 
            (now.replace(month=now.month % 12 + 1) if now.month < 12 else now.replace(year=now.year + 1, month=1)).isoformat(),
            None
        ))
        
        conn.commit()
        conn.close()
        
        # Increment downloads
        sm.increment_download(strategy_id)
        
        logger.info(f"Subscription created: {subscription_id}")
        
        return {
            'subscription_id': subscription_id,
            'amount': strategy.price,
            'currency': 'USD',
            'status': 'active'
        }
    
    async def cancel_subscription(self, subscription_id: str) -> bool:
        """Cancel subscription"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE strategy_subscriptions 
            SET status = 'cancelled' 
            WHERE id = ?
        ''', (subscription_id,))
        
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return deleted
    
    async def get_user_subscriptions(self, user_id: str) -> List[Dict]:
        """Get user's active subscriptions"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT s.*, st.name as strategy_name
            FROM strategy_subscriptions s
            JOIN strategies st ON s.strategy_id = st.id
            WHERE s.user_id = ? AND s.status = 'active'
        ''', (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': row[0], 'user_id': row[1], 'strategy_id': row[2],
                'status': row[3], 'start_date': row[4], 'end_date': row[5],
                'payment_id': row[6], 'strategy_name': row[7]
            }
            for row in rows
        ]
    
    async def check_access(self, user_id: str, strategy_id: str) -> bool:
        """Check if user has access to strategy"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM strategy_subscriptions
            WHERE user_id = ? AND strategy_id = ? AND status = 'active'
            AND end_date > datetime('now')
        ''', (user_id, strategy_id))
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count > 0
