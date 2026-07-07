# Niskala - Pattern Alert System
# Version: 1.0.0
# Detect and notify when patterns are detected

from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
import sqlite3
import json
import logging
from datetime import datetime

from .pattern_recognition import PatternDetector, PatternResult


@dataclass
class PatternAlert:
    """Pattern alert configuration"""
    id: Optional[str] = None
    symbol: str = ''
    pattern_name: str = ''
    min_confidence: float = 60.0
    signal_filter: str = 'any'  # 'bullish', 'bearish', 'any'
    enabled: bool = True
    created_at: str = ''


class PatternAlertManager:
    """Manage pattern detection alerts"""
    
    def __init__(self, db_path: str = 'data/pattern_alerts.db'):
        self.db_path = db_path
        self.detector = PatternDetector()
        self._callbacks: List[Callable] = []
        self._init_db()
        
        logging.info("Pattern alert manager initialized")
    
    def _init_db(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pattern_alerts (
                id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                pattern_name TEXT DEFAULT '',
                min_confidence REAL DEFAULT 60.0,
                signal_filter TEXT DEFAULT 'any',
                enabled BOOLEAN DEFAULT true,
                created_at TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pattern_alert_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_id TEXT,
                symbol TEXT,
                pattern_name TEXT,
                signal TEXT,
                confidence REAL,
                triggered_at TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_alert(
        self,
        symbol: str,
        pattern_name: str = '',
        min_confidence: float = 60.0,
        signal_filter: str = 'any'
    ) -> str:
        """Create pattern alert
        
        Args:
            symbol: Stock symbol
            pattern_name: Specific pattern to watch, or '' for all
            min_confidence: Minimum confidence threshold
            signal_filter: 'bullish', 'bearish', or 'any'
            
        Returns:
            Alert ID
        """
        import uuid
        alert_id = str(uuid.uuid4())[:8]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO pattern_alerts 
            (id, symbol, pattern_name, min_confidence, signal_filter, enabled, created_at)
            VALUES (?, ?, ?, ?, ?, true, ?)
        ''', (alert_id, symbol, pattern_name, min_confidence, signal_filter, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        logging.info(f"Created pattern alert: {symbol} ({alert_id})")
        
        return alert_id
    
    def delete_alert(self, alert_id: str) -> bool:
        """Delete pattern alert"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM pattern_alerts WHERE id=?', (alert_id,))
        deleted = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        return deleted
    
    def list_alerts(self, symbol: Optional[str] = None) -> List[PatternAlert]:
        """List all alerts
        
        Args:
            symbol: Optional filter by symbol
            
        Returns:
            List of PatternAlert objects
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if symbol:
            cursor.execute('SELECT * FROM pattern_alerts WHERE symbol=?', (symbol,))
        else:
            cursor.execute('SELECT * FROM pattern_alerts')
        
        alerts = [
            PatternAlert(
                id=r[0],
                symbol=r[1],
                pattern_name=r[2],
                min_confidence=r[3],
                signal_filter=r[4],
                enabled=bool(r[5]),
                created_at=r[6]
            )
            for r in cursor.fetchall()
        ]
        
        conn.close()
        return alerts
    
    def check_patterns(self, symbol: str, price_data) -> List[Dict]:
        """Check for pattern matches and trigger alerts
        
        Args:
            symbol: Stock symbol
            price_data: DataFrame with OHLC data
            
        Returns:
            List of triggered alert dicts
        """
        # Detect patterns
        patterns = self.detector.detect(price_data)
        
        # Get alerts for this symbol
        alerts = self.list_alerts(symbol)
        active_alerts = [a for a in alerts if a.enabled]
        
        triggered = []
        
        for pattern in patterns:
            for alert in active_alerts:
                # Check pattern name filter
                if alert.pattern_name and alert.pattern_name.lower() not in pattern.pattern_name.lower():
                    continue
                
                # Check confidence threshold
                if pattern.confidence < alert.min_confidence:
                    continue
                
                # Check signal filter
                if alert.signal_filter != 'any' and pattern.signal != alert.signal_filter:
                    continue
                
                # Alert triggered!
                triggered.append({
                    'alert_id': alert.id,
                    'symbol': symbol,
                    'pattern': pattern.pattern_name,
                    'signal': pattern.signal,
                    'confidence': pattern.confidence,
                    'description': pattern.description,
                    'triggered_at': datetime.now().isoformat()
                })
                
                # Log to history
                self._log_trigger(alert.id, symbol, pattern)
                
                # Notify callbacks
                for callback in self._callbacks:
                    try:
                        callback(triggered[-1])
                    except Exception as e:
                        logging.error(f"Alert callback error: {e}")
        
        if triggered:
            logging.info(f"Triggered {len(triggered)} alerts for {symbol}")
        
        return triggered
    
    def on_alert(self, callback: Callable):
        """Register alert callback"""
        self._callbacks.append(callback)
    
    def _log_trigger(self, alert_id: str, symbol: str, pattern: PatternResult):
        """Log triggered alert to history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO pattern_alert_history 
            (alert_id, symbol, pattern_name, signal, confidence, triggered_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (alert_id, symbol, pattern.pattern_name, pattern.signal, 
              pattern.confidence, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_alert_history(self, symbol: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """Get alert trigger history
        
        Args:
            symbol: Optional filter by symbol
            limit: Max entries
            
        Returns:
            List of alert history dicts
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if symbol:
            cursor.execute('''
                SELECT * FROM pattern_alert_history 
                WHERE symbol=? ORDER BY triggered_at DESC LIMIT ?
            ''', (symbol, limit))
        else:
            cursor.execute('''
                SELECT * FROM pattern_alert_history 
                ORDER BY triggered_at DESC LIMIT ?
            ''', (limit,))
        
        history = [
            {
                'id': r[0],
                'alert_id': r[1],
                'symbol': r[2],
                'pattern': r[3],
                'signal': r[4],
                'confidence': r[5],
                'triggered_at': r[6]
            }
            for r in cursor.fetchall()
        ]
        
        conn.close()
        return history


# Test
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    import pandas as pd
    import numpy as np
    
    # Create alert manager
    manager = PatternAlertManager(db_path='/tmp/test_pattern_alerts.db')
    
    # Create alerts
    print("Creating pattern alerts...")
    
    alert1 = manager.create_alert('BBRI', min_confidence=70.0, signal_filter='bullish')
    print(f"Created alert: {alert1}")
    
    alert2 = manager.create_alert('BBCA', pattern_name='Engulfing', min_confidence=65.0)
    print(f"Created alert: {alert2}")
    
    # List alerts
    print("\n=== Active Alerts ===")
    for alert in manager.list_alerts():
        print(f"  {alert.id}: {alert.symbol} - {alert.pattern_name or 'All patterns'} "
              f"({alert.signal_filter}, min_conf={alert.min_confidence}%)")
    
    # Generate sample data
    np.random.seed(42)
    dates = pd.date_range('2023-06-01', '2024-01-01', freq='D')
    close = 4500 + np.cumsum(np.random.randn(len(dates)) * 30)
    
    price_data = pd.DataFrame({
        'open': close * (1 + np.random.randn(len(dates)) * 0.005),
        'high': close * (1 + abs(np.random.randn(len(dates)) * 0.01)),
        'low': close * (1 - abs(np.random.randn(len(dates)) * 0.01)),
        'close': close,
        'volume': np.random.randint(1000000, 5000000, len(dates))
    }, index=dates)
    
    # Check patterns
    print("\n=== Checking Patterns for BBRI ===")
    triggered = manager.check_patterns('BBRI', price_data)
    
    if triggered:
        print(f"Triggered {len(triggered)} alerts:")
        for t in triggered:
            print(f"  {t['pattern']} ({t['signal']}) - Confidence: {t['confidence']}%")
    else:
        print("No alerts triggered")
    
    # Alert history
    print("\n=== Alert History ===")
    history = manager.get_alert_history()
    for h in history[:5]:
        print(f"  {h['symbol']}: {h['pattern']} ({h['signal']}) - {h['triggered_at'][:19]}")
