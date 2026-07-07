# Niskala - Discovery Engine
# Search and recommendations

from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class DiscoveryEngine:
    """Discovery and search engine"""
    
    def __init__(self, db_path: str = 'data/marketplace.db'):
        self.db_path = db_path
        logger.info("DiscoveryEngine initialized")
    
    def search(self, query: str, category: Optional[str] = None,
              min_rating: float = 0, limit: int = 20) -> List[Dict]:
        """Search strategies"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        sql = '''
            SELECT id, name, description, category, rating_avg, download_count, price
            FROM strategies
            WHERE is_public = 1 AND (name LIKE ? OR description LIKE ?)
        '''
        params = [f'%{query}%', f'%{query}%']
        
        if category:
            sql += ' AND category = ?'
            params.append(category)
        
        sql += ' AND rating_avg >= ?'
        params.append(min_rating)
        
        sql += ' ORDER BY rating_avg DESC, download_count DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': r[0], 'name': r[1], 'description': r[2],
                'category': r[3], 'rating': r[4], 'downloads': r[5], 'price': r[6]
            }
            for r in rows
        ]
    
    def get_trending(self, period: str = '7d', limit: int = 10) -> List[Dict]:
        """Get trending strategies"""
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
    
    def get_categories(self) -> List[Dict]:
        """Get available categories"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT category, COUNT(*) as count
            FROM strategies
            WHERE is_public = 1
            GROUP BY category
            ORDER BY count DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        return [{'name': r[0], 'count': r[1]} for r in rows]
