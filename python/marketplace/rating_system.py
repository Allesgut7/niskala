# Niskala - Rating System
# Reviews and ratings for strategies

import uuid
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class Review:
    """Strategy review"""
    id: str
    user_id: str
    strategy_id: str
    rating: int
    comment: str
    created_at: str


class RatingSystem:
    """Rating and review system"""
    
    def __init__(self, db_path: str = 'data/marketplace.db'):
        self.db_path = db_path
        self._init_db()
        logger.info("RatingSystem initialized")
    
    def _init_db(self):
        """Initialize database"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS strategy_reviews (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                strategy_id TEXT NOT NULL,
                rating INTEGER CHECK (rating >= 1 AND rating <= 5),
                comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (strategy_id) REFERENCES strategies(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_review(self, user_id: str, strategy_id: str,
                   rating: int, comment: str = '') -> Review:
        """Add review"""
        review_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        review = Review(
            id=review_id,
            user_id=user_id,
            strategy_id=strategy_id,
            rating=rating,
            comment=comment,
            created_at=now
        )
        
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO strategy_reviews (id, user_id, strategy_id, rating, comment, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (review.id, review.user_id, review.strategy_id, review.rating, review.comment, review.created_at))
        
        # Update strategy average rating
        cursor.execute('''
            UPDATE strategies 
            SET rating_avg = (SELECT AVG(rating) FROM strategy_reviews WHERE strategy_id = ?),
                rating_count = (SELECT COUNT(*) FROM strategy_reviews WHERE strategy_id = ?)
            WHERE id = ?
        ''', (strategy_id, strategy_id, strategy_id))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Review added: {review_id}")
        return review
    
    def get_reviews(self, strategy_id: str, limit: int = 50) -> List[Review]:
        """Get reviews for strategy"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM strategy_reviews 
            WHERE strategy_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (strategy_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            Review(
                id=row[0], user_id=row[1], strategy_id=row[2],
                rating=row[3], comment=row[4], created_at=row[5]
            )
            for row in rows
        ]
    
    def get_average_rating(self, strategy_id: str) -> float:
        """Get average rating"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT AVG(rating) FROM strategy_reviews WHERE strategy_id = ?
        ''', (strategy_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result[0] else 0
    
    def get_user_review(self, user_id: str, strategy_id: str) -> Optional[Review]:
        """Get user's review for strategy"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM strategy_reviews 
            WHERE user_id = ? AND strategy_id = ?
        ''', (user_id, strategy_id))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Review(
                id=row[0], user_id=row[1], strategy_id=row[2],
                rating=row[3], comment=row[4], created_at=row[5]
            )
        return None
    
    def delete_review(self, review_id: str) -> bool:
        """Delete review"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM strategy_reviews WHERE id = ?', (review_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return deleted
    
    def get_top_rated(self, limit: int = 10) -> List[Dict]:
        """Get top rated strategies"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, rating_avg, rating_count
            FROM strategies
            WHERE is_public = 1 AND rating_count > 0
            ORDER BY rating_avg DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {'id': r[0], 'name': r[1], 'rating_avg': r[2], 'rating_count': r[3]}
            for r in rows
        ]
