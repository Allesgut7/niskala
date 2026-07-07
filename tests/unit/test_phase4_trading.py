# Niskala - Phase 4 Tests
# Tests for paper trading engine

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestIDXCommissionModel:
    """Test IDX commission model"""
    
    def test_lot_size_rounding(self):
        from python.quant.backtest_engine import IDXCommissionModel
        
        assert IDXCommissionModel.round_to_lot(150) == 100
        assert IDXCommissionModel.round_to_lot(250) == 200
        assert IDXCommissionModel.round_to_lot(99) == 0
        assert IDXCommissionModel.round_to_lot(100) == 100
    
    def test_tick_size_rounding(self):
        from python.quant.backtest_engine import IDXCommissionModel
        
        # Price < 2000: tick size 50
        assert IDXCommissionModel.round_to_tick(1525) == 1500
        assert IDXCommissionModel.round_to_tick(1575) == 1600
        
        # Price >= 2000: tick size 100
        assert IDXCommissionModel.round_to_tick(9525) == 9500
        assert IDXCommissionModel.round_to_tick(9575) == 9600
    
    def test_commission_calculation(self):
        from python.quant.backtest_engine import IDXCommissionModel, OrderSide
        
        # Buy commission: 0.15%
        buy_comm = IDXCommissionModel.calculate_commission(OrderSide.BUY, 1_000_000)
        assert buy_comm == 1_500
        
        # Sell commission: 0.25% + 0.1% tax = 0.35%
        sell_comm = IDXCommissionModel.calculate_commission(OrderSide.SELL, 1_000_000)
        assert sell_comm == 3_500


class TestOrderManager:
    """Test order manager"""
    
    def test_create_order(self):
        from python.trading.order_manager import OrderManager, OrderSide, OrderType
        
        manager = OrderManager()
        order = manager.create_order('BBCA', 'buy', 100, 'market')
        
        assert order.symbol == 'BBCA'
        assert order.side == OrderSide.BUY
        assert order.quantity == 100
        assert order.order_type == OrderType.MARKET
        assert len(manager.get_pending_orders()) == 1
    
    def test_cancel_order(self):
        from python.trading.order_manager import OrderManager
        
        manager = OrderManager()
        order = manager.create_order('BBCA', 'buy', 100, 'market')
        
        assert manager.cancel_order(order.id) is True
        assert len(manager.get_pending_orders()) == 0
    
    def test_fill_order(self):
        from python.trading.order_manager import OrderManager, OrderStatus
        
        manager = OrderManager()
        order = manager.create_order('BBCA', 'buy', 100, 'market')
        
        filled = manager.fill_order(order.id, 9500, 100, 1500)
        
        assert filled.status == OrderStatus.FILLED
        assert filled.fill_price == 9500
        assert filled.commission == 1500


class TestPositionTracker:
    """Test position tracker"""
    
    def test_open_position(self):
        from python.trading.position_tracker import PositionTracker
        
        tracker = PositionTracker()
        pos = tracker.open_position('BBCA', 100, 9500, 1500)
        
        assert pos.symbol == 'BBCA'
        assert pos.quantity == 100
        # avg_price = total_cost / quantity = (9500*100 + 1500) / 100 = 9515
        assert pos.avg_price == 9515
        assert pos.total_cost == 951500
    
    def test_add_to_position(self):
        from python.trading.position_tracker import PositionTracker
        
        tracker = PositionTracker()
        tracker.open_position('BBCA', 100, 9500, 1500)
        tracker.open_position('BBCA', 100, 10000, 1500)
        
        pos = tracker.get_position('BBCA')
        assert pos.quantity == 200
        # avg_price = (951500 + 1001500) / 200 = 9765
        assert pos.avg_price == 9765
    
    def test_close_position(self):
        from python.trading.position_tracker import PositionTracker
        
        tracker = PositionTracker()
        tracker.open_position('BBCA', 200, 9500, 3000)
        
        closed = tracker.close_position('BBCA', 100, 10000, 1500)
        
        assert closed is not None
        pos = tracker.get_position('BBCA')
        assert pos.quantity == 100


