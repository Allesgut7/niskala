# Niskala - Fear & Greed Historical Tracking
# Version: 1.0.0
# Track and visualize Fear & Greed Index over time

from typing import Dict, List, Optional
from dataclasses import dataclass
import sqlite3
import json
from datetime import datetime, timedelta
import logging


@dataclass
class FearGreedSnapshot:
    """Single Fear & Greed measurement"""
    timestamp: str
    region: str
    score: int
    status: str
    components: Dict[str, int]
    ihsg_price: float = 0.0
    ihsg_change: float = 0.0


class FearGreedHistory:
    """Historical tracking for Fear & Greed Index"""
    
    def __init__(self, db_path: str = 'data/fear_greed_history.db'):
        self.db_path = db_path
        self._init_db()
        
        logging.info("Fear & Greed history initialized")
    
    def _init_db(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fear_greed_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                region TEXT NOT NULL,
                score INTEGER NOT NULL,
                status TEXT NOT NULL,
                components TEXT,
                ihsg_price REAL DEFAULT 0,
                ihsg_change REAL DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_fg_region_time 
            ON fear_greed_history(region, timestamp)
        ''')
        
        conn.commit()
        conn.close()
    
    def save_snapshot(self, snapshot: FearGreedSnapshot):
        """Save Fear & Greed measurement
        
        Args:
            snapshot: FearGreedSnapshot object
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO fear_greed_history 
            (timestamp, region, score, status, components, ihsg_price, ihsg_change)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            snapshot.timestamp,
            snapshot.region,
            snapshot.score,
            snapshot.status,
            json.dumps(snapshot.components),
            snapshot.ihsg_price,
            snapshot.ihsg_change
        ))
        
        conn.commit()
        conn.close()
        
        logging.debug(f"Saved F&G snapshot: {snapshot.region} = {snapshot.score}")
    
    def save_batch(self, snapshots: List[FearGreedSnapshot]):
        """Save multiple snapshots at once"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for s in snapshots:
            cursor.execute('''
                INSERT INTO fear_greed_history 
                (timestamp, region, score, status, components, ihsg_price, ihsg_change)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                s.timestamp, s.region, s.score, s.status,
                json.dumps(s.components), s.ihsg_price, s.ihsg_change
            ))
        
        conn.commit()
        conn.close()
    
    def get_latest(self, region: str = 'indonesia') -> Optional[FearGreedSnapshot]:
        """Get latest Fear & Greed for a region
        
        Args:
            region: 'indonesia', 'asia', or 'global'
            
        Returns:
            Latest FearGreedSnapshot or None
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT timestamp, region, score, status, components, ihsg_price, ihsg_change
            FROM fear_greed_history
            WHERE region = ?
            ORDER BY timestamp DESC
            LIMIT 1
        ''', (region,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return FearGreedSnapshot(
                timestamp=row[0],
                region=row[1],
                score=row[2],
                status=row[3],
                components=json.loads(row[4]) if row[4] else {},
                ihsg_price=row[5],
                ihsg_change=row[6]
            )
        
        return None
    
    def get_history(
        self,
        region: str = 'indonesia',
        days: int = 30
    ) -> List[FearGreedSnapshot]:
        """Get historical Fear & Greed data
        
        Args:
            region: Region to query
            days: Number of days to look back
            
        Returns:
            List of FearGreedSnapshot objects
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor.execute('''
            SELECT timestamp, region, score, status, components, ihsg_price, ihsg_change
            FROM fear_greed_history
            WHERE region = ? AND timestamp >= ?
            ORDER BY timestamp ASC
        ''', (region, cutoff))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            FearGreedSnapshot(
                timestamp=r[0],
                region=r[1],
                score=r[2],
                status=r[3],
                components=json.loads(r[4]) if r[4] else {},
                ihsg_price=r[5],
                ihsg_change=r[6]
            )
            for r in rows
        ]
    
    def get_all_regions_latest(self) -> Dict[str, FearGreedSnapshot]:
        """Get latest Fear & Greed for all regions
        
        Returns:
            Dict mapping region -> latest snapshot
        """
        regions = ['indonesia', 'asia', 'global']
        result = {}
        
        for region in regions:
            snapshot = self.get_latest(region)
            if snapshot:
                result[region] = snapshot
        
        return result
    
    def get_statistics(self, region: str = 'indonesia', days: int = 30) -> Dict:
        """Get statistics for Fear & Greed over period
        
        Args:
            region: Region to analyze
            days: Number of days
            
        Returns:
            Dict with statistics
        """
        history = self.get_history(region, days)
        
        if not history:
            return {
                'count': 0,
                'avg_score': 0,
                'min_score': 0,
                'max_score': 0,
                'std_score': 0,
                'current_status': 'Unknown',
                'trend': 'Unknown'
            }
        
        scores = [s.score for s in history]
        
        # Calculate trend (last 7 days vs previous 7 days)
        if len(scores) >= 14:
            recent_avg = sum(scores[-7:]) / 7
            previous_avg = sum(scores[-14:-7]) / 7
            
            if recent_avg > previous_avg + 5:
                trend = 'improving'
            elif recent_avg < previous_avg - 5:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'insufficient_data'
        
        return {
            'count': len(scores),
            'avg_score': sum(scores) / len(scores),
            'min_score': min(scores),
            'max_score': max(scores),
            'std_score': (sum((s - sum(scores)/len(scores))**2 for s in scores) / len(scores))**0.5,
            'current_status': history[-1].status,
            'trend': trend
        }
    
    def get_extreme_events(
        self,
        region: str = 'indonesia',
        threshold_low: int = 20,
        threshold_high: int = 80,
        days: int = 90
    ) -> List[FearGreedSnapshot]:
        """Get extreme Fear & Greed events
        
        Args:
            region: Region to query
            threshold_low: Below this is extreme fear
            threshold_high: Above this is extreme greed
            days: Number of days to look back
            
        Returns:
            List of extreme events
        """
        history = self.get_history(region, days)
        
        return [
            s for s in history
            if s.score <= threshold_low or s.score >= threshold_high
        ]


