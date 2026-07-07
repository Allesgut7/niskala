# Niskala - Phase 2 Tests
# Version: 1.0.0

import pytest
import sys
import os
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'python'))


class TestBacktestEngine:
    """Test backtesting engine"""
    
    def setup_method(self):
        from quant.backtest_engine import BacktestEngine
        self.engine = BacktestEngine(initial_capital=100_000_000)
    
    def test_initialization(self):
        assert self.engine.initial_capital == 100_000_000
        assert self.engine.capital == 100_000_000
        assert len(self.engine.positions) == 0
    
    def test_commission_model(self):
        from quant.backtest_engine import IDXCommissionModel, OrderSide
        commission = IDXCommissionModel.calculate_commission(OrderSide.BUY, 1_000_000)
        assert commission == 1_000_000 * 0.0015
    
    def test_lot_rounding(self):
        from quant.backtest_engine import IDXCommissionModel
        assert IDXCommissionModel.round_to_lot(150) == 100
        assert IDXCommissionModel.round_to_lot(250) == 200
    
    def test_tick_rounding(self):
        from quant.backtest_engine import IDXCommissionModel
        assert IDXCommissionModel.round_to_tick(1520) == 1500  # < 2000, tick=50
        assert IDXCommissionModel.round_to_tick(5250) == 5300  # >= 2000, tick=100


class TestFactorAnalyzer:
    """Test factor analysis"""
    
    def setup_method(self):
        from quant.factor_analyzer import FactorAnalyzer
        self.analyzer = FactorAnalyzer()
    
    def test_weights_sum_to_one(self):
        total = sum(self.analyzer.weights.values())
        assert abs(total - 1.0) < 0.001
    
    def test_analyze_stocks(self):
        data = pd.DataFrame({
            'symbol': ['A', 'B', 'C'],
            'price': [1000, 2000, 3000],
            'pe_ratio': [10, 15, 20],
            'pb_ratio': [1.0, 1.5, 2.0],
            'dividend_yield': [5.0, 3.0, 1.0],
            'return_1m': [5, 3, -2],
            'return_3m': [10, 5, 0],
            'return_6m': [15, 8, 3],
            'return_12m': [20, 10, 5],
            'roe': [20, 15, 10],
            'roa': [10, 8, 5],
            'debt_equity': [0.3, 0.5, 1.0],
            'current_ratio': [2.0, 1.5, 1.0],
            'market_cap': [100e12, 50e12, 25e12]
        })
        
        scores = self.analyzer.analyze(data)
        assert len(scores) == 3
        assert all(hasattr(s, 'composite_score') for s in scores)


class TestPortfolioOptimizer:
    """Test portfolio optimizer"""
    
    def setup_method(self):
        from quant.portfolio_optimizer import PortfolioOptimizer
        self.optimizer = PortfolioOptimizer(risk_free_rate=0.06)
    
    def test_mean_variance(self):
        np.random.seed(42)
        returns = pd.DataFrame({
            'A': np.random.randn(100) * 0.02,
            'B': np.random.randn(100) * 0.015,
        })
        
        result = self.optimizer.optimize_mean_variance(returns)
        assert abs(sum(result.weights.values()) - 1.0) < 0.01
        assert result.method == 'Mean-Variance'
    
    def test_hrp(self):
        np.random.seed(42)
        returns = pd.DataFrame({
            'A': np.random.randn(100) * 0.02,
            'B': np.random.randn(100) * 0.015,
            'C': np.random.randn(100) * 0.025,
        })
        
        result = self.optimizer.optimize_hrp(returns)
        assert abs(sum(result.weights.values()) - 1.0) < 0.01
        assert result.method == 'HRP'


class TestRiskCalculator:
    """Test risk metrics calculator"""
    
    def setup_method(self):
        from quant.risk_metrics import RiskCalculator
        self.calculator = RiskCalculator(risk_free_rate=0.06)
    
    def test_risk_metrics(self):
        np.random.seed(42)
        returns = pd.Series(np.random.randn(252) * 0.015 + 0.0003)
        
        metrics = self.calculator.calculate(returns)
        
        assert metrics.volatility > 0
        assert metrics.var_95 < 0  # VaR should be negative
        assert metrics.sharpe != 0
        assert metrics.max_drawdown <= 0  # Drawdown is negative
    
    def test_beta_calculation(self):
        np.random.seed(42)
        returns = pd.Series(np.random.randn(100) * 0.015)
        benchmark = pd.Series(np.random.randn(100) * 0.012)
        
        beta = self.calculator._beta(returns, benchmark)
        assert isinstance(beta, float)


