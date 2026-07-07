# Niskala - Follow System
# Follow/unfollow traders

from typing import Dict, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class FollowSystem:
    """Follow/unfollow system"""
    
    def __init__(self, db_path: str = 'data/social.db'):
        self.db_path = db_path
        self._init_db()
        logger.info("FollowSystem initialized")
    
    def _init_db(self):
        """Initialize database"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS follows (
                follower_id TEXT,
                following_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (follower_id, following_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def follow(self, follower_id: str, following_id: str) -> bool:
        """Follow a user"""
        if follower_id == following_id:
            return False
        
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO follows (follower_id, following_id)
                VALUES (?, ?)
            ''', (follower_id, following_id))
            
            # Update counts
            cursor.execute('''
                UPDATE user_profiles SET following_count = following_count + 1
                WHERE user_id = ?
            ''', (follower_id,))
            
            cursor.execute('''
                UPDATE user_profiles SET follower_count = follower_count + 1
                WHERE user_id = ?
            ''', (following_id,))
            
            conn.commit()
            conn.close()
            return True
        except:
            conn.close()
            return False
    
    def unfollow(self, follower_id: str, following_id: str) -> bool:
        """Unfollow a user"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM follows 
            WHERE follower_id = ? AND following_id = ?
        ''', (follower_id, following_id))
        
        if cursor.rowcount > 0:
            cursor.execute('''
                UPDATE user_profiles SET following_count = MAX(0, following_count - 1)
                WHERE user_id = ?
            ''', (follower_id,))
            
            cursor.execute('''
                UPDATE user_profiles SET follower_count = MAX(0, follower_count - 1)
                WHERE user_id = ?
            ''', (following_id,))
            
            conn.commit()
        
        conn.close()
        return cursor.rowcount > 0
    
    def is_following(self, follower_id: str, following_id: str) -> bool:
        """Check if following"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM follows 
            WHERE follower_id = ? AND following_id = ?
        ''', (follower_id, following_id))
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count > 0
    
    def get_followers(self, user_id: str) -> List[str]:
        """Get user's followers"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT follower_id FROM follows WHERE following_id = ?
        ''', (user_id,))
        
        followers = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return followers
    
    def get_following(self, user_id: str) -> List[str]:
        """Get who user follows"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT following_id FROM follows WHERE follower_id = ?
        ''', (user_id,))
        
        following = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return following
