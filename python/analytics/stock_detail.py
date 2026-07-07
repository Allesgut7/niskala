# Niskala - Order Book & Stock Detail
# Version: 1.0.0
# Order book display and stock detail screen

from typing import Dict, List, Optional
from dataclasses import dataclass
import logging


@dataclass
class OrderBookLevel:
    """Single order book level"""
    price: float
    volume: int
    total: int
    queue_count: int = 0


@dataclass
class OrderBook:
    """Full order book for a stock"""
    symbol: str
    bids: List[OrderBookLevel]  # Buy orders (descending price)
    asks: List[OrderBookLevel]  # Sell orders (ascending price)
    spread: float = 0.0
    spread_pct: float = 0.0
    bid_total: int = 0
    ask_total: int = 0
    bid_ask_ratio: float = 0.0
    pressure: str = 'neutral'  # bullish, bearish, neutral


@dataclass
class RecentTrade:
    """Single trade record"""
    time: str
    price: float
    volume: int
    side: str  # 'BUY' or 'SELL'
    value: float = 0.0


@dataclass
class StockDetail:
    """Complete stock detail information"""
    symbol: str
    name: str
    sector: str
    industry: str
    
    # Price info
    last_price: float = 0.0
    change: float = 0.0
    change_pct: float = 0.0
    open_price: float = 0.0
    high: float = 0.0
    low: float = 0.0
    prev_close: float = 0.0
    
    # Trading data
    volume: int = 0
    value: float = 0.0
    frequency: int = 0
    avg_price: float = 0.0
    
    # Market data
    market_cap: float = 0.0
    shares_outstanding: float = 0.0
    free_float: float = 0.0
    
    # 52-week range
    week52_high: float = 0.0
    week52_low: float = 0.0
    
    # Order book
    order_book: Optional[OrderBook] = None
    
    # Recent trades
    recent_trades: List[RecentTrade] = None
    
    # Fundamentals
    pe_ratio: float = 0.0
    pb_ratio: float = 0.0
    roe: float = 0.0
    roa: float = 0.0
    dividend_yield: float = 0.0
    eps: float = 0.0
    debt_equity: float = 0.0
    current_ratio: float = 0.0
    
    def __post_init__(self):
        if self.recent_trades is None:
            self.recent_trades = []


class OrderBookRenderer:
    """Render order book in ASCII format"""
    
    @staticmethod
    def render(order_book: OrderBook, levels: int = 10) -> str:
        """Render order book as ASCII table
        
        Args:
            order_book: OrderBook data
            levels: Number of price levels to show
            
        Returns:
            ASCII art string
        """
        lines = []
        
        # Header
        lines.append("┌─ ORDER BOOK ─────────────────────────────────────────────────────┐")
        lines.append("│                                                                    │")
        lines.append("│      BID (BUY)                    │      ASK (SELL)                │")
        lines.append("│  Price    Volume    Total         │  Price    Volume    Total      │")
        lines.append("│  ─────────────────────────────────┼──────────────────────────────  │")
        
        # Render levels
        max_levels = min(levels, len(order_book.bids), len(order_book.asks))
        
        for i in range(max_levels):
            bid = order_book.bids[i] if i < len(order_book.bids) else None
            ask = order_book.asks[i] if i < len(order_book.asks) else None
            
            bid_str = f"  {bid.price:>7,.0f}  {bid.volume:>7,}  {bid.total:>9,}" if bid else " " * 33
            ask_str = f"  {ask.price:>7,.0f}  {ask.volume:>7,}  {ask.total:>9,}" if ask else ""
            
            lines.append(f"│{bid_str} │{ask_str:<33}│")
        
        # Summary
        lines.append("│                                                                    │")
        lines.append("│  " + "─" * 62 + "  │")
        
        # Totals
        lines.append(f"│  Total Bid: {order_book.bid_total:>10,}         Total Ask: {order_book.ask_total:>10,}         │")
        lines.append(f"│  Bid/Ask Ratio: {order_book.bid_ask_ratio:.2f}         Pressure: {order_book.pressure.upper():>10}         │")
        
        # Spread
        lines.append(f"│  Spread: {order_book.spread:,.0f} ({order_book.spread_pct:.2f}%)                                        │")
        
        lines.append("└────────────────────────────────────────────────────────────────────┘")
        
        return '\n'.join(lines)
    
    @staticmethod
    def render_visual(order_book: OrderBook, width: int = 60) -> str:
        """Render order book with visual volume bars"""
        lines = []
        
        lines.append(" ORDER BOOK")
        lines.append("─" * width)
        
        # Find max volume for scaling
        all_volumes = [l.volume for l in order_book.bids + order_book.asks]
        max_vol = max(all_volumes) if all_volumes else 1
        
        bar_width = width // 2 - 15
        
        # Bids (left side)
        lines.append(" BID (BUY)")
        for level in order_book.bids[:8]:
            bar_len = int(level.volume / max_vol * bar_width)
            bar = "█" * bar_len
            lines.append(f"  {level.price:>7,.0f}  {level.volume:>7,}  {bar}")
        
        lines.append("")
        
        # Asks (right side)
        lines.append(" ASK (SELL)")
        for level in order_book.asks[:8]:
            bar_len = int(level.volume / max_vol * bar_width)
            bar = "░" * bar_len
            lines.append(f"  {level.price:>7,.0f}  {level.volume:>7,}  {bar}")
        
        return '\n'.join(lines)


