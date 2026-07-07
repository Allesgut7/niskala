# Niskala - Leaderboard System
# Trader rankings

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class LeaderboardEntry:
    """Leaderboard entry"""
    rank: int
    user_id: str
    display_name: str
    score: float
    metric: str
    stats: Dict


class Leaderboard:
    """Leaderboard system"""
    
    def __init__(self, db_path: str = 'data/social.db'):
        self.db_path = db_path
        logger.info("Leaderboard initialized")
    
    def calculate_leaderboard(self, period: str = '30d', 
                             metric: str = 'composite') -> List[LeaderboardEntry]:
        """Calculate leaderboard rankings"""
        from .user_profile import UserProfileManager
        
        pm = UserProfileManager(self.db_path)
        
        # Get metric column
        metric_map = {
            'roi_30d': 'roi_30d',
            'roi_90d': 'roi_90d',
            'roi_1y': 'roi_1y',
            'win_rate': 'win_rate',
            'composite': 'roi_30d'  # Default to ROI
        }
        
        db_metric = metric_map.get(metric, 'roi_30d')
        
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(f'''
            SELECT user_id, display_name, {db_metric}, total_trades, win_rate
            FROM user_profiles
            WHERE total_trades > 0
            ORDER BY {db_metric} DESC
            LIMIT 100
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        entries = []
        for rank, row in enumerate(rows, 1):
            # Calculate composite score
            if metric == 'composite':
                score = row[2] * 0.4 + row[4] * 100 * 0.3 + min(row[3] / 10, 1) * 100 * 0.3
            else:
                score = row[2]
            
            entries.append(LeaderboardEntry(
                rank=rank,
                user_id=row[0],
                display_name=row[1],
                score=score,
                metric=metric,
                stats={
                    'total_trades': row[3],
                    'win_rate': row[4],
                    'roi': row[2]
                }
            ))
        
        return entries
    
    def get_user_rank(self, user_id: str, metric: str = 'composite') -> Optional[LeaderboardEntry]:
        """Get user's rank"""
        entries = self.calculate_leaderboard(metric=metric)
        
        for entry in entries:
            if entry.user_id == user_id:
                return entry
        
        return None
    
    def get_top_traders(self, limit: int = 10, 
                       category: str = 'overall') -> List[LeaderboardEntry]:
        """Get top traders"""
        entries = self.calculate_leaderboard(period='30d', metric='composite')
        return entries[:limit]
