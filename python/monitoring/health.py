# Niskala - Health Check
# Health check endpoints for monitoring

import time
import asyncio
from typing import Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class HealthChecker:
    """Health check manager"""
    
    def __init__(self):
        self._checks: Dict[str, callable] = {}
        self._start_time = time.time()
        logger.info("HealthChecker initialized")
    
    def register_check(self, name: str, check_func: callable):
        """Register health check"""
        self._checks[name] = check_func
    
    async def check_health(self) -> Dict:
        """Run all health checks"""
        checks = {}
        overall_status = "healthy"
        
        for name, check_func in self._checks.items():
            try:
                if asyncio.iscoroutinefunction(check_func):
                    result = await check_func()
                else:
                    result = check_func()
                checks[name] = {"status": "healthy", "details": result}
            except Exception as e:
                checks[name] = {"status": "unhealthy", "error": str(e)}
                overall_status = "unhealthy"
        
        uptime = time.time() - self._start_time
        
        return {
            "status": overall_status,
            "version": "1.0.0",
            "uptime_seconds": int(uptime),
            "timestamp": datetime.now().isoformat(),
            "checks": checks,
        }
    
    async def check_database(self) -> Dict:
        """Check database connectivity"""
        try:
            from ..cloud.database import get_db
            db = await get_db()
            result = await db.fetchval("SELECT 1")
            return {"connected": True, "result": result}
        except Exception as e:
            raise Exception(f"Database check failed: {e}")
    
    async def check_redis(self) -> Dict:
        """Check Redis connectivity"""
        try:
            from ..cloud.cache import get_cache
            cache = await get_cache()
            ping = await cache.ping()
            return {"connected": ping}
        except Exception as e:
            raise Exception(f"Redis check failed: {e}")
    
    def check_disk_space(self) -> Dict:
        """Check disk space"""
        import shutil
        total, used, free = shutil.disk_usage("/")
        return {
            "total_gb": round(total / (1024**3), 2),
            "used_gb": round(used / (1024**3), 2),
            "free_gb": round(free / (1024**3), 2),
            "usage_percent": round(used / total * 100, 2),
        }
    
    def check_memory(self) -> Dict:
        """Check memory usage"""
        try:
            import psutil
            mem = psutil.virtual_memory()
            return {
                "total_gb": round(mem.total / (1024**3), 2),
                "available_gb": round(mem.available / (1024**3), 2),
                "usage_percent": mem.percent,
            }
        except ImportError:
            return {"error": "psutil not installed"}
    
    def check_cpu(self) -> Dict:
        """Check CPU usage"""
        try:
            import psutil
            return {
                "percent": psutil.cpu_percent(interval=0.1),
                "count": psutil.cpu_count(),
            }
        except ImportError:
            return {"error": "psutil not installed"}


# Singleton
_health_checker: Optional[HealthChecker] = None


def get_health_checker() -> HealthChecker:
    """Get health checker instance"""
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker()
        # Register default checks
        _health_checker.register_check("database", _health_checker.check_database)
        _health_checker.register_check("redis", _health_checker.check_redis)
        _health_checker.register_check("disk", _health_checker.check_disk_space)
        _health_checker.register_check("memory", _health_checker.check_memory)
        _health_checker.register_check("cpu", _health_checker.check_cpu)
    return _health_checker
