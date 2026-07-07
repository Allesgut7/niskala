# Niskala - Trading Routes
# API routes for paper trading

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


class PlaceOrderRequest(BaseModel):
    symbol: str
    side: str  # 'buy' or 'sell'
    quantity: int
    order_type: str = 'market'  # 'market' or 'limit'
    price: Optional[float] = None
    notes: str = ''


class OrderResponse(BaseModel):
    success: bool
    order_id: Optional[str] = None
    error: Optional[str] = None
    trade_id: Optional[str] = None
    symbol: Optional[str] = None
    side: Optional[str] = None
    quantity: Optional[int] = None
    price: Optional[float] = None
    value: Optional[float] = None
    commission: Optional[float] = None
    pnl: Optional[float] = None


# Global engine reference (set by server)
_engine = None


def set_engine(engine):
    global _engine
    _engine = engine


def get_engine():
    if _engine is None:
        raise HTTPException(status_code=503, detail="Trading engine not initialized")
    return _engine


@router.post("/order", response_model=OrderResponse)
async def place_order(request: PlaceOrderRequest):
    """Place a new paper trading order"""
    engine = get_engine()
    
    result = engine.place_order(
        symbol=request.symbol,
        side=request.side,
        quantity=request.quantity,
        order_type=request.order_type,
        price=request.price,
        notes=request.notes,
    )
    
    return OrderResponse(**result)


@router.delete("/order/{order_id}")
async def cancel_order(order_id: str):
    """Cancel a pending order"""
    engine = get_engine()
    result = engine.cancel_order(order_id)
    
    if result['success']:
        return {"message": "Order cancelled"}
    raise HTTPException(status_code=400, detail=result['error'])


@router.get("/portfolio")
async def get_portfolio():
    """Get portfolio summary"""
    engine = get_engine()
    return engine.get_portfolio_summary()


@router.get("/positions")
async def get_positions():
    """Get all open positions"""
    engine = get_engine()
    return engine.position_tracker.get_positions_summary()


@router.get("/trades")
async def get_trades(symbol: Optional[str] = None, limit: int = 50):
    """Get trade history"""
    engine = get_engine()
    return engine.get_trade_history(symbol=symbol, limit=limit)


@router.get("/orders")
async def get_orders(status: Optional[str] = None, limit: int = 50):
    """Get order history"""
    engine = get_engine()
    return engine.get_order_history(status=status, limit=limit)


@router.get("/risk")
async def get_risk_metrics():
    """Get portfolio risk metrics"""
    engine = get_engine()
    portfolio = engine._get_portfolio_state()
    current_prices = {
        s: engine.market_simulator.get_price(s)
        for s in engine.position_tracker.get_all_positions()
    }
    current_prices = {k: v for k, v in current_prices.items() if v is not None}
    return engine.risk_manager.get_portfolio_risk_metrics(portfolio, current_prices)


@router.post("/reset-day")
async def reset_day_pnl():
    """Reset daily P&L tracking"""
    engine = get_engine()
    engine.reset_day_pnl()
    return {"message": "Daily P&L reset"}
