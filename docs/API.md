![NISKALA](../../Logo-fix.png)

# Niskala - API Documentation

REST API for Niskala trading platform.

**Base URL:** `http://YOUR_VPS_IP/api/`  
**Docs:** `http://YOUR_VPS_IP/api/docs` (Swagger UI)  
**Health:** `http://YOUR_VPS_IP/health`

---

## Authentication

```bash
# Login
POST /api/auth/login
{
  "username": "user",
  "password": "pass"
}

# Response
{
  "access_token": "token...",
  "token_type": "bearer",
  "user_id": "user_xxx"
}
```

**Use token in requests:**
```
Authorization: Bearer <access_token>
```

---

## Market Data

### Get Quote
```
GET /api/market/quote/{symbol}

Response:
{
  "symbol": "BBCA",
  "bid": 9450,
  "ask": 9550,
  "last": 9500,
  "volume": 50000000,
  "change": 150,
  "change_pct": 1.6,
  "timestamp": "2026-07-06T10:00:00"
}
```

### Get Order Book
```
GET /api/market/orderbook/{symbol}?depth=5

Response:
{
  "symbol": "BBCA",
  "bids": [[9450, 100], [9400, 200], ...],
  "asks": [[9550, 150], [9600, 100], ...],
  "timestamp": "2026-07-06T10:00:00"
}
```

### Get All Quotes
```
GET /api/market/quotes

Response:
{
  "BBCA": {"last": 9500, "change": 150, "change_pct": 1.6},
  "BBRI": {"last": 4800, "change": -50, "change_pct": -1.03},
  ...
}
```

### List Stocks
```
GET /api/market/stocks

Response:
{
  "stocks": [
    {"symbol": "BBCA", "name": "Bank Central Asia", "base_price": 9500},
    ...
  ]
}
```

### Market Status
```
GET /api/market/market-status

Response:
{
  "is_open": true,
  "stocks_count": 15,
  "last_prices": {...}
}
```

---

## Trading

### Place Order
```
POST /api/trading/order
{
  "symbol": "BBCA",
  "side": "buy",
  "quantity": 100,
  "order_type": "market",
  "price": null,
  "notes": ""
}

Response:
{
  "success": true,
  "order_id": "uuid...",
  "trade_id": "trade_xxx",
  "symbol": "BBCA",
  "side": "buy",
  "quantity": 100,
  "price": 9500,
  "value": 950000,
  "commission": 1500,
  "pnl": -1500
}
```

### Cancel Order
```
DELETE /api/trading/order/{order_id}

Response:
{"message": "Order cancelled"}
```

### Get Portfolio
```
GET /api/trading/portfolio

Response:
{
  "cash": 50000000,
  "equity": 51000000,
  "positions_value": 1000000,
  "total_realized_pnl": 500000,
  "total_unrealized_pnl": 50000,
  "return_pct": 1.0,
  "positions": [...]
}
```

### Get Positions
```
GET /api/trading/positions

Response:
{
  "position_count": 3,
  "total_market_value": 1000000,
  "positions": [
    {"symbol": "BBCA", "quantity": 100, "avg_price": 9500, "unrealized_pnl": 0}
  ]
}
```

### Get Trades
```
GET /api/trading/trades?symbol=BBCA&limit=50

Response:
[
  {
    "id": "trade_xxx",
    "symbol": "BBCA",
    "side": "buy",
    "quantity": 100,
    "price": 9500,
    "value": 950000,
    "commission": 1500,
    "pnl": -1500,
    "timestamp": "2026-07-06T10:00:00"
  }
]
```

### Get Risk Metrics
```
GET /api/trading/risk

Response:
{
  "equity": 51000000,
  "cash": 50000000,
  "cash_pct": 0.98,
  "invested_pct": 0.02,
  "position_count": 1,
  "warnings": []
}
```

---

## WebSocket

### Connect
```
ws://YOUR_VPS_IP/ws/trading
```

### Subscribe
```json
{"type": "subscribe", "channel": "trades"}
```

### Order Update
```json
{
  "type": "order_update",
  "data": {
    "order_id": "uuid...",
    "status": "filled",
    "fill_price": 9500,
    "fill_quantity": 100
  }
}
```

---

## Health Check

```
GET /health

Response:
{
  "status": "healthy",
  "version": "1.0.0",
  "checks": {
    "database": {"status": "healthy"},
    "redis": {"status": "healthy"},
    "disk": {"status": "healthy", "free_gb": 30.5}
  }
}
```

---

## Error Responses

```json
// 400 Bad Request
{"error": "Invalid input", "message": "Quantity must be positive"}

// 401 Unauthorized
{"error": "Missing authorization token"}

// 404 Not Found
{"error": "Symbol not found"}

// 429 Rate Limited
{"error": "Rate limit exceeded", "retry_after": 60}

// 500 Server Error
{"error": "Internal server error"}
```

---

## Rate Limits

| Endpoint | Limit | Burst |
|----------|-------|-------|
| `/api/market/*` | 120 req/min | 30 |
| `/api/trading/*` | 30 req/min | 10 |
| `/api/auth/*` | 10 req/min | 5 |
| `/health` | Unlimited | - |

---

**END OF API DOCUMENTATION**