class TestPnLCalculator:
    """Test P&L calculator"""
    
    def test_position_pnl(self):
        from python.trading.pnl_calculator import PnLCalculator
        
        calc = PnLCalculator()
        result = calc.calculate_position_pnl(9500, 10000, 100)
        
        assert result['cost_basis'] == 950_000
        assert result['market_value'] == 1_000_000
        assert result['unrealized_pnl'] == 50_000
    
    def test_portfolio_summary(self):
        from python.trading.pnl_calculator import PnLCalculator
        
        calc = PnLCalculator()
        portfolio = {
            'cash': 50_000_000,
            'positions': {
                'BBCA': {'quantity': 100, 'avg_price': 9500}
            }
        }
        prices = {'BBCA': 10000}
        
        summary = calc.calculate_portfolio_summary(portfolio, prices)
        
        assert summary.cash == 50_000_000
        assert summary.positions_value == 1_000_000
        assert summary.equity == 51_000_000


class TestRiskManager:
    """Test risk manager"""
    
    def test_position_size_calculation(self):
        from python.trading.risk_manager import RiskManager
        
        manager = RiskManager()
        portfolio = {
            'cash': 50_000_000,
            'equity': 100_000_000,
            'positions': {},
        }
        
        size = manager.calculate_position_size('BBCA', 9500, portfolio)
        
        assert size > 0
        assert size % 100 == 0  # Must be lot size


class TestMarketSimulator:
    """Test market simulator"""
    
    def test_get_quote(self):
        from python.trading.market_simulator import MarketSimulator
        
        sim = MarketSimulator()
        quote = sim.get_quote('BBCA')
        
        assert quote is not None
        assert quote.symbol == 'BBCA'
        assert quote.last > 0
        assert quote.bid > 0
        assert quote.ask > 0
    
    def test_get_orderbook(self):
        from python.trading.market_simulator import MarketSimulator
        
        sim = MarketSimulator()
        ob = sim.get_orderbook('BBCA')
        
        assert ob is not None
        assert len(ob.bids) == 5
        assert len(ob.asks) == 5
        # Bids should be descending (or equal due to tick rounding)
        assert ob.bids[0][0] >= ob.bids[-1][0]
        # Asks should be ascending (or equal due to tick rounding)
        assert ob.asks[0][0] <= ob.asks[-1][0]
        # Best bid < best ask (spread)
        assert ob.bids[0][0] <= ob.asks[0][0]


class TestPaperTradingEngine:
    """Test paper trading engine"""
    
    def test_place_buy_order(self):
        from python.trading.paper_engine import PaperTradingEngine, TradingConfig
        
        config = TradingConfig(initial_capital=100_000_000)
        engine = PaperTradingEngine(config)
        
        result = engine.place_order('BBCA', 'buy', 100, 'market')
        
        assert result['success'] is True
        assert result['symbol'] == 'BBCA'
        assert result['quantity'] == 100
    
    def test_place_sell_order(self):
        from python.trading.paper_engine import PaperTradingEngine, TradingConfig
        
        config = TradingConfig(initial_capital=100_000_000)
        engine = PaperTradingEngine(config)
        
        # Buy first
        engine.place_order('BBCA', 'buy', 200, 'market')
        
        # Then sell
        result = engine.place_order('BBCA', 'sell', 100, 'market')
        
        assert result['success'] is True
    
    def test_get_portfolio_summary(self):
        from python.trading.paper_engine import PaperTradingEngine, TradingConfig
        
        config = TradingConfig(initial_capital=100_000_000)
        engine = PaperTradingEngine(config)
        
        engine.place_order('BBCA', 'buy', 100, 'market')
        
        summary = engine.get_portfolio_summary()
        
        assert summary['cash'] < 100_000_000
        assert summary['equity'] > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
