# Niskala - API Server
# FastAPI server for mobile app and external integrations

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
import json
from typing import Dict, List
import logging

from .routes.auth_routes import router as auth_router
from .routes.trading_routes import router as trading_router
from .routes.market_routes import router as market_router
from .routes.broker_routes import router as broker_router
from .middleware.auth_middleware import AuthMiddleware
from .middleware.rate_limiter import RateLimitMiddleware

logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket connection manager"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected: {len(self.active_connections)} active")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected: {len(self.active_connections)} active")
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass


manager = ConnectionManager()


def create_app() -> FastAPI:
    """Create FastAPI application"""
    app = FastAPI(
        title="Niskala Trading API",
        description="API for Niskala paper trading and broker integration",
        version="1.0.0",
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Custom middleware
    auth_middleware = AuthMiddleware()
    rate_limit_middleware = RateLimitMiddleware()
    
    # Include routers
    app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
    app.include_router(trading_router, prefix="/api/trading", tags=["Trading"])
    app.include_router(market_router, prefix="/api/market", tags=["Market Data"])
    app.include_router(broker_router, prefix="/api/broker", tags=["Broker Integration"])
    
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "version": "1.0.0",
            "services": {
                "api": "ok",
                "trading": "ok",
                "market_data": "ok",
            }
        }
    
    @app.websocket("/ws/trading")
    async def websocket_trading(websocket: WebSocket):
        await manager.connect(websocket)
        try:
            while True:
                data = await websocket.receive_text()
                # Handle WebSocket messages
                message = json.loads(data)
                if message.get('type') == 'subscribe':
                    await websocket.send_json({
                        'type': 'subscribed',
                        'channel': message.get('channel', 'trades')
                    })
        except WebSocketDisconnect:
            manager.disconnect(websocket)
    
    return app


app = create_app()


def start_server(host: str = "0.0.0.0", port: int = 8080):
    """Start the API server"""
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    start_server()