class StockDetailRenderer:
    """Render stock detail screen"""
    
    @staticmethod
    def render_overview(detail: StockDetail) -> str:
        """Render overview tab"""
        lines = []
        
        lines.append(f"┌─ OVERVIEW ──────────────────────────────────────────────────────┐")
        lines.append(f"│                                                                  │")
        lines.append(f"│  {detail.symbol} - {detail.name}")
        lines.append(f"│  Sector: {detail.sector} │ Industry: {detail.industry}")
        lines.append(f"│                                                                  │")
        lines.append(f"│  PRICE INFORMATION")
        lines.append(f"│  Last Price:    {detail.last_price:>10,.0f} IDR")
        lines.append(f"│  Change:        {detail.change:>+10,.0f} ({detail.change_pct:+.2f}%)")
        lines.append(f"│  Open:          {detail.open_price:>10,.0f}")
        lines.append(f"│  High:          {detail.high:>10,.0f}")
        lines.append(f"│  Low:           {detail.low:>10,.0f}")
        lines.append(f"│  Previous:      {detail.prev_close:>10,.0f}")
        lines.append(f"│                                                                  │")
        lines.append(f"│  TRADING DATA")
        lines.append(f"│  Volume:        {detail.volume:>10,} shares")
        lines.append(f"│  Value:         {detail.value:>10,.0f} IDR")
        lines.append(f"│  Frequency:     {detail.frequency:>10,} trades")
        lines.append(f"│  Average:       {detail.avg_price:>10,.0f}")
        lines.append(f"│                                                                  │")
        lines.append(f"│  MARKET DATA")
        lines.append(f"│  Market Cap:    {detail.market_cap:>10,.0f} IDR ({detail.market_cap/1e12:.1f}T)")
        lines.append(f"│  Shares Out:    {detail.shares_outstanding:>10,.0f}")
        lines.append(f"│  Free Float:    {detail.free_float:>9.1f}%")
        lines.append(f"│                                                                  │")
        lines.append(f"│  52-WEEK RANGE")
        lines.append(f"│  High:          {detail.week52_high:>10,.0f}")
        lines.append(f"│  Low:           {detail.week52_low:>10,.0f}")
        
        if detail.week52_high > detail.week52_low:
            pct_from_low = ((detail.last_price - detail.week52_low) / 
                           (detail.week52_high - detail.week52_low) * 100)
            lines.append(f"│  Current:       {pct_from_low:>9.1f}% from low")
        
        lines.append(f"│                                                                  │")
        lines.append(f"└──────────────────────────────────────────────────────────────────┘")
        
        return '\n'.join(lines)
    
    @staticmethod
    def render_fundamentals(detail: StockDetail) -> str:
        """Render fundamentals tab"""
        lines = []
        
        lines.append("┌─ FUNDAMENTAL DATA ─────────────────────────────────────────────┐")
        lines.append("│                                                                │")
        lines.append("│  VALUATION                                                     │")
        lines.append(f"│  PE Ratio:        {detail.pe_ratio:>8.1f}x")
        lines.append(f"│  PB Ratio:        {detail.pb_ratio:>8.1f}x")
        lines.append(f"│  EPS:             {detail.eps:>8,.0f} IDR")
        lines.append("│                                                                │")
        lines.append("│  PROFITABILITY                                                 │")
        lines.append(f"│  ROE:             {detail.roe:>7.1f}%")
        lines.append(f"│  ROA:             {detail.roa:>7.1f}%")
        lines.append("│                                                                │")
        lines.append("│  DIVIDEND                                                      │")
        lines.append(f"│  Dividend Yield:  {detail.dividend_yield:>7.1f}%")
        lines.append("│                                                                │")
        lines.append("│  FINANCIAL HEALTH                                              │")
        lines.append(f"│  Debt/Equity:     {detail.debt_equity:>8.2f}")
        lines.append(f"│  Current Ratio:   {detail.current_ratio:>8.2f}")
        lines.append("│                                                                │")
        lines.append("└────────────────────────────────────────────────────────────────┘")
        
        return '\n'.join(lines)
    
    @staticmethod
    def render_trades(trades: List[RecentTrade], limit: int = 15) -> str:
        """Render recent trades tab"""
        lines = []
        
        lines.append("┌─ RECENT TRADES ────────────────────────────────────────────────┐")
        lines.append("│  Time        Price    Volume   Side    Value                   │")
        lines.append("│  ────────────────────────────────────────────────────────────  │")
        
        for trade in trades[:limit]:
            side_char = "▲ BUY " if trade.side == 'BUY' else "▼ SELL"
            lines.append(
                f"│  {trade.time:>10}  {trade.price:>7,.0f}  {trade.volume:>7,}  "
                f"{side_char}  {trade.value:>12,.0f}  │"
            )
        
        if not trades:
            lines.append("│  No recent trades available                                    │")
        
        lines.append("└────────────────────────────────────────────────────────────────┘")
        
        return '\n'.join(lines)
    
    @staticmethod
    def render_tabs(active_tab: int = 0) -> str:
        """Render tab navigation"""
        tabs = ['Overview', 'Chart', 'Order Book', 'Trades', 'Fundamental', 'News']
        
        tab_str = " "
        for i, tab in enumerate(tabs):
            if i == active_tab:
                tab_str += f"[{tab}] "
            else:
                tab_str += f" {tab}  "
        
        return tab_str


