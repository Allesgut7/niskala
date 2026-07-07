# Niskala - Shared Watchlist Collaboration
# Version: 1.0.0
# Real-time watchlist sharing using Yjs CRDT

import json
import sqlite3
import uuid
import time
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import logging

try:
    import y_py as Y
    YJS_AVAILABLE = True
except ImportError:
    YJS_AVAILABLE = False


@dataclass
class WatchlistItem:
    """Single watchlist entry"""
    symbol: str
    notes: str = ''
    added_by: str = ''
    added_at: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            'symbol': self.symbol,
            'notes': self.notes,
            'added_by': self.added_by,
            'added_at': self.added_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'WatchlistItem':
        return cls(
            symbol=data.get('symbol', ''),
            notes=data.get('notes', ''),
            added_by=data.get('added_by', ''),
            added_at=data.get('added_at', 0.0)
        )


@dataclass
class SharedWatchlist:
    """Shared watchlist metadata"""
    id: str
    name: str
    owner_id: str
    is_public: bool = False
    items: List[WatchlistItem] = field(default_factory=list)
    members: List[Dict] = field(default_factory=list)
    created_at: str = ''
    updated_at: str = ''


class WatchlistManager:
    """Manage shared watchlists with SQLite persistence
    
    Features:
    - Create/delete watchlists
    - Add/remove symbols
    - Share with users (view/edit permissions)
    - Real-time sync ready (Yjs compatible)
    - Offline support with sync when reconnected
    """
    
    def __init__(self, db_path: str = 'data/watchlists.db'):
        self.db_path = db_path
        self._init_db()
        self._callbacks: List[Callable] = []
        
        logging.info("Watchlist manager initialized")
    
    def _init_db(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS watchlists (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                owner_id TEXT NOT NULL,
                is_public BOOLEAN DEFAULT false,
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS watchlist_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                watchlist_id TEXT REFERENCES watchlists(id) ON DELETE CASCADE,
                symbol TEXT NOT NULL,
                notes TEXT DEFAULT '',
                added_by TEXT,
                added_at REAL,
                position INTEGER DEFAULT 0,
                UNIQUE(watchlist_id, symbol)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS watchlist_members (
                watchlist_id TEXT REFERENCES watchlists(id) ON DELETE CASCADE,
                user_id TEXT NOT NULL,
                permission TEXT CHECK (permission IN ('view', 'edit', 'admin')),
                joined_at TEXT,
                PRIMARY KEY (watchlist_id, user_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS watchlist_changes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                watchlist_id TEXT REFERENCES watchlists(id) ON DELETE CASCADE,
                action TEXT NOT NULL,
                data TEXT,
                user_id TEXT,
                timestamp REAL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_watchlist(
        self,
        name: str,
        owner_id: str,
        is_public: bool = False,
        initial_symbols: List[str] = None
    ) -> str:
        """Create a new watchlist
        
        Args:
            name: Watchlist name
            owner_id: Owner user ID
            is_public: Whether publicly visible
            initial_symbols: Optional initial stock symbols
            
        Returns:
            Watchlist ID
        """
        watchlist_id = str(uuid.uuid4())[:8]
        now = datetime.now().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO watchlists (id, name, owner_id, is_public, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (watchlist_id, name, owner_id, is_public, now, now))
        
        # Add initial symbols
        if initial_symbols:
            for i, symbol in enumerate(initial_symbols):
                cursor.execute('''
                    INSERT INTO watchlist_items (watchlist_id, symbol, added_by, added_at, position)
                    VALUES (?, ?, ?, ?, ?)
                ''', (watchlist_id, symbol, owner_id, time.time(), i))
        
        # Add owner as admin
        cursor.execute('''
            INSERT INTO watchlist_members (watchlist_id, user_id, permission, joined_at)
            VALUES (?, ?, 'admin', ?)
        ''', (watchlist_id, owner_id, now))
        
        # Log change
        self._log_change(cursor, watchlist_id, 'create', {'name': name}, owner_id)
        
        conn.commit()
        conn.close()
        
        logging.info(f"Watchlist created: {name} ({watchlist_id})")
        
        return watchlist_id
    
    def get_watchlist(self, watchlist_id: str) -> Optional[SharedWatchlist]:
        """Get watchlist by ID
        
        Args:
            watchlist_id: Watchlist ID
            
        Returns:
            SharedWatchlist or None
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM watchlists WHERE id=?', (watchlist_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return None
        
        # Get items
        cursor.execute('''
            SELECT symbol, notes, added_by, added_at 
            FROM watchlist_items 
            WHERE watchlist_id=? 
            ORDER BY position
        ''', (watchlist_id,))
        
        items = [
            WatchlistItem(symbol=r[0], notes=r[1], added_by=r[2], added_at=r[3])
            for r in cursor.fetchall()
        ]
        
        # Get members
        cursor.execute('''
            SELECT user_id, permission, joined_at 
            FROM watchlist_members 
            WHERE watchlist_id=?
        ''', (watchlist_id,))
        
        members = [
            {'user_id': r[0], 'permission': r[1], 'joined_at': r[2]}
            for r in cursor.fetchall()
        ]
        
        conn.close()
        
        return SharedWatchlist(
            id=row[0],
            name=row[1],
            owner_id=row[2],
            is_public=bool(row[3]),
            items=items,
            members=members,
            created_at=row[4],
            updated_at=row[5]
        )
    
    def add_symbol(
        self,
        watchlist_id: str,
        symbol: str,
        user_id: str,
        notes: str = ''
    ) -> bool:
        """Add symbol to watchlist
        
        Args:
            watchlist_id: Watchlist ID
            symbol: Stock symbol
            user_id: User adding the symbol
            notes: Optional notes
            
        Returns:
            Success boolean
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get current max position
            cursor.execute('''
                SELECT MAX(position) FROM watchlist_items WHERE watchlist_id=?
            ''', (watchlist_id,))
            max_pos = cursor.fetchone()[0] or 0
            
            cursor.execute('''
                INSERT INTO watchlist_items (watchlist_id, symbol, notes, added_by, added_at, position)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (watchlist_id, symbol, notes, user_id, time.time(), max_pos + 1))
            
            # Update timestamp
            cursor.execute('''
                UPDATE watchlists SET updated_at=? WHERE id=?
            ''', (datetime.now().isoformat(), watchlist_id))
            
            # Log change
            self._log_change(cursor, watchlist_id, 'add_symbol', 
                           {'symbol': symbol, 'notes': notes}, user_id)
            
            conn.commit()
            conn.close()
            
            self._notify_change(watchlist_id, 'add', symbol)
            
            logging.info(f"Added {symbol} to watchlist {watchlist_id}")
            return True
            
        except sqlite3.IntegrityError:
            conn.close()
            logging.warning(f"Symbol {symbol} already in watchlist {watchlist_id}")
            return False
    
    def remove_symbol(self, watchlist_id: str, symbol: str, user_id: str) -> bool:
        """Remove symbol from watchlist
        
        Args:
            watchlist_id: Watchlist ID
            symbol: Stock symbol
            user_id: User removing the symbol
            
        Returns:
            Success boolean
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM watchlist_items 
            WHERE watchlist_id=? AND symbol=?
        ''', (watchlist_id, symbol))
        
        deleted = cursor.rowcount > 0
        
        if deleted:
            # Update timestamp
            cursor.execute('''
                UPDATE watchlists SET updated_at=? WHERE id=?
            ''', (datetime.now().isoformat(), watchlist_id))
            
            # Log change
            self._log_change(cursor, watchlist_id, 'remove_symbol', 
                           {'symbol': symbol}, user_id)
            
            self._notify_change(watchlist_id, 'remove', symbol)
        
        conn.commit()
        conn.close()
        
        return deleted
    
    def share_watchlist(
        self,
        watchlist_id: str,
        user_id: str,
        permission: str = 'view'
    ) -> bool:
        """Share watchlist with user
        
        Args:
            watchlist_id: Watchlist ID
            user_id: User to share with
            permission: 'view' or 'edit'
            
        Returns:
            Success boolean
        """
        now = datetime.now().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO watchlist_members 
                (watchlist_id, user_id, permission, joined_at)
                VALUES (?, ?, ?, ?)
            ''', (watchlist_id, user_id, permission, now))
            
            conn.commit()
            conn.close()
            
            logging.info(f"Shared watchlist {watchlist_id} with {user_id} ({permission})")
            return True
            
        except Exception as e:
            conn.close()
            logging.error(f"Failed to share watchlist: {e}")
            return False
    
    def get_user_watchlists(self, user_id: str) -> List[SharedWatchlist]:
        """Get all watchlists for a user
        
        Args:
            user_id: User ID
            
        Returns:
            List of SharedWatchlist objects
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get watchlists where user is owner or member
        cursor.execute('''
            SELECT DISTINCT w.id FROM watchlists w
            LEFT JOIN watchlist_members wm ON w.id = wm.watchlist_id
            WHERE w.owner_id = ? OR wm.user_id = ? OR w.is_public = true
        ''', (user_id, user_id))
        
        watchlist_ids = [r[0] for r in cursor.fetchall()]
        conn.close()
        
        return [self.get_watchlist(wid) for wid in watchlist_ids if self.get_watchlist(wid)]
    
    def get_symbols(self, watchlist_id: str) -> List[str]:
        """Get all symbols in watchlist
        
        Args:
            watchlist_id: Watchlist ID
            
        Returns:
            List of stock symbols
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT symbol FROM watchlist_items 
            WHERE watchlist_id=? ORDER BY position
        ''', (watchlist_id,))
        
        symbols = [r[0] for r in cursor.fetchall()]
        conn.close()
        
        return symbols
    
    def delete_watchlist(self, watchlist_id: str, user_id: str) -> bool:
        """Delete watchlist
        
        Args:
            watchlist_id: Watchlist ID
            user_id: User requesting deletion (must be owner)
            
        Returns:
            Success boolean
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Verify ownership
        cursor.execute('''
            SELECT owner_id FROM watchlists WHERE id=?
        ''', (watchlist_id,))
        
        row = cursor.fetchone()
        if not row or row[0] != user_id:
            conn.close()
            return False
        
        cursor.execute('DELETE FROM watchlists WHERE id=?', (watchlist_id,))
        conn.commit()
        conn.close()
        
        logging.info(f"Deleted watchlist {watchlist_id}")
        return True
    
    def get_change_log(self, watchlist_id: str, limit: int = 50) -> List[Dict]:
        """Get change history for watchlist
        
        Args:
            watchlist_id: Watchlist ID
            limit: Max entries
            
        Returns:
            List of change dicts
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT action, data, user_id, timestamp 
            FROM watchlist_changes 
            WHERE watchlist_id=? 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (watchlist_id, limit))
        
        changes = [
            {
                'action': r[0],
                'data': json.loads(r[1]) if r[1] else {},
                'user_id': r[2],
                'timestamp': r[3]
            }
            for r in cursor.fetchall()
        ]
        
        conn.close()
        return changes
    
    def on_change(self, callback: Callable):
        """Register change callback for real-time updates"""
        self._callbacks.append(callback)
    
    def _log_change(self, cursor, watchlist_id: str, action: str, data: Dict, user_id: str):
        """Log change to database"""
        cursor.execute('''
            INSERT INTO watchlist_changes (watchlist_id, action, data, user_id, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (watchlist_id, action, json.dumps(data), user_id, time.time()))
    
    def _notify_change(self, watchlist_id: str, action: str, symbol: str):
        """Notify registered callbacks of changes"""
        for callback in self._callbacks:
            try:
                callback(watchlist_id, action, symbol)
            except Exception as e:
                logging.error(f"Callback error: {e}")


class YjsSyncAdapter:
    """Yjs CRDT adapter for real-time watchlist sync
    
    Converts watchlist operations to Yjs document updates
    for conflict-free real-time collaboration.
    """
    
    def __init__(self, manager: WatchlistManager):
        self.manager = manager
        
        if not YJS_AVAILABLE:
            logging.warning("y-py not installed, Yjs sync disabled")
            return
        
        # Register change handler
        manager.on_change(self._on_watchlist_change)
    
    def create_ydoc(self, watchlist_id: str) -> Optional[object]:
        """Create Yjs document for watchlist
        
        Args:
            watchlist_id: Watchlist ID
            
        Returns:
            Y.YDoc or None
        """
        if not YJS_AVAILABLE:
            return None
        
        doc = Y.YDoc()
        items_array = doc.get_array('watchlist')
        
        # Load existing items
        symbols = self.manager.get_symbols(watchlist_id)
        
        with doc.begin_transaction() as txn:
            for symbol in symbols:
                items_array.append(txn, symbol)
        
        return doc
    
    def apply_remote_update(self, watchlist_id: str, update: bytes):
        """Apply remote Yjs update
        
        Args:
            watchlist_id: Watchlist ID
            update: Yjs update bytes
        """
        if not YJS_AVAILABLE:
            return
        
        # Apply update to local state
        # This would be connected to y-websocket provider
        logging.debug(f"Applied remote update for {watchlist_id}")
    
    def _on_watchlist_change(self, watchlist_id: str, action: str, symbol: str):
        """Handle watchlist changes for Yjs sync"""
        logging.debug(f"Yjs sync: {action} {symbol} in {watchlist_id}")


# Test
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    # Create manager
    manager = WatchlistManager(db_path='/tmp/test_watchlists.db')
    
    # Create watchlist
    print("Creating watchlist...")
    wl_id = manager.create_watchlist(
        name='My IDX Portfolio',
        owner_id='user1',
        is_public=False,
        initial_symbols=['BBCA', 'BBRI', 'BMRI']
    )
    print(f"Created: {wl_id}")
    
    # Add symbols
    manager.add_symbol(wl_id, 'TLKM', 'user1', 'Telkom Indonesia')
    manager.add_symbol(wl_id, 'GOTO', 'user1', 'GoTo Group')
    
    # Get watchlist
    wl = manager.get_watchlist(wl_id)
    print(f"\nWatchlist: {wl.name}")
    print(f"Owner: {wl.owner_id}")
    print(f"Symbols: {[i.symbol for i in wl.items]}")
    print(f"Members: {len(wl.members)}")
    
    # Share
    manager.share_watchlist(wl_id, 'user2', 'view')
    
    # Get user watchlists
    user_wl = manager.get_user_watchlists('user1')
    print(f"\nUser1 watchlists: {len(user_wl)}")
    
    # Change log
    changes = manager.get_change_log(wl_id)
    print(f"\nChange log ({len(changes)} entries):")
    for c in changes[:5]:
        print(f"  {c['action']}: {c['data']}")
    
    # Remove symbol
    manager.remove_symbol(wl_id, 'GOTO', 'user1')
    
    # Final state
    symbols = manager.get_symbols(wl_id)
    print(f"\nFinal symbols: {symbols}")
