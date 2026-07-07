# Niskala - Broker Routes
# API routes for broker integration

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


class ConnectBrokerRequest(BaseModel):
    broker: str  # 'ajaib' or 'stockbit'
    credentials: Dict


class PlaceBrokerOrderRequest(BaseModel):
    symbol: str
    side: str
    quantity: int
    order_type: str = 'market'
    price: Optional[float] = None


# Global broker manager reference
_broker_manager = None


def set_broker_manager(manager):
    global _broker_manager
    _broker_manager = manager


def get_broker_manager():
    if _broker_manager is None:
        raise HTTPException(status_code=503, detail="Broker manager not initialized")
    return _broker_manager


@router.post("/connect")
async def connect_broker(request: ConnectBrokerRequest):
    """Connect to a broker"""
    manager = get_broker_manager()
    
    try:
        result = await manager.connect(request.broker, request.credentials)
        return {"message": f"Connected to {request.broker}", "status": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/disconnect/{broker}")
async def disconnect_broker(broker: str):
    """Disconnect from broker"""
    manager = get_broker_manager()
    await manager.disconnect(broker)
    return {"message": f"Disconnected from {broker}"}


@router.get("/status")
async def get_broker_status():
    """Get broker connection status"""
    manager = get_broker_manager()
    return manager.get_status()


@router.post("/order")
async def place_broker_order(request: PlaceBrokerOrderRequest):
    """Place order through broker"""
    manager = get_broker_manager()
    
    try:
        result = await manager.place_order(
            symbol=request.symbol,
            side=request.side,
            quantity=request.quantity,
            order_type=request.order_type,
            price=request.price,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/order/{order_id}")
async def cancel_broker_order(order_id: str):
    """Cancel broker order"""
    manager = get_broker_manager()
    
    try:
        result = await manager.cancel_order(order_id)
        return {"message": "Order cancelled", "result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/positions")
async def get_broker_positions():
    """Get positions from broker"""
    manager = get_broker_manager()
    
    try:
        return await manager.get_positions()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/account")
async def get_broker_account():
    """Get broker account info"""
    manager = get_broker_manager()
    
    try:
        return await manager.get_account()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
