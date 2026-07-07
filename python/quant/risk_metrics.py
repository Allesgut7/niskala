# Niskala - Risk Metrics Calculator
# Version: 1.0.0
# VaR, CVaR, Sharpe, Sortino, Max DD, Beta, Alpha

from typing import Dict, List, Optional
from dataclasses import dataclass
import pandas as pd
import numpy as np
from scipy import stats
import logging


@dataclass
class RiskMetrics:
    """Container for risk metrics"""
    var_95: float = 0.0       # Value at Risk (95%)
    var_99: float = 0.0       # Value at Risk (99%)
    cvar_95: float = 0.0      # Conditional VaR (95%)
    cvar_99: float = 0.0      # Conditional VaR (99%)
    sharpe: float = 0.0       # Sharpe ratio
    sortino: float = 0.0      # Sortino ratio
    calmar: float = 0.0       # Calmar ratio
    max_drawdown: float = 0.0 # Maximum drawdown %
    max_dd_duration: int = 0  # Max drawdown duration (days)
    volatility: float = 0.0   # Annualized volatility
    beta: float = 0.0         # Beta vs benchmark
    alpha: float = 0.0        # Jensen's alpha
    tracking_error: float = 0.0
    information_ratio: float = 0.0


class RiskCalculator:
    """Calculate comprehensive risk metrics for portfolios and stocks"""
    
    def __init__(self, risk_free_rate: float = 0.06):
        """Initialize risk calculator
        
        Args:
            risk_free_rate: Annual risk-free rate (BI Rate ~6%)
        """
        self.risk_free_rate = risk_free_rate
        self.daily_rf = risk_free_rate / 252
        
        logging.info(f"Risk calculator initialized (rf={risk_free_rate:.2%})")
    
    def calculate(
        self,
        returns: pd.Series,
        benchmark: Optional[pd.Series] = None
    ) -> RiskMetrics:
        """Calculate all risk metrics
        
        Args:
            returns: Daily returns series
            benchmark: Benchmark daily returns (e.g., IHSG)
            
        Returns:
            RiskMetrics with all calculations
        """
        metrics = RiskMetrics()
        
        if len(returns) < 2:
            logging.warning("Insufficient data for risk calculation")
            return metrics
        
        # Annualized volatility
        metrics.volatility = returns.std() * np.sqrt(252)
        
        # Value at Risk (Historical)
        metrics.var_95 = self._var_historical(returns, 0.95)
        metrics.var_99 = self._var_historical(returns, 0.99)
        
        # Conditional VaR (Expected Shortfall)
        metrics.cvar_95 = self._cvar(returns, 0.95)
        metrics.cvar_99 = self._cvar(returns, 0.99)
        
        # Sharpe Ratio
        metrics.sharpe = self._sharpe_ratio(returns)
        
        # Sortino Ratio
        metrics.sortino = self._sortino_ratio(returns)
        
        # Maximum Drawdown
        dd_result = self._max_drawdown(returns)
        metrics.max_drawdown = dd_result['max_drawdown']
        metrics.max_dd_duration = dd_result['duration']
        
        # Calmar Ratio
        if metrics.max_drawdown != 0:
            annual_return = returns.mean() * 252
            metrics.calmar = annual_return / abs(metrics.max_drawdown)
        
        # Benchmark-relative metrics
        if benchmark is not None:
            aligned = pd.concat([returns, benchmark], axis=1).dropna()
            if len(aligned) > 1:
                port_returns = aligned.iloc[:, 0]
                bench_returns = aligned.iloc[:, 1]
                
                metrics.beta = self._beta(port_returns, bench_returns)
                metrics.alpha = self._alpha(port_returns, bench_returns, metrics.beta)
                metrics.tracking_error = self._tracking_error(port_returns, bench_returns)
                metrics.information_ratio = self._information_ratio(port_returns, bench_returns)
        
        return metrics
    
    def _var_historical(self, returns: pd.Series, confidence: float) -> float:
        """Historical Value at Risk
        
        Args:
            returns: Daily returns
            confidence: Confidence level (0.95 or 0.99)
            
        Returns:
            VaR as negative return (e.g., -0.03 = 3% loss)
        """
        return float(np.percentile(returns, (1 - confidence) * 100))
    
    def _cvar(self, returns: pd.Series, confidence: float) -> float:
        """Conditional VaR (Expected Shortfall)
        
        Args:
            returns: Daily returns
            confidence: Confidence level
            
        Returns:
            CVaR as negative return
        """
        var = self._var_historical(returns, confidence)
        return float(returns[returns <= var].mean())
    
    def _sharpe_ratio(self, returns: pd.Series) -> float:
        """Sharpe Ratio (annualized)"""
        excess_returns = returns - self.daily_rf
        
        if returns.std() == 0:
            return 0.0
        
        return float((excess_returns.mean() / returns.std()) * np.sqrt(252))
    
    def _sortino_ratio(self, returns: pd.Series) -> float:
        """Sortino Ratio (annualized, using downside deviation)"""
        excess_returns = returns - self.daily_rf
        downside_returns = returns[returns < 0]
        
        if len(downside_returns) == 0:
            return float('inf')
        
        downside_dev = downside_returns.std()
        
        if downside_dev == 0:
            return 0.0
        
        return float((excess_returns.mean() / downside_dev) * np.sqrt(252))
    
    def _max_drawdown(self, returns: pd.Series) -> Dict:
        """Calculate maximum drawdown and duration
        
        Returns:
            Dict with max_drawdown (negative %) and duration (days)
        """
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.cummax()
        drawdown = (cumulative - running_max) / running_max
        
        max_dd = float(drawdown.min())
        
        # Calculate duration
        is_in_dd = drawdown < 0
        dd_groups = (~is_in_dd).cumsum()
        
        if is_in_dd.any():
            dd_durations = is_in_dd.groupby(dd_groups).sum()
            max_duration = int(dd_durations.max())
        else:
            max_duration = 0
        
        return {
            'max_drawdown': max_dd,
            'duration': max_duration
        }
    
    def _beta(self, returns: pd.Series, benchmark: pd.Series) -> float:
        """Calculate beta vs benchmark"""
        covariance = np.cov(returns, benchmark)[0][1]
        benchmark_variance = benchmark.var()
        
        if benchmark_variance == 0:
            return 0.0
        
        return float(covariance / benchmark_variance)
    
    def _alpha(
        self,
        returns: pd.Series,
        benchmark: pd.Series,
        beta: float
    ) -> float:
        """Calculate Jensen's Alpha (annualized)"""
        portfolio_return = returns.mean() * 252
        benchmark_return = benchmark.mean() * 252
        
        alpha = portfolio_return - (self.risk_free_rate + beta * (benchmark_return - self.risk_free_rate))
        return float(alpha)
    
    def _tracking_error(
        self,
        returns: pd.Series,
        benchmark: pd.Series
    ) -> float:
        """Calculate tracking error (annualized)"""
        active_returns = returns - benchmark
        return float(active_returns.std() * np.sqrt(252))
    
    def _information_ratio(
        self,
        returns: pd.Series,
        benchmark: pd.Series
    ) -> float:
        """Calculate information ratio"""
        active_returns = returns - benchmark
        te = self._tracking_error(returns, benchmark)
        
        if te == 0:
            return 0.0
        
        return float((active_returns.mean() * 252) / te)
    
    def parametric_var(
        self,
        returns: pd.Series,
        confidence: float = 0.95,
        holding_period: int = 1
    ) -> float:
        """Parametric VaR (assumes normal distribution)
        
        Args:
            returns: Daily returns
            confidence: Confidence level
            holding_period: Holding period in days
            
        Returns:
            VaR as negative return
        """
        z_score = stats.norm.ppf(1 - confidence)
        daily_vol = returns.std()
        period_vol = daily_vol * np.sqrt(holding_period)
        
        return float(z_score * period_vol)
    
    def monte_carlo_var(
        self,
        returns: pd.Series,
        confidence: float = 0.95,
        simulations: int = 10000,
        holding_period: int = 1
    ) -> float:
        """Monte Carlo VaR simulation
        
        Args:
            returns: Daily returns
            confidence: Confidence level
            simulations: Number of simulations
            holding_period: Holding period in days
            
        Returns:
            VaR as negative return
        """
        mu = returns.mean()
        sigma = returns.std()
        
        # Generate random returns
        np.random.seed(42)
        random_returns = np.random.normal(
            mu * holding_period,
            sigma * np.sqrt(holding_period),
            simulations
        )
        
        return float(np.percentile(random_returns, (1 - confidence) * 100))


