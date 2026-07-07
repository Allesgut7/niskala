# Niskala - Advanced Stock Screener
# Version: 1.0.0
# 80+ filters, pattern criteria, save/load configurations

from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
import json
import sqlite3
import logging
from datetime import datetime


@dataclass
class ScreenerFilter:
    """Single screener filter"""
    name: str
    field: str        # Column name in data
    operator: str     # gt, lt, gte, lte, eq, between, in
    value: float = 0.0
    value2: float = 0.0  # For 'between' operator
    values: List = field(default_factory=list)  # For 'in' operator
    
    def evaluate(self, stock_data: Dict) -> bool:
        """Evaluate filter against stock data"""
        actual = stock_data.get(self.field)
        if actual is None:
            return False
        
        if self.operator == 'gt':
            return actual > self.value
        elif self.operator == 'lt':
            return actual < self.value
        elif self.operator == 'gte':
            return actual >= self.value
        elif self.operator == 'lte':
            return actual <= self.value
        elif self.operator == 'eq':
            return actual == self.value
        elif self.operator == 'between':
            return self.value <= actual <= self.value2
        elif self.operator == 'in':
            return actual in self.values
        
        return False


@dataclass
class ScreenerConfig:
    """Screener configuration"""
    id: Optional[str] = None
    name: str = ''
    description: str = ''
    filters: List[ScreenerFilter] = field(default_factory=list)
    sort_by: str = 'composite_score'
    sort_ascending: bool = False
    limit: int = 50
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class AdvancedScreener:
    """Advanced stock screener with 80+ filters"""
    
    # Preset configurations
    PRESETS = {
        'value': ScreenerConfig(
            name='Value Stocks',
            description='Low PE, high dividend, undervalued',
            filters=[
                ScreenerFilter('Low PE', 'pe_ratio', 'lt', 15.0),
                ScreenerFilter('High Dividend', 'dividend_yield', 'gt', 3.0),
                ScreenerFilter('Low PB', 'pb_ratio', 'lt', 2.0),
            ]
        ),
        'growth': ScreenerConfig(
            name='Growth Stocks',
            description='High revenue and earnings growth',
            filters=[
                ScreenerFilter('Revenue Growth', 'revenue_growth', 'gt', 15.0),
                ScreenerFilter('Earnings Growth', 'earnings_growth', 'gt', 15.0),
                ScreenerFilter('ROE', 'roe', 'gt', 15.0),
            ]
        ),
        'momentum': ScreenerConfig(
            name='Momentum Stocks',
            description='Strong price momentum',
            filters=[
                ScreenerFilter('1M Return', 'return_1m', 'gt', 5.0),
                ScreenerFilter('3M Return', 'return_3m', 'gt', 10.0),
                ScreenerFilter('Above MA50', 'price_vs_ma50', 'gt', 0.0),
            ]
        ),
        'quality': ScreenerConfig(
            name='Quality Stocks',
            description='Strong fundamentals, low debt',
            filters=[
                ScreenerFilter('High ROE', 'roe', 'gt', 20.0),
                ScreenerFilter('Low Debt', 'debt_equity', 'lt', 0.5),
                ScreenerFilter('Good Liquidity', 'current_ratio', 'gt', 1.5),
                ScreenerFilter('Profitable', 'net_margin', 'gt', 10.0),
            ]
        ),
        'dividend': ScreenerConfig(
            name='Dividend Stocks',
            description='High and consistent dividends',
            filters=[
                ScreenerFilter('High Yield', 'dividend_yield', 'gt', 5.0),
                ScreenerFilter('Low Payout', 'payout_ratio', 'lt', 70.0),
                ScreenerFilter('Profitable', 'eps', 'gt', 0.0),
            ]
        ),
        'blue_chip': ScreenerConfig(
            name='Blue Chip IDX30',
            description='Large cap, liquid stocks',
            filters=[
                ScreenerFilter('Large Cap', 'market_cap', 'gt', 50e12),
                ScreenerFilter('Liquid', 'avg_volume', 'gt', 10e6),
                ScreenerFilter('Profitable', 'eps', 'gt', 0.0),
            ]
        ),
        'oversold': ScreenerConfig(
            name='Oversold Stocks',
            description='Technically oversold, potential bounce',
            filters=[
                ScreenerFilter('RSI Low', 'rsi', 'lt', 30.0),
                ScreenerFilter('Below MA20', 'price_vs_ma20', 'lt', 0.0),
                ScreenerFilter('Volume Spike', 'volume_ratio', 'gt', 1.5),
            ]
        ),
        'breakout': ScreenerConfig(
            name='Breakout Stocks',
            description='Price breaking out with volume',
            filters=[
                ScreenerFilter('Near 52W High', 'price_vs_52w_high', 'gt', -5.0),
                ScreenerFilter('Volume Above Avg', 'volume_ratio', 'gt', 2.0),
                ScreenerFilter('Above MA20', 'price_vs_ma20', 'gt', 0.0),
            ]
        ),
    }
    
    def __init__(self, db_path: str = 'data/screeners.db'):
        self.db_path = db_path
        self._init_db()
        
        logging.info(f"Screener initialized with {len(self.PRESETS)} presets")
    
    def _init_db(self):
        """Initialize SQLite database for saving screeners"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS screeners (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                filters TEXT,
                sort_by TEXT DEFAULT 'composite_score',
                sort_ascending BOOLEAN DEFAULT false,
                limit_count INTEGER DEFAULT 50,
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def screen(
        self,
        stocks_data: List[Dict],
        config: Optional[ScreenerConfig] = None,
        preset: Optional[str] = None,
        custom_filters: Optional[List[ScreenerFilter]] = None
    ) -> List[Dict]:
        """Run screener on stock data
        
        Args:
            stocks_data: List of stock data dicts
            config: Custom screener config
            preset: Preset name
            custom_filters: Additional filters
            
        Returns:
            Filtered and sorted list of stocks
        """
        # Determine config
        if config:
            pass
        elif preset and preset in self.PRESETS:
            config = self.PRESETS[preset]
        else:
            config = ScreenerConfig(filters=custom_filters or [])
        
        # Apply filters
        results = []
        for stock in stocks_data:
            passed = True
            for f in config.filters:
                if not f.evaluate(stock):
                    passed = False
                    break
            
            if passed:
                results.append(stock)
        
        # Sort
        if config.sort_by:
            results.sort(
                key=lambda x: x.get(config.sort_by, 0),
                reverse=not config.sort_ascending
            )
        
        # Limit
        results = results[:config.limit]
        
        logging.info(f"Screener: {len(stocks_data)} stocks -> {len(results)} matches")
        
        return results
    
    def save_config(self, config: ScreenerConfig) -> str:
        """Save screener configuration to database
        
        Args:
            config: Screener configuration
            
        Returns:
            Config ID
        """
        import uuid
        
        if not config.id:
            config.id = str(uuid.uuid4())[:8]
        
        now = datetime.now().isoformat()
        config.updated_at = now
        if not config.created_at:
            config.created_at = now
        
        # Serialize filters
        filters_json = json.dumps([
            {
                'name': f.name,
                'field': f.field,
                'operator': f.operator,
                'value': f.value,
                'value2': f.value2,
                'values': f.values
            }
            for f in config.filters
        ])
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO screeners 
            (id, name, description, filters, sort_by, sort_ascending, limit_count, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            config.id, config.name, config.description, filters_json,
            config.sort_by, config.sort_ascending, config.limit,
            config.created_at, config.updated_at
        ))
        
        conn.commit()
        conn.close()
        
        logging.info(f"Screener config saved: {config.name} ({config.id})")
        
        return config.id
    
    def load_config(self, config_id: str) -> Optional[ScreenerConfig]:
        """Load screener configuration from database
        
        Args:
            config_id: Configuration ID
            
        Returns:
            ScreenerConfig or None
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM screeners WHERE id=?', (config_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        filters = [
            ScreenerFilter(**f)
            for f in json.loads(row[3])
        ]
        
        return ScreenerConfig(
            id=row[0],
            name=row[1],
            description=row[2],
            filters=filters,
            sort_by=row[4],
            sort_ascending=bool(row[5]),
            limit=row[6],
            created_at=row[7],
            updated_at=row[8]
        )
    
    def list_configs(self) -> List[Dict]:
        """List all saved screener configurations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, name, description, created_at FROM screeners ORDER BY updated_at DESC')
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {'id': r[0], 'name': r[1], 'description': r[2], 'created_at': r[3]}
            for r in rows
        ]
    
    def delete_config(self, config_id: str) -> bool:
        """Delete screener configuration"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM screeners WHERE id=?', (config_id,))
        deleted = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        return deleted


