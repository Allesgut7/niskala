# Niskala - Social Feed
# Real-time social trading feed

import uuid
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class FeedPost:
    """Social feed post"""
    id: str
    user_id: str
    content: str
    post_type: str
    likes: int
    comments_count: int
    created_at: str


class SocialFeed:
    """Social trading feed"""
    
    def __init__(self, db_path: str = 'data/social.db'):
        self.db_path = db_path
        self._init_db()
        logger.info("SocialFeed initialized")
    
    def _init_db(self):
        """Initialize database"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS social_posts (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                content TEXT,
                post_type TEXT DEFAULT 'trade',
                trade_data TEXT,
                likes INTEGER DEFAULT 0,
                comments_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS post_likes (
                user_id TEXT,
                post_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, post_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_post(self, user_id: str, content: str, 
                   post_type: str = 'trade', trade_data: Dict = None) -> FeedPost:
        """Create new post"""
        post_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        import json
        cursor.execute('''
            INSERT INTO social_posts (id, user_id, content, post_type, trade_data, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (post_id, user_id, content, post_type, 
              json.dumps(trade_data) if trade_data else None, now))
        
        conn.commit()
        conn.close()
        
        return FeedPost(
            id=post_id, user_id=user_id, content=content,
            post_type=post_type, likes=0, comments_count=0,
            created_at=now
        )
    
    def get_feed(self, user_id: Optional[str] = None, 
                page: int = 1, limit: int = 20) -> List[FeedPost]:
        """Get feed posts"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        offset = (page - 1) * limit
        
        cursor.execute('''
            SELECT * FROM social_posts 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            FeedPost(
                id=row[0], user_id=row[1], content=row[2],
                post_type=row[3], likes=row[5], comments_count=row[6],
                created_at=row[7]
            )
            for row in rows
        ]
    
    def like_post(self, user_id: str, post_id: str) -> bool:
        """Like a post"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO post_likes (user_id, post_id)
                VALUES (?, ?)
            ''', (user_id, post_id))
            
            cursor.execute('''
                UPDATE social_posts SET likes = likes + 1 WHERE id = ?
            ''', (post_id,))
            
            conn.commit()
            conn.close()
            return True
        except:
            conn.close()
            return False
    
    def unlike_post(self, user_id: str, post_id: str) -> bool:
        """Unlike a post"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM post_likes WHERE user_id = ? AND post_id = ?
        ''', (user_id, post_id))
        
        if cursor.rowcount > 0:
            cursor.execute('''
                UPDATE social_posts SET likes = likes - 1 WHERE id = ?
            ''', (post_id,))
            conn.commit()
        
        conn.close()
        return cursor.rowcount > 0
    
    def get_hot_posts(self, period: str = '24h', limit: int = 10) -> List[FeedPost]:
        """Get hot posts by likes"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM social_posts 
            WHERE created_at > datetime('now', '-1 day')
            ORDER BY likes DESC 
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            FeedPost(
                id=row[0], user_id=row[1], content=row[2],
                post_type=row[3], likes=row[5], comments_count=row[6],
                created_at=row[7]
            )
            for row in rows
        ]
