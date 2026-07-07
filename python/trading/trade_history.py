# Niskala - Trade History
# SQLite-based trade history persistence

import sqlite3
import json
import uuid
from typing import List, Optional, Dict
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging


@dataclass
class TradeRecord:
    """Persisted trade record"""
    id: str
    symbol: str
    side: str
    quantity: int
    price: float
    value: float
    commission: float
    pnl: float
    timestamp: str
    order_id: str = ''
    notes: str = ''


class TradeHistory:
    """SQLite-based trade history with analytics"""
    
    def __init__(self, db_path: str = 'data/paper_trading.db'):
        self.db_path = db_path
        self._init_db()
        logging.info(f"TradeHistory initialized: {db_path}")
    
    def _init_db(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS paper_orders (
                id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL CHECK (side IN ('buy', 'sell')),
                quantity INTEGER NOT NULL,
                order_type TEXT NOT NULL CHECK (order_type IN ('market', 'limit')),
                price REAL,
                status TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                filled_at TIMESTAMP,
                fill_price REAL,
                fill_quantity INTEGER DEFAULT 0,
                notes TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS paper_trades (
                id TEXT PRIMARY KEY,
                order_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                value REAL NOT NULL,
                commission REAL NOT NULL,
                pnl REAL DEFAULT 0,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (order_id) REFERENCES paper_orders(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS paper_positions (
                symbol TEXT PRIMARY KEY,
                quantity INTEGER NOT NULL DEFAULT 0,
                avg_price REAL NOT NULL DEFAULT 0,
                total_cost REAL NOT NULL DEFAULT 0,
                realized_pnl REAL NOT NULL DEFAULT 0,
                unrealized_pnl REAL NOT NULL DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS paper_portfolio (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                cash REAL NOT NULL,
                initial_capital REAL NOT NULL,
                total_realized_pnl REAL NOT NULL DEFAULT 0,
                total_commission REAL NOT NULL DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_trades_symbol ON paper_trades(symbol)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_trades_timestamp ON paper_trades(timestamp)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_orders_status ON paper_orders(status)
        ''')
        
        conn.commit()
        conn.close()
    
    def save_portfolio(self, cash: float, initial_capital: float,
                       total_realized_pnl: float = 0, total_commission: float = 0):
        """Save or update portfolio state"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO paper_portfolio (id, cash, initial_capital, total_realized_pnl, total_commission)
            VALUES (1, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                cash = excluded.cash,
                total_realized_pnl = excluded.total_realized_pnl,
                total_commission = excluded.total_commission,
                updated_at = CURRENT_TIMESTAMP
        ''', (cash, initial_capital, total_realized_pnl, total_commission))
        
        conn.commit()
        conn.close()
    
    def load_portfolio(self) -> Optional[Dict]:
        """Load portfolio state"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM paper_portfolio WHERE id = 1')
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'cash': row[1],
                'initial_capital': row[2],
                'total_realized_pnl': row[3],
                'total_commission': row[4],
            }
        return None
    
    def save_order(self, order_id: str, symbol: str, side: str, quantity: int,
                   order_type: str, price: Optional[float], status: str,
                   notes: str = ''):
        """Save order to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO paper_orders (id, symbol, side, quantity, order_type, price, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (order_id, symbol, side, quantity, order_type, price, status, notes))
        
        conn.commit()
        conn.close()
    
    def update_order_status(self, order_id: str, status: str,
                            fill_price: Optional[float] = None,
                            fill_quantity: Optional[int] = None):
        """Update order status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        filled_at = datetime.now().isoformat() if status in ('filled', 'partially_filled') else None
        
        cursor.execute('''
            UPDATE paper_orders 
            SET status = ?, fill_price = COALESCE(?, fill_price),
                fill_quantity = COALESCE(?, fill_quantity),
                filled_at = COALESCE(?, filled_at),
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (status, fill_price, fill_quantity, filled_at, order_id))
        
        conn.commit()
        conn.close()
    
    def save_trade(self, trade_id: str, order_id: str, symbol: str, side: str,
                   quantity: int, price: float, value: float, commission: float,
                   pnl: float = 0):
        """Save executed trade"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO paper_trades (id, order_id, symbol, side, quantity, price, value, commission, pnl)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (trade_id, order_id, symbol, side, quantity, price, value, commission, pnl))
        
        conn.commit()
        conn.close()
    
    def save_position(self, symbol: str, quantity: int, avg_price: float,
                      total_cost: float, realized_pnl: float = 0,
                      unrealized_pnl: float = 0):
        """Save or update position"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if quantity == 0:
            cursor.execute('DELETE FROM paper_positions WHERE symbol = ?', (symbol,))
        else:
            cursor.execute('''
                INSERT INTO paper_positions (symbol, quantity, avg_price, total_cost, realized_pnl, unrealized_pnl)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(symbol) DO UPDATE SET
                    quantity = excluded.quantity,
                    avg_price = excluded.avg_price,
                    total_cost = excluded.total_cost,
                    realized_pnl = excluded.realized_pnl,
                    unrealized_pnl = excluded.unrealized_pnl,
                    updated_at = CURRENT_TIMESTAMP
            ''', (symbol, quantity, avg_price, total_cost, realized_pnl, unrealized_pnl))
        
        conn.commit()
        conn.close()
    
    def load_positions(self) -> List[Dict]:
        """Load all open positions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM paper_positions WHERE quantity > 0')
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'symbol': row[0],
                'quantity': row[1],
                'avg_price': row[2],
                'total_cost': row[3],
                'realized_pnl': row[4],
                'unrealized_pnl': row[5],
            }
            for row in rows
        ]
    
    def get_trades(self, symbol: Optional[str] = None,
                   start_date: Optional[str] = None,
                   end_date: Optional[str] = None,
                   limit: int = 100) -> List[TradeRecord]:
        """Get trade history with filters"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = 'SELECT * FROM paper_trades WHERE 1=1'
        params = []
        
        if symbol:
            query += ' AND symbol = ?'
            params.append(symbol)
        if start_date:
            query += ' AND timestamp >= ?'
            params.append(start_date)
        if end_date:
            query += ' AND timestamp <= ?'
            params.append(end_date)
        
        query += ' ORDER BY timestamp DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [
            TradeRecord(
                id=row[0], order_id=row[1], symbol=row[2], side=row[3],
                quantity=row[4], price=row[5], value=row[6], commission=row[7],
                pnl=row[8], timestamp=row[9]
            )
            for row in rows
        ]
    
    def get_orders(self, status: Optional[str] = None,
                   symbol: Optional[str] = None,
                   limit: int = 50) -> List[Dict]:
        """Get order history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = 'SELECT * FROM paper_orders WHERE 1=1'
        params = []
        
        if status:
            query += ' AND status = ?'
            params.append(status)
        if symbol:
            query += ' AND symbol = ?'
            params.append(symbol)
        
        query += ' ORDER BY created_at DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': row[0], 'symbol': row[1], 'side': row[2],
                'quantity': row[3], 'order_type': row[4], 'price': row[5],
                'status': row[6], 'created_at': row[7], 'updated_at': row[8],
                'filled_at': row[9], 'fill_price': row[10],
                'fill_quantity': row[11], 'notes': row[12],
            }
            for row in rows
        ]
    
    def get_trade_summary(self, days: int = 30) -> Dict:
        """Get trade summary for period"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        start_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total_trades,
                SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
                SUM(CASE WHEN pnl < 0 THEN 1 ELSE 0 END) as losing_trades,
                SUM(pnl) as total_pnl,
                SUM(commission) as total_commission,
                AVG(pnl) as avg_pnl,
                MAX(pnl) as best_trade,
                MIN(pnl) as worst_trade
            FROM paper_trades
            WHERE timestamp >= ?
        ''', (start_date,))
        
        row = cursor.fetchone()
        conn.close()
        
        total = row[0] or 0
        winning = row[1] or 0
        
        return {
            'period_days': days,
            'total_trades': total,
            'winning_trades': winning,
            'losing_trades': row[2] or 0,
            'win_rate': (winning / total * 100) if total > 0 else 0,
            'total_pnl': row[3] or 0,
            'total_commission': row[4] or 0,
            'avg_pnl': row[5] or 0,
            'best_trade': row[6] or 0,
            'worst_trade': row[7] or 0,
        }