# Test
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    # Create tracker
    tracker = FearGreedHistory(db_path='/tmp/test_fg_history.db')
    
    # Generate sample data
    import numpy as np
    np.random.seed(42)
    
    print("Generating sample Fear & Greed data...")
    
    base_score = 55
    for i in range(30):
        score = int(base_score + np.random.randn() * 15)
        score = max(0, min(100, score))
        
        if score <= 25:
            status = 'Extreme Fear'
        elif score <= 45:
            status = 'Fear'
        elif score <= 55:
            status = 'Neutral'
        elif score <= 75:
            status = 'Greed'
        else:
            status = 'Extreme Greed'
        
        timestamp = (datetime.now() - timedelta(days=30-i)).isoformat()
        
        snapshot = FearGreedSnapshot(
            timestamp=timestamp,
            region='indonesia',
            score=score,
            status=status,
            components={
                'volatility': int(score + np.random.randn() * 10),
                'breadth': int(score + np.random.randn() * 10),
                'momentum': int(score + np.random.randn() * 10),
                'volume': int(score + np.random.randn() * 10),
                'sentiment': int(score + np.random.randn() * 10),
                'safe_haven': int(score + np.random.randn() * 10)
            },
            ihsg_price=7200 + np.random.randn() * 100,
            ihsg_change=np.random.randn() * 1.5
        )
        
        tracker.save_snapshot(snapshot)
    
    # Query data
    print("\n=== Latest Fear & Greed ===")
    latest = tracker.get_latest('indonesia')
    if latest:
        print(f"Score: {latest.score}")
        print(f"Status: {latest.status}")
        print(f"Timestamp: {latest.timestamp}")
    
    print("\n=== Statistics (30 days) ===")
    stats = tracker.get_statistics('indonesia', 30)
    print(f"Average: {stats['avg_score']:.1f}")
    print(f"Min: {stats['min_score']}")
    print(f"Max: {stats['max_score']}")
    print(f"Trend: {stats['trend']}")
    
    print("\n=== History (last 10) ===")
    history = tracker.get_history('indonesia', 30)
    for s in history[-10:]:
        print(f"  {s.timestamp[:10]}: {s.score} ({s.status})")
    
    print("\n=== Extreme Events ===")
    extremes = tracker.get_extreme_events('indonesia', 25, 75, 30)
    for e in extremes:
        print(f"  {e.timestamp[:10]}: {e.score} ({e.status})")