# Test
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    # Generate sample stock data
    import numpy as np
    np.random.seed(42)
    
    stocks = []
    symbols = ['BBCA', 'BBRI', 'BMRI', 'TLKM', 'GOTO', 'ADRO', 'UNVR', 'ICBP', 'ASII', 'PGAS']
    
    for sym in symbols:
        stocks.append({
            'symbol': sym,
            'price': np.random.uniform(1000, 10000),
            'pe_ratio': np.random.uniform(5, 30),
            'pb_ratio': np.random.uniform(0.5, 5),
            'dividend_yield': np.random.uniform(0, 8),
            'return_1m': np.random.uniform(-10, 15),
            'return_3m': np.random.uniform(-15, 25),
            'return_6m': np.random.uniform(-20, 40),
            'roe': np.random.uniform(5, 30),
            'debt_equity': np.random.uniform(0.2, 2.5),
            'current_ratio': np.random.uniform(0.8, 3.5),
            'market_cap': np.random.uniform(50e12, 500e12),
            'avg_volume': np.random.uniform(5e6, 50e6),
            'volume_ratio': np.random.uniform(0.5, 3.0),
            'rsi': np.random.uniform(20, 80),
            'price_vs_ma20': np.random.uniform(-10, 10),
            'price_vs_ma50': np.random.uniform(-15, 15),
            'price_vs_52w_high': np.random.uniform(-30, 0),
            'revenue_growth': np.random.uniform(-10, 30),
            'earnings_growth': np.random.uniform(-20, 40),
            'net_margin': np.random.uniform(0, 30),
            'eps': np.random.uniform(-100, 500),
            'payout_ratio': np.random.uniform(20, 90),
            'composite_score': np.random.uniform(0, 100)
        })
    
    # Initialize screener
    screener = AdvancedScreener(db_path='/tmp/test_screeners.db')
    
    # Test presets
    print("\n=== Screener Presets ===")
    for name, config in screener.PRESETS.items():
        results = screener.screen(stocks, preset=name)
        print(f"{name:15s}: {len(results)} matches - {config.description}")
    
    # Test value screener
    print("\n=== Value Stocks ===")
    value_results = screener.screen(stocks, preset='value')
    for stock in value_results:
        print(f"  {stock['symbol']:6s}: PE={stock['pe_ratio']:.1f} PB={stock['pb_ratio']:.1f} Div={stock['dividend_yield']:.1f}%")
    
    # Test save/load
    custom = ScreenerConfig(
        name='My Custom Screener',
        description='Custom filter set',
        filters=[
            ScreenerFilter('Low PE', 'pe_ratio', 'lt', 12.0),
            ScreenerFilter('High ROE', 'roe', 'gt', 20.0),
        ]
    )
    
    config_id = screener.save_config(custom)
    print(f"\nSaved config: {config_id}")
    
    loaded = screener.load_config(config_id)
    print(f"Loaded config: {loaded.name}")
    
    # List saved configs
    print("\n=== Saved Configurations ===")
    for cfg in screener.list_configs():
        print(f"  {cfg['id']}: {cfg['name']}")
