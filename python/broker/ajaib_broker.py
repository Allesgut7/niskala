# Niskala - Ajaib Broker Integration
# Ajaib API integration for Indonesian stock trading

import aiohttp
import hashlib
import hmac
import time
from typing import Dict, Optional, List
import logging

from .base_broker import BaseBroker, BrokerConfig, BrokerStatus

logger = logging.getLogger(__name__)


class AjaibBroker(BaseBroker):
    """Ajaib broker integration
    
    Note: Ajaib API availability is uncertain. This implementation
    provides a structured interface that can be used with:
    - Real Ajaib API (when available)
    - Mock mode for testing
    """
    
    def __init__(self, config: Optional[BrokerConfig] = None):
        if config is None:
            config = BrokerConfig(
                name='ajaib',
                api_url='https://api.ajaib.co.id',
                sandbox=True,
            )
        super().__init__(config)
        self._session: Optional[aiohttp.ClientSession] = None
        self._access_token: str = ''
        self._client_id: str = ''
    
    async def connect(self, credentials: Dict) -> bool:
        """Connect to Ajaib API
        
        Args:
            credentials: {'client_id': str, 'client_secret': str}
        
        Returns:
            True if connected
        """
        try:
            self.status = BrokerStatus.CONNECTING
            self._client_id = credentials.get('client_id', '')
            client_secret = credentials.get('client_secret', '')
            
            if self.config.sandbox:
                # Mock connection for sandbox
                self._access_token = 'sandbox_token_ajaib'
                self._connected = True
                self.status = BrokerStatus.CONNECTED
                logger.info("Connected to Ajaib (sandbox mode)")
                return True
            
            # Real API connection
            self._session = aiohttp.ClientSession()
            
            # OAuth2 token request
            auth_url = f"{self.config.api_url}/oauth/token"
            payload = {
                'grant_type': 'client_credentials',
                'client_id': self._client_id,
                'client_secret': client_secret,
            }
            
            async with self._session.post(auth_url, data=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    self._access_token = data.get('access_token', '')
                    self._connected = True
                    self.status = BrokerStatus.CONNECTED
                    logger.info("Connected to Ajaib API")
                    return True
                else:
                    self.status = BrokerStatus.ERROR
                    logger.error(f"Ajaib connection failed: {resp.status}")
                    return False
        
        except Exception as e:
            self.status = BrokerStatus.ERROR
            logger.error(f"Ajaib connection error: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from Ajaib"""
        if self._session:
            await self._session.close()
        self._connected = False
        self._access_token = ''
        self.status = BrokerStatus.DISCONNECTED
        logger.info("Disconnected from Ajaib")
    
    async def place_order(self, symbol: str, side: str, quantity: int,
                          order_type: str = 'market',
                          price: Optional[float] = None) -> Dict:
        """Place order through Ajaib"""
        if not self._connected:
            return {'success': False, 'error': 'Not connected'}
        
        if self.config.sandbox:
            # Mock order placement
            import uuid
            order_id = f"AJB-{uuid.uuid4().hex[:8].upper()}"
            logger.info(f"Ajaib mock order: {side} {quantity} {symbol}")
            return {
                'success': True,
                'order_id': order_id,
                'broker': 'ajaib',
                'status': 'pending',
            }
        
        # Real API call
        headers = {'Authorization': f'Bearer {self._access_token}'}
        payload = {
            'symbol': symbol,
            'side': side.upper(),
            'quantity': quantity,
            'orderType': order_type.upper(),
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
                    'order_id': data.get('orderId'),
                    'broker': 'ajaib',
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
            logger.info(f"Ajaib mock cancel: {order_id}")
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
            f"{self.config.api_url}/v1/portfolio/positions",
            headers=headers,
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get('positions', [])
            return []
    
    async def get_account(self) -> Dict:
        """Get account info"""
        if not self._connected:
            return {}
        
        if self.config.sandbox:
            return {
                'balance': 100_000_000,
                'equity': 100_000_000,
                'margin': 0,
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
                'orderId': order_id,
                'status': 'filled',
                'filledQuantity': 100,
                'averagePrice': 9500,
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
