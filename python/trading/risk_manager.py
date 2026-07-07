# Niskala - Risk Manager
# Risk management for paper trading

from typing import Dict, Optional, List
from dataclasses import dataclass
import logging


@dataclass
class RiskLimits:
    """Risk limit configuration"""
    max_position_pct: float = 0.20        # Max 20% per stock
    max_total_exposure_pct: float = 0.95   # Max 95% invested
    max_daily_loss_pct: float = 0.05       # Max 5% daily loss
    max_open_positions: int = 20           # Max 20 positions
    min_order_value: float = 100_000       # Min 100K IDR
    max_order_value: float = 10_000_000_000  # Max 10B IDR
    stop_loss_pct: float = 0.08            # Default 8% stop loss
    take_profit_pct: float = 0.15          # Default 15% take profit
    max_leverage: float = 1.0              # No leverage (cash account)


@dataclass
class RiskCheck:
    """Result of a risk check"""
    passed: bool
    reason: str = ''
    severity: str = 'info'  # info, warning, danger


class RiskManager:
    """Risk management engine for paper trading"""
    
    def __init__(self, limits: Optional[RiskLimits] = None):
        self.limits = limits or RiskLimits()
        self.daily_pnl: float = 0.0
        self.daily_reset_date: str = ''
        logging.info("RiskManager initialized")
    
    def check_pre_trade(self, order: Dict, portfolio: Dict,
                        current_prices: Dict) -> RiskCheck:
        """Pre-trade risk check
        
        Args:
            order: {'symbol', 'side', 'quantity', 'price', 'order_type'}
            portfolio: {'cash', 'positions', 'equity'}
            current_prices: {symbol: price}
        
        Returns:
            RiskCheck with pass/fail and reason
        """
        symbol = order['symbol']
        side = order['side']
        quantity = order['quantity']
        price = order['price']
        
        if price is None or price <= 0:
            return RiskCheck(passed=False, reason='Invalid price', severity='danger')
        
        order_value = price * quantity
        
        # Check minimum order value
        if order_value < self.limits.min_order_value:
            return RiskCheck(
                passed=False,
                reason=f'Order value {order_value:,.0f} below minimum {self.limits.min_order_value:,.0f}',
                severity='warning'
            )
        
        # Check maximum order value
        if order_value > self.limits.max_order_value:
            return RiskCheck(
                passed=False,
                reason=f'Order value {order_value:,.0f} exceeds maximum {self.limits.max_order_value:,.0f}',
                severity='warning'
            )
        
        if side == 'buy':
            # Check sufficient cash
            if order_value > portfolio['cash']:
                return RiskCheck(
                    passed=False,
                    reason=f'Insufficient cash: need {order_value:,.0f}, have {portfolio["cash"]:,.0f}',
                    severity='danger'
                )
            
            # Check max positions
            if len(portfolio['positions']) >= self.limits.max_open_positions:
                if symbol not in portfolio['positions']:
                    return RiskCheck(
                        passed=False,
                        reason=f'Maximum open positions ({self.limits.max_open_positions}) reached',
                        severity='warning'
                    )
            
            # Check max position concentration
            equity = portfolio['equity']
            current_pos_value = portfolio['positions'].get(symbol, {}).get('market_value', 0)
            new_pos_value = current_pos_value + order_value
            pos_pct = new_pos_value / equity if equity > 0 else 0
            
            if pos_pct > self.limits.max_position_pct:
                return RiskCheck(
                    passed=False,
                    reason=f'Position would be {pos_pct:.1%} of equity (max {self.limits.max_position_pct:.1%})',
                    severity='warning'
                )
            
            # Check total exposure
            total_invested = sum(
                pos.get('market_value', 0)
                for pos in portfolio['positions'].values()
            )
            new_total = total_invested + order_value
            exposure_pct = new_total / equity if equity > 0 else 0
            
            if exposure_pct > self.limits.max_total_exposure_pct:
                return RiskCheck(
                    passed=False,
                    reason=f'Total exposure would be {exposure_pct:.1%} (max {self.limits.max_total_exposure_pct:.1%})',
                    severity='warning'
                )
        
        elif side == 'sell':
            # Check sufficient position
            pos = portfolio['positions'].get(symbol)
            if not pos or pos.get('quantity', 0) < quantity:
                available = pos.get('quantity', 0) if pos else 0
                return RiskCheck(
                    passed=False,
                    reason=f'Insufficient position: need {quantity}, have {available}',
                    severity='danger'
                )
        
        # Check daily loss limit
        equity = portfolio['equity']
        if equity > 0:
            daily_loss_pct = abs(self.daily_pnl) / equity if self.daily_pnl < 0 else 0
            if daily_loss_pct >= self.limits.max_daily_loss_pct:
                return RiskCheck(
                    passed=False,
                    reason=f'Daily loss limit reached ({daily_loss_pct:.1%} of equity)',
                    severity='danger'
                )
        
        return RiskCheck(passed=True, reason='Risk check passed')
    
    def check_stop_loss(self, position: Dict, current_price: float,
                        stop_loss_pct: Optional[float] = None) -> RiskCheck:
        """Check if stop loss is triggered
        
        Args:
            position: {'symbol', 'avg_price', 'quantity'}
            current_price: Current market price
            stop_loss_pct: Override default stop loss %
        
        Returns:
            RiskCheck indicating if stop loss should trigger
        """
        avg_price = position['avg_price']
        threshold = stop_loss_pct or self.limits.stop_loss_pct
        
        if avg_price <= 0:
            return RiskCheck(passed=False, reason='Invalid average price')
        
        loss_pct = (avg_price - current_price) / avg_price
        
        if loss_pct >= threshold:
            return RiskCheck(
                passed=False,
                reason=f'Stop loss triggered: {loss_pct:.1%} loss (threshold {threshold:.1%})',
                severity='danger'
            )
        
        return RiskCheck(passed=True)
    
    def check_take_profit(self, position: Dict, current_price: float,
                          take_profit_pct: Optional[float] = None) -> RiskCheck:
        """Check if take profit is triggered
        
        Args:
            position: {'symbol', 'avg_price', 'quantity'}
            current_price: Current market price
            take_profit_pct: Override default take profit %
        
        Returns:
            RiskCheck indicating if take profit should trigger
        """
        avg_price = position['avg_price']
        threshold = take_profit_pct or self.limits.take_profit_pct
        
        if avg_price <= 0:
            return RiskCheck(passed=False, reason='Invalid average price')
        
        gain_pct = (current_price - avg_price) / avg_price
        
        if gain_pct >= threshold:
            return RiskCheck(
                passed=False,
                reason=f'Take profit triggered: {gain_pct:.1%} gain (threshold {threshold:.1%})',
                severity='danger'
            )
        
        return RiskCheck(passed=True)
    
    def calculate_position_size(self, symbol: str, price: float,
                                portfolio: Dict, risk_pct: float = 0.02) -> int:
        """Calculate position size based on risk budget
        
        Args:
            symbol: Stock symbol
            price: Current price
            portfolio: {'cash', 'equity', 'positions'}
            risk_pct: Risk per trade as % of equity (default 2%)
        
        Returns:
            Recommended quantity in lots
        """
        from ..quant.backtest_engine import IDXCommissionModel
        
        equity = portfolio['equity']
        risk_budget = equity * risk_pct
        
        # Calculate max shares based on risk budget
        # Assume stop loss at default %
        stop_loss_distance = price * self.limits.stop_loss_pct
        max_shares_by_risk = int(risk_budget / stop_loss_distance) if stop_loss_distance > 0 else 0
        
        # Calculate max shares based on position limit
        max_pos_value = equity * self.limits.max_position_pct
        current_pos_value = portfolio['positions'].get(symbol, {}).get('market_value', 0)
        available_pos_value = max_pos_value - current_pos_value
        max_shers_by_position = int(available_pos_value / price) if price > 0 else 0
        
        # Take the minimum
        max_shares = min(max_shares_by_risk, max_shers_by_position)
        
        # Round to lot size
        lots = IDXCommissionModel.round_to_lot(max_shares)
        
        return lots
    
    def get_portfolio_risk_metrics(self, portfolio: Dict,
                                   current_prices: Dict) -> Dict:
        """Calculate portfolio risk metrics
        
        Args:
            portfolio: {'cash', 'positions', 'equity'}
            current_prices: {symbol: price}
        
        Returns:
            Dict with risk metrics
        """
        equity = portfolio['equity']
        positions = portfolio['positions']
        
        if equity <= 0:
            return {'error': 'Invalid equity'}
        
        # Calculate exposure
        total_invested = sum(
            pos.get('market_value', 0) for pos in positions.values()
        )
        cash_pct = portfolio['cash'] / equity
        invested_pct = total_invested / equity
        
        # Calculate concentration
        position_pcts = {}
        for symbol, pos in positions.items():
            market_value = current_prices.get(symbol, pos.get('avg_price', 0)) * pos.get('quantity', 0)
            position_pcts[symbol] = market_value / equity
        
        max_concentration = max(position_pcts.values()) if position_pcts else 0
        
        # Check limits
        warnings = []
        if invested_pct > self.limits.max_total_exposure_pct:
            warnings.append(f'Total exposure {invested_pct:.1%} exceeds limit')
        if max_concentration > self.limits.max_position_pct:
            warnings.append(f'Max position concentration {max_concentration:.1%} exceeds limit')
        if len(positions) > self.limits.max_open_positions:
            warnings.append(f'Position count {len(positions)} exceeds limit')
        
        return {
            'equity': equity,
            'cash': portfolio['cash'],
            'cash_pct': cash_pct,
            'invested': total_invested,
            'invested_pct': invested_pct,
            'position_count': len(positions),
            'max_concentration': max_concentration,
            'position_pcts': position_pcts,
            'warnings': warnings,
        }
    
    def reset_daily(self):
        """Reset daily P&L tracking"""
        self.daily_pnl = 0.0
    
    def update_daily_pnl(self, pnl: float):
        """Update daily P&L"""
        self.daily_pnl += pnl
