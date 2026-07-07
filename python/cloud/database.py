# Niskala - Database Connection Pool
# PostgreSQL async connection management

import asyncio
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager
import logging

try:
    import asyncpg
    HAS_ASYNCPG = True
except ImportError:
    HAS_ASYNCPG = False

try:
    import psycopg2
    import psycopg2.extras
    HAS_PSYCOPG = True
except ImportError:
    HAS_PSYCOPG = False

from .config import get_config

logger = logging.getLogger(__name__)


class DatabasePool:
    """PostgreSQL connection pool manager"""
    
    def __init__(self, dsn: Optional[str] = None):
        self.config = get_config()
        self.dsn = dsn or self.config.DATABASE_URL
        self._pool: Optional[Any] = None
        self._sync_conn: Optional[Any] = None
        logger.info(f"DatabasePool initialized: {self.dsn.split('@')[-1] if '@' in self.dsn else 'local'}")
    
    async def connect(self):
        """Create async connection pool"""
        if not HAS_ASYNCPG:
            logger.warning("asyncpg not installed, using sync fallback")
            return
        
        try:
            self._pool = await asyncpg.create_pool(
                self.dsn,
                min_size=2,
                max_size=self.config.DATABASE_POOL_SIZE,
                max_inactive_connection_lifetime=300,
                command_timeout=60,
            )
            logger.info(f"PostgreSQL pool connected (size: {self.config.DATABASE_POOL_SIZE})")
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise
    
    async def disconnect(self):
        """Close connection pool"""
        if self._pool:
            await self._pool.close()
            logger.info("PostgreSQL pool disconnected")
    
    @asynccontextmanager
    async def acquire(self):
        """Acquire a connection from the pool"""
        if self._pool:
            async with self._pool.acquire() as conn:
                yield conn
        else:
            # Fallback to sync
            conn = self._get_sync_connection()
            try:
                yield conn
            finally:
                pass
    
    async def execute(self, query: str, *args) -> str:
        """Execute a query"""
        async with self.acquire() as conn:
            return await conn.execute(query, *args)
    
    async def fetch(self, query: str, *args) -> List:
        """Fetch multiple rows"""
        async with self.acquire() as conn:
            return await conn.fetch(query, *args)
    
    async def fetchrow(self, query: str, *args) -> Optional[Any]:
        """Fetch a single row"""
        async with self.acquire() as conn:
            return await conn.fetchrow(query, *args)
    
    async def fetchval(self, query: str, *args) -> Any:
        """Fetch a single value"""
        async with self.acquire() as conn:
            return await conn.fetchval(query, *args)
    
    def _get_sync_connection(self):
        """Get synchronous connection (fallback)"""
        if not HAS_PSYCOPG:
            raise RuntimeError("No PostgreSQL driver available")
        
        if self._sync_conn is None or self._sync_conn.closed:
            self._sync_conn = psycopg2.connect(self.dsn)
            self._sync_conn.autocommit = True
        
        return self._sync_conn
    
    def execute_sync(self, query: str, params: tuple = None) -> Any:
        """Execute query synchronously"""
        conn = self._get_sync_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute(query, params)
            if cursor.description:
                return cursor.fetchall()
            conn.commit()
            return None
        except Exception:
            conn.rollback()
            raise
    
    async def init_db(self):
        """Initialize database schema"""
        schema = """
        -- Tenants
        CREATE TABLE IF NOT EXISTS tenants (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR(255) NOT NULL,
            slug VARCHAR(100) UNIQUE NOT NULL,
            plan VARCHAR(50) DEFAULT 'free',
            status VARCHAR(50) DEFAULT 'active',
            settings JSONB DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Users
        CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
            email VARCHAR(255) UNIQUE NOT NULL,
            name VARCHAR(255) NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            role VARCHAR(50) DEFAULT 'viewer',
            status VARCHAR(50) DEFAULT 'active',
            mfa_enabled BOOLEAN DEFAULT false,
            last_login TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Watchlists
        CREATE TABLE IF NOT EXISTS watchlists (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID REFERENCES users(id) ON DELETE CASCADE,
            name VARCHAR(255) NOT NULL,
            symbols TEXT[] DEFAULT '{}',
            is_default BOOLEAN DEFAULT false,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Price Alerts
        CREATE TABLE IF NOT EXISTS price_alerts (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID REFERENCES users(id) ON DELETE CASCADE,
            symbol VARCHAR(20) NOT NULL,
            target_price NUMERIC(15,2) NOT NULL,
            condition VARCHAR(10) NOT NULL CHECK (condition IN ('above', 'below')),
            is_active BOOLEAN DEFAULT true,
            triggered_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Paper Trading Orders
        CREATE TABLE IF NOT EXISTS paper_orders (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID REFERENCES users(id) ON DELETE CASCADE,
            symbol VARCHAR(20) NOT NULL,
            side VARCHAR(10) NOT NULL CHECK (side IN ('buy', 'sell')),
            quantity INTEGER NOT NULL,
            order_type VARCHAR(20) NOT NULL CHECK (order_type IN ('market', 'limit')),
            price NUMERIC(15,2),
            status VARCHAR(20) DEFAULT 'pending',
            filled_quantity INTEGER DEFAULT 0,
            fill_price NUMERIC(15,2),
            commission NUMERIC(15,2) DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            filled_at TIMESTAMP
        );

        -- Paper Trading Positions
        CREATE TABLE IF NOT EXISTS paper_positions (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID REFERENCES users(id) ON DELETE CASCADE,
            symbol VARCHAR(20) NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 0,
            avg_price NUMERIC(15,2) NOT NULL DEFAULT 0,
            total_cost NUMERIC(15,2) NOT NULL DEFAULT 0,
            realized_pnl NUMERIC(15,2) DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, symbol)
        );

        -- Paper Trading Portfolio
        CREATE TABLE IF NOT EXISTS paper_portfolio (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
            cash NUMERIC(15,2) NOT NULL DEFAULT 100000000,
            initial_capital NUMERIC(15,2) NOT NULL DEFAULT 100000000,
            total_realized_pnl NUMERIC(15,2) DEFAULT 0,
            total_commission NUMERIC(15,2) DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Trade History
        CREATE TABLE IF NOT EXISTS trade_history (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID REFERENCES users(id) ON DELETE CASCADE,
            order_id UUID REFERENCES paper_orders(id),
            symbol VARCHAR(20) NOT NULL,
            side VARCHAR(10) NOT NULL,
            quantity INTEGER NOT NULL,
            price NUMERIC(15,2) NOT NULL,
            value NUMERIC(15,2) NOT NULL,
            commission NUMERIC(15,2) NOT NULL,
            pnl NUMERIC(15,2) DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- API Usage Tracking
        CREATE TABLE IF NOT EXISTS api_usage (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID REFERENCES users(id) ON DELETE CASCADE,
            endpoint VARCHAR(255) NOT NULL,
            method VARCHAR(10) NOT NULL,
            status_code INTEGER,
            response_time_ms INTEGER,
            ip_address INET,
            user_agent TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Indexes
        CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
        CREATE INDEX IF NOT EXISTS idx_users_tenant ON users(tenant_id);
        CREATE INDEX IF NOT EXISTS idx_watchlists_user ON watchlists(user_id);
        CREATE INDEX IF NOT EXISTS idx_alerts_user ON price_alerts(user_id);
        CREATE INDEX IF NOT EXISTS idx_alerts_symbol ON price_alerts(symbol);
        CREATE INDEX IF NOT EXISTS idx_orders_user ON paper_orders(user_id);
        CREATE INDEX IF NOT EXISTS idx_orders_symbol ON paper_orders(symbol);
        CREATE INDEX IF NOT EXISTS idx_positions_user ON paper_positions(user_id);
        CREATE INDEX IF NOT EXISTS idx_trades_user ON trade_history(user_id);
        CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trade_history(symbol);
        CREATE INDEX IF NOT EXISTS idx_usage_user ON api_usage(user_id);
        CREATE INDEX IF NOT EXISTS idx_usage_created ON api_usage(created_at);
        """
        
        async with self.acquire() as conn:
            await conn.execute(schema)
        logger.info("Database schema initialized")


# Singleton
_db_pool: Optional[DatabasePool] = None


async def get_db() -> DatabasePool:
    """Get database pool instance"""
    global _db_pool
    if _db_pool is None:
        _db_pool = DatabasePool()
        await _db_pool.connect()
    return _db_pool


async def close_db():
    """Close database pool"""
    global _db_pool
    if _db_pool:
        await _db_pool.disconnect()
        _db_pool = None
