# Niskala - User Profile Manager
# User profiles and stats

import uuid
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class UserProfile:
    """User profile"""
    user_id: str
    display_name: str
    bio: str
    avatar_url: str
    is_verified: bool
    trust_score: float
    total_trades: int
    win_rate: float
    roi_30d: float
    roi_90d: float
    roi_1y: float
    follower_count: int
    following_count: int
    created_at: str


class UserProfileManager:
    """User profile management"""
    
    def __init__(self, db_path: str = 'data/social.db'):
        self.db_path = db_path
        self._init_db()
        logger.info("UserProfileManager initialized")
    
    def _init_db(self):
        """Initialize database"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id TEXT PRIMARY KEY,
                display_name TEXT,
                bio TEXT,
                avatar_url TEXT,
                is_verified BOOLEAN DEFAULT 0,
                trust_score REAL DEFAULT 0,
                total_trades INTEGER DEFAULT 0,
                win_rate REAL DEFAULT 0,
                roi_30d REAL DEFAULT 0,
                roi_90d REAL DEFAULT 0,
                roi_1y REAL DEFAULT 0,
                follower_count INTEGER DEFAULT 0,
                following_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_profile(self, user_id: str, display_name: str = '') -> UserProfile:
        """Create user profile"""
        now = datetime.now().isoformat()
        
        profile = UserProfile(
            user_id=user_id,
            display_name=display_name or f'Trader_{user_id[:8]}',
            bio='',
            avatar_url='',
            is_verified=False,
            trust_score=0,
            total_trades=0,
            win_rate=0,
            roi_30d=0,
            roi_90d=0,
            roi_1y=0,
            follower_count=0,
            following_count=0,
            created_at=now
        )
        
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO user_profiles 
            (user_id, display_name, created_at)
            VALUES (?, ?, ?)
        ''', (user_id, display_name, now))
        
        conn.commit()
        conn.close()
        
        return profile
    
    def get_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM user_profiles WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_profile(row)
        return None
    
    def update_profile(self, user_id: str, data: Dict) -> Optional[UserProfile]:
        """Update profile"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        for key in ['display_name', 'bio', 'avatar_url']:
            if key in data:
                updates.append(f'{key} = ?')
                params.append(data[key])
        
        if updates:
            params.append(user_id)
            cursor.execute(f'UPDATE user_profiles SET {", ".join(updates)} WHERE user_id = ?', params)
            conn.commit()
        
        conn.close()
        return self.get_profile(user_id)
    
    def update_stats(self, user_id: str, trade_pnl: float):
        """Update user stats after trade"""
        profile = self.get_profile(user_id)
        if not profile:
            return
        
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        new_total = profile.total_trades + 1
        new_win_rate = ((profile.win_rate * profile.total_trades) + (1 if trade_pnl > 0 else 0)) / new_total
        
        cursor.execute('''
            UPDATE user_profiles 
            SET total_trades = ?, win_rate = ?
            WHERE user_id = ?
        ''', (new_total, new_win_rate, user_id))
        
        conn.commit()
        conn.close()
    
    def get_leaderboard(self, metric: str = 'roi_30d', limit: int = 10) -> List[UserProfile]:
        """Get leaderboard"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        valid_metrics = ['roi_30d', 'roi_90d', 'roi_1y', 'win_rate', 'trust_score']
        if metric not in valid_metrics:
            metric = 'roi_30d'
        
        cursor.execute(f'''
            SELECT * FROM user_profiles 
            WHERE total_trades > 0
            ORDER BY {metric} DESC 
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_profile(row) for row in rows]
    
    def _row_to_profile(self, row) -> UserProfile:
        """Convert row to profile"""
        return UserProfile(
            user_id=row[0], display_name=row[1], bio=row[2],
            avatar_url=row[3], is_verified=row[4], trust_score=row[5],
            total_trades=row[6], win_rate=row[7], roi_30d=row[8],
            roi_90d=row[9], roi_1y=row[10], follower_count=row[11],
            following_count=row[12], created_at=row[13]
        )