# Test
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    # Generate sample returns
    np.random.seed(42)
    dates = pd.date_range('2023-01-01', '2024-01-01', freq='B')
    
    # Portfolio returns (slightly positive drift)
    portfolio_returns = pd.Series(
        np.random.randn(len(dates)) * 0.015 + 0.0003,
        index=dates,
        name='Portfolio'
    )
    
    # Benchmark returns (IHSG-like)
    benchmark_returns = pd.Series(
        np.random.randn(len(dates)) * 0.012 + 0.0002,
        index=dates,
        name='IHSG'
    )
    
    # Calculate risk metrics
    calculator = RiskCalculator(risk_free_rate=0.06)
    metrics = calculator.calculate(portfolio_returns, benchmark_returns)
    
    print("\n=== Risk Metrics ===")
    print(f"Annualized Volatility: {metrics.volatility:.2%}")
    print(f"VaR (95%): {metrics.var_95:.2%}")
    print(f"VaR (99%): {metrics.var_99:.2%}")
    print(f"CVaR (95%): {metrics.cvar_95:.2%}")
    print(f"CVaR (99%): {metrics.cvar_99:.2%}")
    print(f"Sharpe Ratio: {metrics.sharpe:.2f}")
    print(f"Sortino Ratio: {metrics.sortino:.2f}")
    print(f"Calmar Ratio: {metrics.calmar:.2f}")
    print(f"Max Drawdown: {metrics.max_drawdown:.2%}")
    print(f"Max DD Duration: {metrics.max_dd_duration} days")
    print(f"Beta: {metrics.beta:.2f}")
    print(f"Alpha (Jensen): {metrics.alpha:.2%}")
    print(f"Tracking Error: {metrics.tracking_error:.2%}")
    print(f"Information Ratio: {metrics.information_ratio:.2f}")
    
    # Additional VaR methods
    print(f"\nParametric VaR (95%): {calculator.parametric_var(portfolio_returns, 0.95):.2%}")
    print(f"Monte Carlo VaR (95%): {calculator.monte_carlo_var(portfolio_returns, 0.95):.2%}")
