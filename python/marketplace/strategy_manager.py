# Niskala - Strategy Manager
# Strategy CRUD and management

import json
import uuid
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class Strategy:
    """Trading strategy"""
    id: str
    user_id: str
    name: str
    description: str
    category: str
    parameters: Dict
    backtest_results: Dict
    price: float
    is_public: bool
    is_premium: bool
    rating_avg: float
    rating_count: int
    download_count: int
    created_at: str
    updated_at: str


class StrategyManager:
    """Strategy marketplace manager"""
    
    def __init__(self, db_path: str = 'data/marketplace.db'):
        self.db_path = db_path
        self._init_db()
        logger.info("StrategyManager initialized")
    
    def _init_db(self):
        """Initialize database"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS strategies (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                category TEXT,
                parameters TEXT,
                backtest_results TEXT,
                price REAL DEFAULT 0,
                is_public BOOLEAN DEFAULT 0,
                is_premium BOOLEAN DEFAULT 0,
                rating_avg REAL DEFAULT 0,
                rating_count INTEGER DEFAULT 0,
                download_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS strategy_subscriptions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                strategy_id TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_date TIMESTAMP,
                payment_id TEXT,
                FOREIGN KEY (strategy_id) REFERENCES strategies(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_strategy(self, user_id: str, data: Dict) -> Strategy:
        """Create new strategy"""
        strategy_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        strategy = Strategy(
            id=strategy_id,
            user_id=user_id,
            name=data.get('name', ''),
            description=data.get('description', ''),
            category=data.get('category', 'other'),
            parameters=data.get('parameters', {}),
            backtest_results=data.get('backtest_results', {}),
            price=data.get('price', 0),
            is_public=data.get('is_public', False),
            is_premium=data.get('is_premium', False),
            rating_avg=0,
            rating_count=0,
            download_count=0,
            created_at=now,
            updated_at=now
        )
        
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO strategies (id, user_id, name, description, category,
                                   parameters, backtest_results, price, is_public,
                                   is_premium, rating_avg, rating_count, download_count,
                                   created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            strategy.id, strategy.user_id, strategy.name, strategy.description,
            strategy.category, json.dumps(strategy.parameters),
            json.dumps(strategy.backtest_results), strategy.price,
            strategy.is_public, strategy.is_premium, strategy.rating_avg,
            strategy.rating_count, strategy.download_count,
            strategy.created_at, strategy.updated_at
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Strategy created: {strategy_id}")
        return strategy
    
    def get_strategy(self, strategy_id: str) -> Optional[Strategy]:
        """Get strategy by ID"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM strategies WHERE id = ?', (strategy_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_strategy(row)
        return None
    
    def list_strategies(self, category: Optional[str] = None,
                       is_public: bool = True, limit: int = 50) -> List[Strategy]:
        """List strategies"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = 'SELECT * FROM strategies WHERE is_public = ?'
        params = [is_public]
        
        if category:
            query += ' AND category = ?'
            params.append(category)
        
        query += ' ORDER BY rating_avg DESC, download_count DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_strategy(row) for row in rows]
    
    def update_strategy(self, strategy_id: str, data: Dict) -> Optional[Strategy]:
        """Update strategy"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        for key in ['name', 'description', 'category', 'price', 'is_public', 'is_premium']:
            if key in data:
                updates.append(f'{key} = ?')
                params.append(data[key])
        
        if 'parameters' in data:
            updates.append('parameters = ?')
            params.append(json.dumps(data['parameters']))
        
        if 'backtest_results' in data:
            updates.append('backtest_results = ?')
            params.append(json.dumps(data['backtest_results']))
        
        updates.append('updated_at = ?')
        params.append(datetime.now().isoformat())
        
        params.append(strategy_id)
        
        cursor.execute(f'UPDATE strategies SET {", ".join(updates)} WHERE id = ?', params)
        conn.commit()
        conn.close()
        
        return self.get_strategy(strategy_id)
    
    def delete_strategy(self, strategy_id: str) -> bool:
        """Delete strategy"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM strategies WHERE id = ?', (strategy_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return deleted
    
    def get_user_strategies(self, user_id: str) -> List[Strategy]:
        """Get user's strategies"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM strategies WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_strategy(row) for row in rows]
    
    def increment_download(self, strategy_id: str):
        """Increment download count"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE strategies SET download_count = download_count + 1 WHERE id = ?', (strategy_id,))
        conn.commit()
        conn.close()
    
    def _row_to_strategy(self, row) -> Strategy:
        """Convert database row to Strategy"""
        return Strategy(
            id=row[0], user_id=row[1], name=row[2], description=row[3],
            category=row[4], parameters=json.loads(row[5]) if row[5] else {},
            backtest_results=json.loads(row[6]) if row[6] else {},
            price=row[7], is_public=row[8], is_premium=row[9],
            rating_avg=row[10], rating_count=row[11], download_count=row[12],
            created_at=row[13], updated_at=row[14]
        )
