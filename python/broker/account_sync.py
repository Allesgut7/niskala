# Niskala - Account Sync
# Account synchronization with brokers

import sqlite3
from typing import Dict, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AccountSync:
    """Account synchronization with brokers"""
    
    def __init__(self, db_path: str = 'data/broker_sync.db'):
        self.db_path = db_path
        self._init_db()
        logger.info(f"AccountSync initialized: {db_path}")
    
    def _init_db(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                broker TEXT NOT NULL,
                sync_type TEXT NOT NULL,
                status TEXT NOT NULL,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS broker_positions (
                broker TEXT NOT NULL,
                symbol TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                avg_price REAL NOT NULL,
                synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (broker, symbol)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS broker_orders (
                broker TEXT NOT NULL,
                order_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL,
                status TEXT NOT NULL,
                synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (broker, order_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    async def sync_positions(self, broker_name: str, broker) -> Dict:
        """Sync positions from broker
        
        Args:
            broker_name: Broker identifier
            broker: Broker instance
        
        Returns:
            Sync result
        """
        try:
            positions = await broker.get_positions()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Clear old positions for this broker
            cursor.execute('DELETE FROM broker_positions WHERE broker = ?', (broker_name,))
            
            # Insert new positions
            for pos in positions:
                cursor.execute('''
                    INSERT INTO broker_positions (broker, symbol, quantity, avg_price)
                    VALUES (?, ?, ?, ?)
                ''', (
                    broker_name,
                    pos.get('symbol', ''),
                    pos.get('quantity', 0),
                    pos.get('avg_price', 0),
                ))
            
            # Log sync
            cursor.execute('''
                INSERT INTO sync_log (broker, sync_type, status, details)
                VALUES (?, 'positions', 'success', ?)
            ''', (broker_name, f"Synced {len(positions)} positions"))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Synced {len(positions)} positions from {broker_name}")
            return {'success': True, 'count': len(positions)}
        
        except Exception as e:
            logger.error(f"Position sync failed: {e}")
            self._log_sync(broker_name, 'positions', 'error', str(e))
            return {'success': False, 'error': str(e)}
    
    async def sync_orders(self, broker_name: str, broker) -> Dict:
        """Sync order history from broker"""
        try:
            orders = await broker.get_order_history()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for order in orders:
                cursor.execute('''
                    INSERT OR REPLACE INTO broker_orders 
                    (broker, order_id, symbol, side, quantity, price, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    broker_name,
                    order.get('order_id', ''),
                    order.get('symbol', ''),
                    order.get('side', ''),
                    order.get('quantity', 0),
                    order.get('price'),
                    order.get('status', ''),
                ))
            
            cursor.execute('''
                INSERT INTO sync_log (broker, sync_type, status, details)
                VALUES (?, 'orders', 'success', ?)
            ''', (broker_name, f"Synced {len(orders)} orders"))
            
            conn.commit()
            conn.close()
            
            return {'success': True, 'count': len(orders)}
        
        except Exception as e:
            logger.error(f"Order sync failed: {e}")
            self._log_sync(broker_name, 'orders', 'error', str(e))
            return {'success': False, 'error': str(e)}
    
    def get_synced_positions(self, broker_name: str) -> List[Dict]:
        """Get synced positions from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT * FROM broker_positions WHERE broker = ?',
            (broker_name,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'broker': row[0],
                'symbol': row[1],
                'quantity': row[2],
                'avg_price': row[3],
                'synced_at': row[4],
            }
            for row in rows
        ]
    
    def get_sync_log(self, broker_name: Optional[str] = None,
                     limit: int = 50) -> List[Dict]:
        """Get sync history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if broker_name:
            cursor.execute(
                'SELECT * FROM sync_log WHERE broker = ? ORDER BY timestamp DESC LIMIT ?',
                (broker_name, limit)
            )
        else:
            cursor.execute(
                'SELECT * FROM sync_log ORDER BY timestamp DESC LIMIT ?',
                (limit,)
            )
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': row[0],
                'broker': row[1],
                'sync_type': row[2],
                'status': row[3],
                'details': row[4],
                'timestamp': row[5],
            }
            for row in rows
        ]
    
    def _log_sync(self, broker: str, sync_type: str, status: str, details: str):
        """Log sync event"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sync_log (broker, sync_type, status, details)
            VALUES (?, ?, ?, ?)
        ''', (broker, sync_type, status, details))
        
        conn.commit()
        conn.close()
