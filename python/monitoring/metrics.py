# Niskala - Prometheus Metrics
# Application metrics for monitoring

import time
from typing import Dict, Optional
from dataclasses import dataclass, field
from collections import defaultdict
from threading import Lock
import logging

logger = logging.getLogger(__name__)


@dataclass
class Metric:
    """Single metric"""
    name: str
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


class PrometheusMetrics:
    """Prometheus-compatible metrics collector"""
    
    def __init__(self):
        self._counters: Dict[str, float] = defaultdict(float)
        self._gauges: Dict[str, float] = {}
        self._histograms: Dict[str, list] = defaultdict(list)
        self._lock = Lock()
        logger.info("PrometheusMetrics initialized")
    
    # Counter methods
    
    def inc_counter(self, name: str, value: float = 1, labels: Optional[Dict] = None):
        """Increment counter"""
        key = self._make_key(name, labels)
        with self._lock:
            self._counters[key] += value
    
    def get_counter(self, name: str, labels: Optional[Dict] = None) -> float:
        """Get counter value"""
        key = self._make_key(name, labels)
        return self._counters.get(key, 0)
    
    # Gauge methods
    
    def set_gauge(self, name: str, value: float, labels: Optional[Dict] = None):
        """Set gauge value"""
        key = self._make_key(name, labels)
        with self._lock:
            self._gauges[key] = value
    
    def inc_gauge(self, name: str, value: float = 1, labels: Optional[Dict] = None):
        """Increment gauge"""
        key = self._make_key(name, labels)
        with self._lock:
            self._gauges[key] = self._gauges.get(key, 0) + value
    
    def dec_gauge(self, name: str, value: float = 1, labels: Optional[Dict] = None):
        """Decrement gauge"""
        key = self._make_key(name, labels)
        with self._lock:
            self._gauges[key] = self._gauges.get(key, 0) - value
    
    def get_gauge(self, name: str, labels: Optional[Dict] = None) -> float:
        """Get gauge value"""
        key = self._make_key(name, labels)
        return self._gauges.get(key, 0)
    
    # Histogram methods
    
    def observe_histogram(self, name: str, value: float, labels: Optional[Dict] = None):
        """Observe histogram value"""
        key = self._make_key(name, labels)
        with self._lock:
            self._histograms[key].append(value)
            # Keep only last 1000 values
            if len(self._histograms[key]) > 1000:
                self._histograms[key] = self._histograms[key][-1000:]
    
    def get_histogram(self, name: str, labels: Optional[Dict] = None) -> Dict:
        """Get histogram stats"""
        key = self._make_key(name, labels)
        values = self._histograms.get(key, [])
        if not values:
            return {"count": 0, "sum": 0, "avg": 0, "min": 0, "max": 0}
        
        return {
            "count": len(values),
            "sum": sum(values),
            "avg": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
        }
    
    # Helper methods
    
    def _make_key(self, name: str, labels: Optional[Dict] = None) -> str:
        """Create metric key"""
        if not labels:
            return name
        label_str = ",".join(f'{k}="{v}"' for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"
    
    def format_prometheus(self) -> str:
        """Format metrics in Prometheus text format"""
        lines = []
        
        # Counters
        for key, value in self._counters.items():
            lines.append(f"# TYPE {key.split('{')[0]} counter")
            lines.append(f"{key} {value}")
        
        # Gauges
        for key, value in self._gauges.items():
            lines.append(f"# TYPE {key.split('{')[0]} gauge")
            lines.append(f"{key} {value}")
        
        # Histograms
        for key, values in self._histograms.items():
            name = key.split('{')[0]
            lines.append(f"# TYPE {name} histogram")
            if values:
                lines.append(f"{name}_count{{{key.split('{')[1] if '{' in key else ''}}} {len(values)}")
                lines.append(f"{name}_sum{{{key.split('{')[1] if '{' in key else ''}}} {sum(values)}")
        
        return "\n".join(lines)
    
    def reset(self):
        """Reset all metrics"""
        with self._lock:
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()


# Pre-defined metrics for Niskala

class NiskalaMetrics:
    """Niskala-specific metrics"""
    
    def __init__(self, metrics: PrometheusMetrics):
        self.m = metrics
    
    def request_started(self, method: str, endpoint: str):
        """Track request started"""
        self.m.inc_counter("niskala_http_requests_total", labels={"method": method, "endpoint": endpoint})
        self.m.inc_gauge("niskala_http_requests_active")
    
    def request_completed(self, method: str, endpoint: str, status: int, duration: float):
        """Track request completed"""
        self.m.dec_gauge("niskala_http_requests_active")
        self.m.inc_counter("niskala_http_requests_completed", labels={"method": method, "endpoint": endpoint, "status": str(status)})
        self.m.observe_histogram("niskala_http_request_duration_seconds", duration, labels={"endpoint": endpoint})
    
    def trade_placed(self, symbol: str, side: str):
        """Track trade placed"""
        self.m.inc_counter("niskala_trades_total", labels={"symbol": symbol, "side": side})
    
    def trade_executed(self, symbol: str, side: str):
        """Track trade executed"""
        self.m.inc_counter("niskala_trades_executed_total", labels={"symbol": symbol, "side": side})
    
    def active_users(self, count: int):
        """Set active users"""
        self.m.set_gauge("niskala_active_users", count)
    
    def database_connections(self, active: int, idle: int):
        """Track database connections"""
        self.m.set_gauge("niskala_db_connections_active", active)
        self.m.set_gauge("niskala_db_connections_idle", idle)
    
    def redis_operations(self, op_type: str):
        """Track Redis operations"""
        self.m.inc_counter("niskala_redis_operations_total", labels={"type": op_type})
    
    def cache_hit(self):
        """Track cache hit"""
        self.m.inc_counter("niskala_cache_hits_total")
    
    def cache_miss(self):
        """Track cache miss"""
        self.m.inc_counter("niskala_cache_misses_total")


# Singleton
_metrics: Optional[PrometheusMetrics] = None
_niskala_metrics: Optional[NiskalaMetrics] = None


def get_metrics() -> PrometheusMetrics:
    """Get metrics instance"""
    global _metrics
    if _metrics is None:
        _metrics = PrometheusMetrics()
    return _metrics


def get_niskala_metrics() -> NiskalaMetrics:
    """Get Niskala metrics instance"""
    global _niskala_metrics
    if _niskala_metrics is None:
        _niskala_metrics = NiskalaMetrics(get_metrics())
    return _niskala_metrics
