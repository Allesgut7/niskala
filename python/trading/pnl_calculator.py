# Niskala - P&L Calculator
# Portfolio P&L calculation engine

from typing import Dict, Optional
from dataclasses import dataclass
import logging


@dataclass
class PnLSummary:
    """Portfolio P&L summary"""
    cash: float
    positions_value: float
    equity: float
    total_invested: float
    total_realized_pnl: float
    total_unrealized_pnl: float
    total_pnl: float
    total_commission: float
    return_pct: float
    day_pnl: float
    day_return_pct: float


class PnLCalculator:
    """Portfolio P&L calculation engine"""
    
    def __init__(self):
        logging.info("PnLCalculator initialized")
    
    def calculate_position_pnl(self, avg_price: float, current_price: float,
                               quantity: int) -> Dict:
        """Calculate P&L for a single position
        
        Args:
            avg_price: Average entry price
            current_price: Current market price
            quantity: Number of shares
        
        Returns:
            Dict with P&L metrics
        """
        if quantity <= 0 or avg_price <= 0:
            return {
                'cost_basis': 0,
                'market_value': 0,
                'unrealized_pnl': 0,
                'return_pct': 0,
            }
        
        cost_basis = avg_price * quantity
        market_value = current_price * quantity
        unrealized_pnl = market_value - cost_basis
        return_pct = (unrealized_pnl / cost_basis) * 100 if cost_basis > 0 else 0
        
        return {
            'cost_basis': cost_basis,
            'market_value': market_value,
            'unrealized_pnl': unrealized_pnl,
            'return_pct': return_pct,
        }
    
    def calculate_portfolio_summary(self, portfolio: Dict,
                                    current_prices: Dict,
                                    initial_capital: float = 100_000_000,
                                    total_realized_pnl: float = 0,
                                    total_commission: float = 0,
                                    day_pnl: float = 0) -> PnLSummary:
        """Calculate full portfolio P&L summary
        
        Args:
            portfolio: {'cash', 'positions': {symbol: {'quantity', 'avg_price'}}}
            current_prices: {symbol: current_price}
            initial_capital: Starting capital
            total_realized_pnl: Cumulative realized P&L
            total_commission: Cumulative commission paid
            day_pnl: Today's P&L
        
        Returns:
            PnLSummary with all metrics
        """
        cash = portfolio['cash']
        positions = portfolio['positions']
        
        # Calculate positions value and unrealized P&L
        positions_value = 0
        total_invested = 0
        total_unrealized_pnl = 0
        
        for symbol, pos in positions.items():
            quantity = pos.get('quantity', 0)
            avg_price = pos.get('avg_price', 0)
            current_price = current_prices.get(symbol, avg_price)
            
            pos_metrics = self.calculate_position_pnl(avg_price, current_price, quantity)
            positions_value += pos_metrics['market_value']
            total_invested += pos_metrics['cost_basis']
            total_unrealized_pnl += pos_metrics['unrealized_pnl']
        
        equity = cash + positions_value
        total_pnl = total_realized_pnl + total_unrealized_pnl
        return_pct = ((equity - initial_capital) / initial_capital) * 100 if initial_capital > 0 else 0
        day_return_pct = (day_pnl / equity) * 100 if equity > 0 else 0
        
        return PnLSummary(
            cash=cash,
            positions_value=positions_value,
            equity=equity,
            total_invested=total_invested,
            total_realized_pnl=total_realized_pnl,
            total_unrealized_pnl=total_unrealized_pnl,
            total_pnl=total_pnl,
            total_commission=total_commission,
            return_pct=return_pct,
            day_pnl=day_pnl,
            day_return_pct=day_return_pct,
        )
    
    def calculate_trade_pnl(self, side: str, quantity: int, price: float,
                            avg_price: float, commission: float) -> Dict:
        """Calculate P&L for a single trade
        
        Args:
            side: 'buy' or 'sell'
            quantity: Number of shares
            price: Execution price
            avg_price: Average position price (for sells)
            commission: Commission paid
        
        Returns:
            Dict with trade P&L
        """
        trade_value = price * quantity
        
        if side == 'buy':
            return {
                'trade_value': trade_value,
                'commission': commission,
                'net_cost': trade_value + commission,
                'pnl': -commission,  # Immediate P&L is just commission cost
            }
        else:  # sell
            proceeds = trade_value - commission
            cost_basis = avg_price * quantity
            pnl = proceeds - cost_basis
            
            return {
                'trade_value': trade_value,
                'commission': commission,
                'proceeds': proceeds,
                'cost_basis': cost_basis,
                'pnl': pnl,
            }
    
    def calculate_break_even_price(self, avg_price: float, commission_buy: float,
                                   commission_sell: float, quantity: int) -> float:
        """Calculate break-even price for a position
        
        Args:
            avg_price: Average entry price
            commission_buy: Total commission paid for entry
            commission_sell: Commission rate for sell
            quantity: Number of shares
        
        Returns:
            Break-even sell price
        """
        if quantity <= 0:
            return 0
        
        total_cost = (avg_price * quantity) + commission_buy
        # Break-even: sell_price * quantity - sell_commission = total_cost
        # sell_commission = sell_price * quantity * commission_sell_rate
        # sell_price * quantity * (1 - commission_sell_rate) = total_cost
        # sell_price = total_cost / (quantity * (1 - commission_sell_rate))
        
        sell_rate = commission_sell / (avg_price * quantity) if avg_price * quantity > 0 else 0.0035
        
        break_even = total_cost / (quantity * (1 - sell_rate))
        return break_even
    
    def format_pnl(self, pnl: float, show_sign: bool = True) -> str:
        """Format P&L for display"""
        if show_sign:
            sign = '+' if pnl >= 0 else ''
            return f"{sign}{pnl:,.0f}"
        return f"{pnl:,.0f}"
    
    def format_return(self, return_pct: float) -> str:
        """Format return percentage for display"""
        sign = '+' if return_pct >= 0 else ''
        return f"{sign}{return_pct:.2f}%"
