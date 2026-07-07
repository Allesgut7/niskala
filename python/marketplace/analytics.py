# Niskala - Marketplace Analytics
# Marketplace statistics and insights

from typing import Dict, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class MarketplaceAnalytics:
    """Marketplace analytics"""
    
    def __init__(self, db_path: str = 'data/marketplace.db'):
        self.db_path = db_path
        logger.info("MarketplaceAnalytics initialized")
    
    def get_platform_stats(self) -> Dict:
        """Get platform statistics"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM strategies WHERE is_public = 1')
        total_strategies = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM strategy_subscriptions WHERE status = 'active'")
        active_subscriptions = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM strategy_reviews')
        total_reviews = cursor.fetchone()[0]
        
        cursor.execute('SELECT AVG(rating_avg) FROM strategies WHERE rating_count > 0')
        avg_rating = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_strategies': total_strategies,
            'active_subscriptions': active_subscriptions,
            'total_reviews': total_reviews,
            'average_rating': round(avg_rating, 2)
        }
    
    def get_category_stats(self) -> List[Dict]:
        """Get stats by category"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT category, COUNT(*) as count, AVG(rating_avg) as avg_rating
            FROM strategies
            WHERE is_public = 1
            GROUP BY category
            ORDER BY count DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {'category': r[0], 'count': r[1], 'avg_rating': round(r[2] or 0, 2)}
            for r in rows
        ]
    
    def get_top_strategies(self, limit: int = 10) -> List[Dict]:
        """Get top performing strategies"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, category, rating_avg, download_count, price
            FROM strategies
            WHERE is_public = 1
            ORDER BY download_count DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': r[0], 'name': r[1], 'category': r[2],
                'rating': r[3], 'downloads': r[4], 'price': r[5]
            }
            for r in rows
        ]