class TestSignalGenerator:
    """Test signal generator"""
    
    def setup_method(self):
        from quant.signal_generator import SignalGenerator
        self.generator = SignalGenerator()
    
    def test_generate_signal(self):
        np.random.seed(42)
        dates = pd.date_range('2023-06-01', '2024-01-01', freq='B')
        prices = 4500 + np.cumsum(np.random.randn(len(dates)) * 30)
        
        price_data = pd.DataFrame({
            'open': prices * 0.99,
            'high': prices * 1.01,
            'low': prices * 0.98,
            'close': prices,
            'volume': np.random.randint(1000000, 5000000, len(dates))
        }, index=dates)
        
        fundamentals = {
            'pe_ratio': 12.5,
            'pb_ratio': 1.8,
            'roe': 18.5,
            'debt_equity': 0.8,
            'current_ratio': 2.1,
            'sector_pe': 15.0
        }
        
        signal = self.generator.generate('BBRI', price_data, fundamentals, 35, 5)
        
        assert signal.symbol == 'BBRI'
        assert -100 <= signal.score <= 100
        assert 0 <= signal.confidence <= 100


class TestDCFModel:
    """Test DCF valuation model"""
    
    def setup_method(self):
        from quant.dcf_model import DCFModel
        self.model = DCFModel()
    
    def test_dcf_calculation(self):
        result = self.model.calculate(
            symbol='TEST',
            current_price=5000,
            shares_outstanding=100e9,
            fcf_last=10e12,
            growth_rates=[0.10, 0.08, 0.06, 0.05, 0.04],
            beta=1.0,
            debt=5e12,
            cash=2e12
        )
        
        assert result.fair_value > 0
        assert result.projection_years == 5
        assert len(result.projected_fcf) == 5
    
    def test_monte_carlo(self):
        result = self.model.monte_carlo_simulation(
            symbol='TEST',
            current_price=5000,
            shares_outstanding=100e9,
            fcf_last=10e12,
            base_growth_rates=[0.10, 0.08, 0.06],
            simulations=100
        )
        
        assert result['mean'] > 0
        assert result['p5'] < result['p95']


class TestScreener:
    """Test advanced screener"""
    
    def setup_method(self):
        from analytics.screener import AdvancedScreener
        self.screener = AdvancedScreener(db_path='/tmp/test_screener_phase2.db')
    
    def test_preset_screening(self):
        stocks = [
            {'symbol': 'A', 'pe_ratio': 10, 'dividend_yield': 5, 'pb_ratio': 1.5},
            {'symbol': 'B', 'pe_ratio': 25, 'dividend_yield': 1, 'pb_ratio': 4.0},
        ]
        
        results = self.screener.screen(stocks, preset='value')
        assert len(results) == 1
        assert results[0]['symbol'] == 'A'
    
    def test_save_load_config(self):
        from analytics.screener import ScreenerConfig, ScreenerFilter
        
        config = ScreenerConfig(
            name='Test',
            filters=[ScreenerFilter('PE', 'pe_ratio', 'lt', 15.0)]
        )
        
        config_id = self.screener.save_config(config)
        loaded = self.screener.load_config(config_id)
        
        assert loaded is not None
        assert loaded.name == 'Test'


class TestSentimentPipeline:
    """Test sentiment pipeline"""
    
    @pytest.mark.slow
    def test_pipeline_initialization(self):
        from ai.sentiment_pipeline import SentimentPipeline
        pipeline = SentimentPipeline(use_llm=False)
        assert pipeline.finbert is not None
    
    def test_sector_mapper(self):
        from ai.sentiment_pipeline import SectorMapper
        mapper = SectorMapper()
        
        sectors = mapper.detect_sectors("Bank BCA melaporkan laba naik")
        assert 'Banking' in sectors or 'FINANCE' in [s.upper() for s in sectors]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
