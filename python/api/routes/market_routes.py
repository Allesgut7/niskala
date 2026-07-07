# Niskala - Market Routes
# API routes for market data

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


class QuoteResponse(BaseModel):
    symbol: str
    bid: float
    ask: float
    last: float
    volume: int
    change: float
    change_pct: float
    timestamp: str


class OrderBookResponse(BaseModel):
    symbol: str
    bids: List[List[float]]
    asks: List[List[float]]
    timestamp: str


# Global simulator reference
_simulator = None


def set_simulator(simulator):
    global _simulator
    _simulator = simulator


def get_simulator():
    if _simulator is None:
        raise HTTPException(status_code=503, detail="Market simulator not initialized")
    return _simulator


@router.get("/quote/{symbol}", response_model=QuoteResponse)
async def get_quote(symbol: str):
    """Get stock quote"""
    simulator = get_simulator()
    symbol = symbol.upper()
    
    quote = simulator.get_quote(symbol)
    if not quote:
        raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
    
    return QuoteResponse(
        symbol=quote.symbol,
        bid=quote.bid,
        ask=quote.ask,
        last=quote.last,
        volume=quote.volume,
        change=quote.change,
        change_pct=quote.change_pct,
        timestamp=quote.timestamp,
    )


@router.get("/orderbook/{symbol}", response_model=OrderBookResponse)
async def get_orderbook(symbol: str, depth: int = 5):
    """Get order book"""
    simulator = get_simulator()
    symbol = symbol.upper()
    
    orderbook = simulator.get_orderbook(symbol, depth)
    if not orderbook:
        raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
    
    return OrderBookResponse(
        symbol=orderbook.symbol,
        bids=orderbook.bids,
        asks=orderbook.asks,
        timestamp=orderbook.timestamp,
    )


@router.get("/quotes")
async def get_all_quotes():
    """Get quotes for all stocks"""
    simulator = get_simulator()
    quotes = simulator.get_all_quotes()
    
    return {
        symbol: {
            'last': q.last,
            'change': q.change,
            'change_pct': q.change_pct,
            'volume': q.volume,
        }
        for symbol, q in quotes.items()
    }


@router.get("/stocks")
async def list_stocks():
    """List available stocks"""
    simulator = get_simulator()
    return {
        'stocks': [
            {
                'symbol': sym,
                'base_price': config['base_price'],
                'volatility': config['volatility'],
            }
            for sym, config in simulator.stocks.items()
        ]
    }


@router.get("/market-status")
async def get_market_status():
    """Get market status"""
    simulator = get_simulator()
    return simulator.get_market_status()
