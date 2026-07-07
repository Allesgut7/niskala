# Niskala - Copy Trading Engine
# Automatic trade replication

import uuid
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class CopyRelationship:
    """Copy trading relationship"""
    id: str
    follower_id: str
    trader_id: str
    allocation_pct: float
    max_loss_pct: float
    status: str
    created_at: str


class CopyTradingEngine:
    """Copy trading engine"""
    
    def __init__(self, db_path: str = 'data/social.db'):
        self.db_path = db_path
        self._init_db()
        logger.info("CopyTradingEngine initialized")
    
    def _init_db(self):
        """Initialize database"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS copy_relationships (
                id TEXT PRIMARY KEY,
                follower_id TEXT NOT NULL,
                trader_id TEXT NOT NULL,
                allocation_pct REAL DEFAULT 10,
                max_loss_pct REAL DEFAULT 5,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS copy_trades (
                id TEXT PRIMARY KEY,
                relationship_id TEXT NOT NULL,
                trader_trade_id TEXT,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                pnl REAL DEFAULT 0,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def start_copying(self, follower_id: str, trader_id: str,
                      allocation_pct: float = 10, max_loss_pct: float = 5) -> CopyRelationship:
        """Start copy relationship"""
        rel_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        relationship = CopyRelationship(
            id=rel_id,
            follower_id=follower_id,
            trader_id=trader_id,
            allocation_pct=allocation_pct,
            max_loss_pct=max_loss_pct,
            status='active',
            created_at=now
        )
        
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO copy_relationships 
            (id, follower_id, trader_id, allocation_pct, max_loss_pct, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (rel_id, follower_id, trader_id, allocation_pct, max_loss_pct, 'active', now))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Copy relationship created: {follower_id} -> {trader_id}")
        return relationship
    
    def stop_copying(self, follower_id: str, trader_id: str) -> bool:
        """Stop copy relationship"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE copy_relationships 
            SET status = 'inactive'
            WHERE follower_id = ? AND trader_id = ? AND status = 'active'
        ''', (follower_id, trader_id))
        
        updated = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return updated
    
    def get_followers(self, trader_id: str) -> List[CopyRelationship]:
        """Get trader's followers"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM copy_relationships 
            WHERE trader_id = ? AND status = 'active'
        ''', (trader_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_relationship(row) for row in rows]
    
    def get_copying(self, follower_id: str) -> List[CopyRelationship]:
        """Get who follower is copying"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM copy_relationships 
            WHERE follower_id = ? AND status = 'active'
        ''', (follower_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_relationship(row) for row in rows]
    
    async def execute_copy(self, trader_trade: Dict) -> List[Dict]:
        """Execute copy trade for all followers"""
        trader_id = trader_trade.get('user_id')
        followers = self.get_followers(trader_id)
        
        results = []
        
        for rel in followers:
            # Calculate position size based on allocation
            follower_capital = trader_trade.get('follower_capital', 100_000_000)
            allocation = follower_capital * (rel.allocation_pct / 100)
            
            quantity = int(allocation / trader_trade['price'])
            quantity = (quantity // 100) * 100  # Round to lot size
            
            if quantity > 0:
                trade = {
                    'id': str(uuid.uuid4()),
                    'relationship_id': rel.id,
                    'follower_id': rel.follower_id,
                    'symbol': trader_trade['symbol'],
                    'side': trader_trade['side'],
                    'quantity': quantity,
                    'price': trader_trade['price'],
                    'status': 'executed'
                }
                
                # Save trade
                import sqlite3
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO copy_trades 
                    (id, relationship_id, symbol, side, quantity, price, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (trade['id'], rel.id, trade['symbol'], trade['side'],
                      trade['quantity'], trade['price'], 'executed'))
                
                conn.commit()
                conn.close()
                
                results.append(trade)
                logger.info(f"Copy trade executed: {rel.follower_id} - {trade['side']} {trade['quantity']} {trade['symbol']}")
        
        return results
    
    def _row_to_relationship(self, row) -> CopyRelationship:
        """Convert row to relationship"""
        return CopyRelationship(
            id=row[0], follower_id=row[1], trader_id=row[2],
            allocation_pct=row[3], max_loss_pct=row[4],
            status=row[5], created_at=row[6]
        )