# Test
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    # Create sample order book
    bids = [
        OrderBookLevel(4850, 500, 500),
        OrderBookLevel(4840, 800, 1300),
        OrderBookLevel(4830, 1200, 2500),
        OrderBookLevel(4820, 1500, 4000),
        OrderBookLevel(4810, 2000, 6000),
    ]
    
    asks = [
        OrderBookLevel(4860, 300, 300),
        OrderBookLevel(4870, 450, 750),
        OrderBookLevel(4880, 600, 1350),
        OrderBookLevel(4890, 900, 2250),
        OrderBookLevel(4900, 1200, 3450),
    ]
    
    ob = OrderBook(
        symbol='BBRI',
        bids=bids,
        asks=asks,
        spread=10,
        spread_pct=0.21,
        bid_total=6000,
        ask_total=3450,
        bid_ask_ratio=1.74,
        pressure='bullish'
    )
    
    print(OrderBookRenderer.render(ob))
    print()
    print(OrderBookRenderer.render_visual(ob))
    
    # Stock detail
    detail = StockDetail(
        symbol='BBRI',
        name='Bank Rakyat Indonesia Tbk.',
        sector='Financials',
        industry='Banking',
        last_price=4850,
        change=50,
        change_pct=1.04,
        open_price=4800,
        high=4870,
        low=4790,
        prev_close=4800,
        volume=125000000,
        value=606250000000,
        frequency=15420,
        market_cap=625500000000000,
        shares_outstanding=128969072000,
        free_float=45.2,
        week52_high=5200,
        week52_low=3800,
        pe_ratio=12.5,
        pb_ratio=2.1,
        roe=18.5,
        roa=3.2,
        dividend_yield=4.2,
        eps=388,
        debt_equity=0.8,
        current_ratio=2.1
    )
    
    print()
    print(StockDetailRenderer.render_tabs(0))
    print()
    print(StockDetailRenderer.render_overview(detail))
