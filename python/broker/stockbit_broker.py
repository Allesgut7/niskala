# Niskala - Stockbit Broker Integration
# Stockbit API integration for Indonesian stock trading

import aiohttp
from typing import Dict, Optional, List
import logging

from .base_broker import BaseBroker, BrokerConfig, BrokerStatus

logger = logging.getLogger(__name__)


class StockbitBroker(BaseBroker):
    """Stockbit broker integration
    
    Note: Stockbit API availability is uncertain. This implementation
    provides a structured interface that can be used with:
    - Real Stockbit API (when available)
    - Mock mode for testing
    """
    
    def __init__(self, config: Optional[BrokerConfig] = None):
        if config is None:
            config = BrokerConfig(
                name='stockbit',
                api_url='https://api.stockbit.com',
                sandbox=True,
            )
        super().__init__(config)
        self._session: Optional[aiohttp.ClientSession] = None
        self._access_token: str = ''
        self._user_id: str = ''
    
    async def connect(self, credentials: Dict) -> bool:
        """Connect to Stockbit API
        
        Args:
            credentials: {'username': str, 'password': str} or {'api_token': str}
        
        Returns:
            True if connected
        """
        try:
            self.status = BrokerStatus.CONNECTING
            
            if self.config.sandbox:
                # Mock connection for sandbox
                self._access_token = 'sandbox_token_stockbit'
                self._user_id = 'sandbox_user'
                self._connected = True
                self.status = BrokerStatus.CONNECTED
                logger.info("Connected to Stockbit (sandbox mode)")
                return True
            
            # Real API connection
            self._session = aiohttp.ClientSession()
            
            api_token = credentials.get('api_token')
            if api_token:
                self._access_token = api_token
                self._connected = True
                self.status = BrokerStatus.CONNECTED
                logger.info("Connected to Stockbit API")
                return True
            
            # Login flow
            login_url = f"{self.config.api_url}/v1/auth/login"
            payload = {
                'email': credentials.get('username', ''),
                'password': credentials.get('password', ''),
            }
            
            async with self._session.post(login_url, json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    self._access_token = data.get('token', '')
                    self._user_id = data.get('user_id', '')
                    self._connected = True
                    self.status = BrokerStatus.CONNECTED
                    logger.info("Connected to Stockbit API")
                    return True
                else:
                    self.status = BrokerStatus.ERROR
                    logger.error(f"Stockbit connection failed: {resp.status}")
                    return False
        
        except Exception as e:
            self.status = BrokerStatus.ERROR
            logger.error(f"Stockbit connection error: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from Stockbit"""
        if self._session:
            await self._session.close()
        self._connected = False
        self._access_token = ''
        self.status = BrokerStatus.DISCONNECTED
        logger.info("Disconnected from Stockbit")
    
    async def place_order(self, symbol: str, side: str, quantity: int,
                          order_type: str = 'market',
                          price: Optional[float] = None) -> Dict:
        """Place order through Stockbit"""
        if not self._connected:
            return {'success': False, 'error': 'Not connected'}
        
        if self.config.sandbox:
            # Mock order placement
            import uuid
            order_id = f"SB-{uuid.uuid4().hex[:8].upper()}"
            logger.info(f"Stockbit mock order: {side} {quantity} {symbol}")
            return {
                'success': True,
                'order_id': order_id,
                'broker': 'stockbit',
                'status': 'pending',
            }
        
        # Real API call
        headers = {'Authorization': f'Bearer {self._access_token}'}
        payload = {
            'stock_code': symbol,
            'buy_sell': side.upper(),
            'quantity': quantity,
            'order_type': order_type.upper(),
            'price': price,
        }
        
        async with self._session.post(
            f"{self.config.api_url}/v1/orders",
            json=payload,
            headers=headers,
        ) as resp:
            data = await resp.json()
            if resp.status == 201:
                return {
                    'success': True,
                    'order_id': data.get('order_id'),
                    'broker': 'stockbit',
                    'status': 'pending',
                }
            else:
                return {
                    'success': False,
                    'error': data.get('message', 'Order failed'),
                }
    
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel order"""
        if not self._connected:
            return False
        
        if self.config.sandbox:
            logger.info(f"Stockbit mock cancel: {order_id}")
            return True
        
        headers = {'Authorization': f'Bearer {self._access_token}'}
        async with self._session.delete(
            f"{self.config.api_url}/v1/orders/{order_id}",
            headers=headers,
        ) as resp:
            return resp.status == 200
    
    async def get_positions(self) -> List[Dict]:
        """Get positions"""
        if not self._connected:
            return []
        
        if self.config.sandbox:
            return []
        
        headers = {'Authorization': f'Bearer {self._access_token}'}
        async with self._session.get(
            f"{self.config.api_url}/v1/portfolio",
            headers=headers,
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get('portfolio', [])
            return []
    
    async def get_account(self) -> Dict:
        """Get account info"""
        if not self._connected:
            return {}
        
        if self.config.sandbox:
            return {
                'balance': 100_000_000,
                'equity': 100_000_000,
                'buying_power': 100_000_000,
            }
        
        headers = {'Authorization': f'Bearer {self._access_token}'}
        async with self._session.get(
            f"{self.config.api_url}/v1/account",
            headers=headers,
        ) as resp:
            if resp.status == 200:
                return await resp.json()
            return {}
    
    async def get_order_status(self, order_id: str) -> Dict:
        """Get order status"""
        if not self._connected:
            return {}
        
        if self.config.sandbox:
            return {
                'order_id': order_id,
                'status': 'filled',
                'filled_quantity': 100,
                'average_price': 9500,
            }
        
        headers = {'Authorization': f'Bearer {self._access_token}'}
        async with self._session.get(
            f"{self.config.api_url}/v1/orders/{order_id}",
            headers=headers,
        ) as resp:
            if resp.status == 200:
                return await resp.json()
            return {}
    
    async def get_order_history(self, limit: int = 50) -> List[Dict]:
        """Get order history"""
        if not self._connected:
            return []
        
        if self.config.sandbox:
            return []
        
        headers = {'Authorization': f'Bearer {self._access_token}'}
        params = {'limit': limit}
        async with self._session.get(
            f"{self.config.api_url}/v1/orders",
            headers=headers,
            params=params,
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get('orders', [])
            return []
