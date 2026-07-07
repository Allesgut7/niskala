# Niskala - Portfolio Optimizer
# Version: 1.0.0
# Multiple optimization methods: Mean-Variance, HRP, Black-Litterman

from typing import Dict, List, Optional
from dataclasses import dataclass
import pandas as pd
import numpy as np
from scipy.optimize import minimize
import logging


@dataclass
class OptimizationResult:
    """Portfolio optimization result"""
    weights: Dict[str, float]
    expected_return: float
    volatility: float
    sharpe_ratio: float
    method: str


class PortfolioOptimizer:
    """Multi-method portfolio optimizer"""
    
    def __init__(self, risk_free_rate: float = 0.06):
        """Initialize optimizer
        
        Args:
            risk_free_rate: Risk-free rate (e.g., Indonesian bond yield)
        """
        self.risk_free_rate = risk_free_rate
        logging.info(f"Portfolio optimizer initialized (rf={risk_free_rate:.2%})")
    
    def optimize_mean_variance(
        self,
        returns: pd.DataFrame,
        target_return: Optional[float] = None,
        max_weight: float = 0.3,
        min_weight: float = 0.0
    ) -> OptimizationResult:
        """Mean-Variance optimization (Markowitz)
        
        Args:
            returns: DataFrame of historical returns (symbols as columns)
            target_return: Target portfolio return, or None for max Sharpe
            max_weight: Maximum weight per asset
            min_weight: Minimum weight per asset
            
        Returns:
            OptimizationResult
        """
        n_assets = len(returns.columns)
        
        # Calculate mean returns and covariance
        mean_returns = returns.mean() * 252  # Annualized
        cov_matrix = returns.cov() * 252     # Annualized
        
        # Objective function
        def portfolio_volatility(weights):
            return np.sqrt(weights @ cov_matrix @ weights)
        
        def neg_sharpe(weights):
            ret = weights @ mean_returns
            vol = portfolio_volatility(weights)
            return -(ret - self.risk_free_rate) / vol
        
        # Constraints
        constraints = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}  # Weights sum to 1
        ]
        
        if target_return:
            constraints.append({
                'type': 'eq',
                'fun': lambda w: w @ mean_returns - target_return
            })
        
        # Bounds
        bounds = tuple((min_weight, max_weight) for _ in range(n_assets))
        
        # Initial guess
        w0 = np.array([1/n_assets] * n_assets)
        
        # Optimize
        result = minimize(
            neg_sharpe if not target_return else portfolio_volatility,
            w0,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        if not result.success:
            logging.warning(f"Optimization failed: {result.message}")
        
        weights = dict(zip(returns.columns, result.x))
        
        # Calculate metrics
        final_weights = np.array(list(weights.values()))
        exp_return = final_weights @ mean_returns
        volatility = portfolio_volatility(final_weights)
        sharpe = (exp_return - self.risk_free_rate) / volatility
        
        return OptimizationResult(
            weights=weights,
            expected_return=exp_return,
            volatility=volatility,
            sharpe_ratio=sharpe,
            method='Mean-Variance'
        )
    
    def optimize_hrp(self, returns: pd.DataFrame) -> OptimizationResult:
        """Hierarchical Risk Parity (HRP)
        
        Args:
            returns: DataFrame of historical returns
            
        Returns:
            OptimizationResult
        """
        # Calculate correlation and covariance
        corr = returns.corr()
        cov = returns.cov() * 252  # Annualized
        
        # Compute distance matrix
        dist = np.sqrt((1 - corr) / 2)
        
        # Hierarchical clustering
        from scipy.cluster.hierarchy import linkage, dendrogram
        from scipy.spatial.distance import squareform
        
        link = linkage(squareform(dist), method='single')
        
        # Get quasi-diagonalization order
        sortIx = self._get_quasi_diag(link)
        sortIx = corr.index[sortIx].tolist()
        
        # Recursive bisection
        weights = self._hrp_recursive_bisection(cov, sortIx)
        
        # Calculate metrics
        mean_returns = returns.mean() * 252
        final_weights = np.array([weights[s] for s in returns.columns])
        
        exp_return = final_weights @ mean_returns
        volatility = np.sqrt(final_weights @ cov @ final_weights)
        sharpe = (exp_return - self.risk_free_rate) / volatility
        
        return OptimizationResult(
            weights=weights,
            expected_return=exp_return,
            volatility=volatility,
            sharpe_ratio=sharpe,
            method='HRP'
        )
    
    def optimize_black_litterman(
        self,
        returns: pd.DataFrame,
        market_caps: Dict[str, float],
        views: Optional[Dict[str, float]] = None,
        view_confidence: float = 0.25
    ) -> OptimizationResult:
        """Black-Litterman optimization
        
        Args:
            returns: DataFrame of historical returns
            market_caps: Dict of market capitalizations
            views: Dict of expected returns (your views)
            view_confidence: Confidence in views (0-1)
            
        Returns:
            OptimizationResult
        """
        # Market-cap weighted portfolio (equilibrium)
        total_cap = sum(market_caps.values())
        market_weights = {s: market_caps[s] / total_cap for s in returns.columns}
        
        # Calculate covariance
        cov = returns.cov() * 252
        
        # Implied equilibrium returns (reverse optimization)
        delta = 2.5  # Risk aversion coefficient
        w_mkt = np.array([market_weights[s] for s in returns.columns])
        pi = delta * cov @ w_mkt  # Implied returns
        
        if views:
            # Incorporate views using Black-Litterman formula
            tau = view_confidence
            
            # P matrix (pick matrix)
            P = np.eye(len(returns.columns))
            
            # Q vector (view returns)
            Q = np.array([views.get(s, pi[i]) for i, s in enumerate(returns.columns)])
            
            # Omega (uncertainty in views)
            omega = np.eye(len(returns.columns)) * tau
            
            # Black-Litterman formula
            M_inv = np.linalg.inv(tau * cov)
            omega_inv = np.linalg.inv(omega)
            
            posterior_returns = np.linalg.inv(M_inv + P.T @ omega_inv @ P) @ \
                                (M_inv @ pi + P.T @ omega_inv @ Q)
        else:
            posterior_returns = pi
        
        # Optimize with posterior returns
        def neg_utility(w):
            return -(w @ posterior_returns - 0.5 * delta * w @ cov @ w)
        
        constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]
        bounds = tuple((0, 0.3) for _ in range(len(returns.columns)))
        w0 = w_mkt
        
        result = minimize(neg_utility, w0, method='SLSQP', bounds=bounds, constraints=constraints)
        
        weights = dict(zip(returns.columns, result.x))
        
        # Calculate metrics
        final_weights = np.array(list(weights.values()))
        exp_return = final_weights @ posterior_returns
        volatility = np.sqrt(final_weights @ cov @ final_weights)
        sharpe = (exp_return - self.risk_free_rate) / volatility
        
        return OptimizationResult(
            weights=weights,
            expected_return=exp_return,
            volatility=volatility,
            sharpe_ratio=sharpe,
            method='Black-Litterman'
        )
    
    def _get_quasi_diag(self, link):
        """Get quasi-diagonal order from linkage matrix"""
        link = link.astype(int)
        sortIx = pd.Series([link[-1, 0], link[-1, 1]])
        numItems = link[-1, 3]
        
        while sortIx.max() >= numItems:
            sortIx.index = range(0, sortIx.shape[0] * 2, 2)
            df0 = sortIx[sortIx >= numItems]
            i = df0.index
            j = df0.values - numItems
            sortIx[i] = link[j, 0]
            df0 = pd.Series(link[j, 1], index=i + 1)
            sortIx = pd.concat([sortIx, df0])
            sortIx = sortIx.sort_index()
            sortIx.index = range(sortIx.shape[0])
        
        return sortIx.tolist()
    
    def _hrp_recursive_bisection(self, cov, sortIx):
        """Recursive bisection for HRP"""
        weights = pd.Series(1.0, index=sortIx)
        clusters = [sortIx]
        
        while len(clusters) > 0:
            clusters = [c[i:j] for c in clusters
                       for i, j in ((0, len(c) // 2), (len(c) // 2, len(c)))
                       if len(c) > 1]
            
            for i in range(0, len(clusters), 2):
                cluster0 = clusters[i]
                cluster1 = clusters[i + 1]
                
                # Cluster variance
                cov0 = cov.loc[cluster0, cluster0]
                cov1 = cov.loc[cluster1, cluster1]
                
                w0 = weights[cluster0].values
                w1 = weights[cluster1].values
                
                var0 = w0 @ cov0 @ w0
                var1 = w1 @ cov1 @ w1
                
                # Allocate weight
                alpha = 1 - var0 / (var0 + var1)
                
                weights[cluster0] *= alpha
                weights[cluster1] *= 1 - alpha
        
        return weights.to_dict()


# Test
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    # Generate sample returns
    np.random.seed(42)
    dates = pd.date_range('2023-01-01', '2024-01-01', freq='D')
    symbols = ['BBCA', 'BBRI', 'BMRI', 'TLKM', 'ASII']
    
    returns_data = {}
    for sym in symbols:
        returns_data[sym] = np.random.randn(len(dates)) * 0.02
    
    returns = pd.DataFrame(returns_data, index=dates)
    
    # Market caps (in IDR trillion)
    market_caps = {
        'BBCA': 1000,
        'BBRI': 800,
        'BMRI': 600,
        'TLKM': 400,
        'ASII': 300
    }
    
    # Initialize optimizer
    optimizer = PortfolioOptimizer(risk_free_rate=0.06)
    
    print("\n=== Mean-Variance Optimization (Max Sharpe) ===")
    mv_result = optimizer.optimize_mean_variance(returns)
    print(f"Expected Return: {mv_result.expected_return:.2%}")
    print(f"Volatility: {mv_result.volatility:.2%}")
    print(f"Sharpe Ratio: {mv_result.sharpe_ratio:.2f}")
    print("Weights:")
    for sym, weight in sorted(mv_result.weights.items(), key=lambda x: x[1], reverse=True):
        print(f"  {sym}: {weight:.2%}")
    
    print("\n=== Hierarchical Risk Parity ===")
    hrp_result = optimizer.optimize_hrp(returns)
    print(f"Expected Return: {hrp_result.expected_return:.2%}")
    print(f"Volatility: {hrp_result.volatility:.2%}")
    print(f"Sharpe Ratio: {hrp_result.sharpe_ratio:.2f}")
    print("Weights:")
    for sym, weight in sorted(hrp_result.weights.items(), key=lambda x: x[1], reverse=True):
        print(f"  {sym}: {weight:.2%}")
    
    print("\n=== Black-Litterman (No Views) ===")
    bl_result = optimizer.optimize_black_litterman(returns, market_caps)
    print(f"Expected Return: {bl_result.expected_return:.2%}")
    print(f"Volatility: {bl_result.volatility:.2%}")
    print(f"Sharpe Ratio: {bl_result.sharpe_ratio:.2f}")
    print("Weights:")
    for sym, weight in sorted(bl_result.weights.items(), key=lambda x: x[1], reverse=True):
        print(f"  {sym}: {weight:.2%}")
