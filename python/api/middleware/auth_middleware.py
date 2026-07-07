# Niskala - Auth Middleware
# JWT-based authentication middleware

from functools import wraps
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class AuthMiddleware:
    """Authentication middleware for API routes"""
    
    def __init__(self):
        self._tokens = {}
    
    def validate_token(self, token: str) -> Optional[str]:
        """Validate JWT token and return user_id"""
        if token in self._tokens:
            return self._tokens[token]
        return None
    
    def create_token(self, user_id: str) -> str:
        """Create a new token"""
        import secrets
        token = secrets.token_hex(32)
        self._tokens[token] = user_id
        return token
    
    def revoke_token(self, token: str):
        """Revoke a token"""
        if token in self._tokens:
            del self._tokens[token]
    
    def require_auth(self, func):
        """Decorator to require authentication"""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get token from header
            auth_header = kwargs.get('headers', {}).get('authorization', '')
            
            if not auth_header.startswith('Bearer '):
                from fastapi import HTTPException
                raise HTTPException(status_code=401, detail="Missing authorization token")
            
            token = auth_header[7:]
            user_id = self.validate_token(token)
            
            if not user_id:
                from fastapi import HTTPException
                raise HTTPException(status_code=401, detail="Invalid or expired token")
            
            kwargs['user_id'] = user_id
            return await func(*args, **kwargs)
        
        return wrapper
