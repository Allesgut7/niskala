# Niskala - Order Router
# Smart order routing across brokers

from typing import Dict, Optional, List
import logging

from .base_broker import BaseBroker

logger = logging.getLogger(__name__)


class OrderRouter:
    """Smart order routing across multiple brokers"""
    
    def __init__(self):
        self._brokers: Dict[str, BaseBroker] = {}
        self._primary_broker: Optional[str] = None
        logger.info("OrderRouter initialized")
    
    def register_broker(self, name: str, broker: BaseBroker, primary: bool = False):
        """Register a broker
        
        Args:
            name: Broker name
            broker: Broker instance
            primary: Set as primary broker
        """
        self._brokers[name] = broker
        if primary:
            self._primary_broker = name
        logger.info(f"Broker registered: {name} (primary: {primary})")
    
    async def route_order(self, symbol: str, side: str, quantity: int,
                          order_type: str = 'market',
                          price: Optional[float] = None) -> Dict:
        """Route order to best available broker
        
        Args:
            symbol: Stock symbol
            side: 'buy' or 'sell'
            quantity: Number of shares
            order_type: 'market' or 'limit'
            price: Limit price
        
        Returns:
            Order result from selected broker
        """
        # Try primary broker first
        if self._primary_broker:
            broker = self._brokers.get(self._primary_broker)
            if broker and broker._connected:
                try:
                    result = await broker.place_order(
                        symbol, side, quantity, order_type, price
                    )
                    result['broker'] = self._primary_broker
                    return result
                except Exception as e:
                    logger.warning(f"Primary broker failed: {e}")
        
        # Fallback to other brokers
        for name, broker in self._brokers.items():
            if broker._connected and name != self._primary_broker:
                try:
                    result = await broker.place_order(
                        symbol, side, quantity, order_type, price
                    )
                    result['broker'] = name
                    return result
                except Exception as e:
                    logger.warning(f"Broker {name} failed: {e}")
        
        return {'success': False, 'error': 'No broker available'}
    
    async def cancel_order(self, order_id: str, broker_name: str) -> bool:
        """Cancel order through specific broker"""
        broker = self._brokers.get(broker_name)
        if broker:
            return await broker.cancel_order(order_id)
        return False
    
    def get_available_brokers(self) -> List[Dict]:
        """Get list of available brokers"""
        return [
            {
                'name': name,
                'status': broker.status.value,
                'connected': broker._connected,
                'primary': name == self._primary_broker,
            }
            for name, broker in self._brokers.items()
        ]
    
    def get_best_price(self, symbol: str) -> Optional[Dict]:
        """Get best price across brokers"""
        # For now, return None - would need real-time price feeds
        return None
