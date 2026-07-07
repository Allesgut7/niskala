# Niskala - Base Broker Interface
# Abstract broker interface for Indonesian brokers

from abc import ABC, abstractmethod
from typing import Dict, Optional, List
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class BrokerStatus(Enum):
    DISCONNECTED = 'disconnected'
    CONNECTING = 'connecting'
    CONNECTED = 'connected'
    ERROR = 'error'


@dataclass
class BrokerConfig:
    """Broker configuration"""
    name: str
    api_url: str
    api_key: str = ''
    api_secret: str = ''
    access_token: str = ''
    sandbox: bool = True


class BaseBroker(ABC):
    """Abstract base class for broker integrations"""
    
    def __init__(self, config: BrokerConfig):
        self.config = config
        self.status = BrokerStatus.DISCONNECTED
        self._connected = False
        logger.info(f"Broker initialized: {config.name}")
    
    @abstractmethod
    async def connect(self, credentials: Dict) -> bool:
        """Connect to broker
        
        Args:
            credentials: Authentication credentials
        
        Returns:
            True if connected successfully
        """
        pass
    
    @abstractmethod
    async def disconnect(self):
        """Disconnect from broker"""
        pass
    
    @abstractmethod
    async def place_order(self, symbol: str, side: str, quantity: int,
                          order_type: str = 'market',
                          price: Optional[float] = None) -> Dict:
        """Place an order
        
        Args:
            symbol: Stock symbol
            side: 'buy' or 'sell'
            quantity: Number of shares
            order_type: 'market' or 'limit'
            price: Limit price
        
        Returns:
            Order result dict
        """
        pass
    
    @abstractmethod
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an order
        
        Args:
            order_id: Order ID
        
        Returns:
            True if cancelled successfully
        """
        pass
    
    @abstractmethod
    async def get_positions(self) -> List[Dict]:
        """Get current positions
        
        Returns:
            List of position dicts
        """
        pass
    
    @abstractmethod
    async def get_account(self) -> Dict:
        """Get account information
        
        Returns:
            Account info dict
        """
        pass
    
    @abstractmethod
    async def get_order_status(self, order_id: str) -> Dict:
        """Get order status
        
        Args:
            order_id: Order ID
        
        Returns:
            Order status dict
        """
        pass
    
    @abstractmethod
    async def get_order_history(self, limit: int = 50) -> List[Dict]:
        """Get order history
        
        Args:
            limit: Maximum number of orders
        
        Returns:
            List of order dicts
        """
        pass
    
    def get_status(self) -> Dict:
        """Get broker status"""
        return {
            'name': self.config.name,
            'status': self.status.value,
            'connected': self._connected,
            'sandbox': self.config.sandbox,
        }
