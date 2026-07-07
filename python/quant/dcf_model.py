# Niskala - DCF Valuation Model
# Version: 1.0.0
# Discounted Cash Flow for Indonesian stocks

from typing import Dict, List, Optional
from dataclasses import dataclass
import numpy as np
import logging


@dataclass
class DCFResult:
    """DCF valuation result"""
    symbol: str
    fair_value: float
    current_price: float
    upside_downside: float      # % difference
    intrinsic_value: float
    growth_rate: float
    discount_rate: float
    terminal_growth: float
    projection_years: int
    projected_fcf: List[float]
    terminal_value: float
    enterprise_value: float
    equity_value: float
    shares_outstanding: float
    margin_of_safety: float


class DCFModel:
    """Discounted Cash Flow valuation model
    
    Adapted for Indonesian market:
    - Uses WACC based on Indonesian risk-free rate (BI Rate)
    - Accounts for IDX-specific tax rates
    - Supports Rupiah-denominated cash flows
    """
    
    # Indonesian market parameters
    DEFAULT_RISK_FREE = 0.06       # BI Rate ~6%
    DEFAULT_MARKET_RISK_PREM = 0.06  # Indonesia ERP ~6%
    DEFAULT_TAX_RATE = 0.22        # Indonesian corporate tax 22%
    DEFAULT_TERMINAL_GROWTH = 0.03  # Long-term GDP growth
    
    def __init__(
        self,
        risk_free_rate: float = DEFAULT_RISK_FREE,
        market_risk_premium: float = DEFAULT_MARKET_RISK_PREM,
        tax_rate: float = DEFAULT_TAX_RATE,
        terminal_growth: float = DEFAULT_TERMINAL_GROWTH
    ):
        self.risk_free_rate = risk_free_rate
        self.market_risk_premium = market_risk_premium
        self.tax_rate = tax_rate
        self.terminal_growth = terminal_growth
        
        logging.info(f"DCF model initialized (rf={risk_free_rate:.2%}, ERP={market_risk_premium:.2%})")
    
    def calculate(
        self,
        symbol: str,
        current_price: float,
        shares_outstanding: float,
        fcf_last: float,                    # Last free cash flow (IDR)
        growth_rates: List[float],           # Expected growth rates for projection years
        beta: float = 1.0,
        debt: float = 0.0,                  # Total debt (IDR)
        cash: float = 0.0,                  # Cash and equivalents (IDR)
        wacc_override: Optional[float] = None
    ) -> DCFResult:
        """Calculate DCF valuation
        
        Args:
            symbol: Stock ticker
            current_price: Current market price
            shares_outstanding: Number of shares
            fcf_last: Last year's free cash flow
            growth_rates: List of growth rates for each projection year
            beta: Stock beta
            debt: Total debt
            cash: Cash and equivalents
            wacc_override: Override WACC calculation
            
        Returns:
            DCFResult with valuation
        """
        projection_years = len(growth_rates)
        
        # Calculate WACC
        if wacc_override:
            wacc = wacc_override
        else:
            cost_of_equity = self.risk_free_rate + beta * self.market_risk_premium
            cost_of_debt = self.risk_free_rate + 0.02  # Spread over risk-free
            
            # Assume 70% equity, 30% debt (typical IDX)
            equity_weight = 0.7
            debt_weight = 0.3
            
            wacc = (
                equity_weight * cost_of_equity +
                debt_weight * cost_of_debt * (1 - self.tax_rate)
            )
        
        # Project FCFs
        projected_fcf = []
        current_fcf = fcf_last
        
        for i in range(projection_years):
            current_fcf *= (1 + growth_rates[i])
            projected_fcf.append(current_fcf)
        
        # Terminal value (Gordon Growth Model)
        terminal_fcf = projected_fcf[-1] * (1 + self.terminal_growth)
        terminal_value = terminal_fcf / (wacc - self.terminal_growth)
        
        # Discount cash flows
        pv_fcfs = []
        for i, fcf in enumerate(projected_fcf):
            pv = fcf / ((1 + wacc) ** (i + 1))
            pv_fcfs.append(pv)
        
        pv_terminal = terminal_value / ((1 + wacc) ** projection_years)
        
        # Enterprise value
        enterprise_value = sum(pv_fcfs) + pv_terminal
        
        # Equity value
        equity_value = enterprise_value - debt + cash
        
        # Fair value per share
        fair_value = equity_value / shares_outstanding
        
        # Upside/downside
        upside_downside = ((fair_value - current_price) / current_price) * 100
        
        # Margin of safety
        margin_of_safety = ((fair_value - current_price) / fair_value) * 100 if fair_value > 0 else 0
        
        return DCFResult(
            symbol=symbol,
            fair_value=fair_value,
            current_price=current_price,
            upside_downside=upside_downside,
            intrinsic_value=fair_value,
            growth_rate=np.mean(growth_rates),
            discount_rate=wacc,
            terminal_growth=self.terminal_growth,
            projection_years=projection_years,
            projected_fcf=projected_fcf,
            terminal_value=terminal_value,
            enterprise_value=enterprise_value,
            equity_value=equity_value,
            shares_outstanding=shares_outstanding,
            margin_of_safety=margin_of_safety
        )
    
    def sensitivity_analysis(
        self,
        symbol: str,
        current_price: float,
        shares_outstanding: float,
        fcf_last: float,
        growth_rates: List[float],
        beta: float = 1.0,
        debt: float = 0.0,
        cash: float = 0.0,
        wacc_range: List[float] = None,
        growth_range: List[float] = None
    ) -> Dict:
        """Sensitivity analysis on WACC and growth rate
        
        Returns:
            Dict with matrix of fair values
        """
        if wacc_range is None:
            wacc_range = [0.08, 0.09, 0.10, 0.11, 0.12]
        
        if growth_range is None:
            growth_range = [0.01, 0.02, 0.03, 0.04, 0.05]
        
        matrix = {}
        
        for wacc in wacc_range:
            for growth in growth_range:
                self.terminal_growth = growth
                result = self.calculate(
                    symbol, current_price, shares_outstanding,
                    fcf_last, growth_rates, beta, debt, cash,
                    wacc_override=wacc
                )
                matrix[(wacc, growth)] = result.fair_value
        
        # Reset terminal growth
        self.terminal_growth = self.DEFAULT_TERMINAL_GROWTH
        
        return {
            'wacc_range': wacc_range,
            'growth_range': growth_range,
            'matrix': matrix
        }
    
    def monte_carlo_simulation(
        self,
        symbol: str,
        current_price: float,
        shares_outstanding: float,
        fcf_last: float,
        base_growth_rates: List[float],
        beta: float = 1.0,
        debt: float = 0.0,
        cash: float = 0.0,
        simulations: int = 1000,
        growth_std: float = 0.05
    ) -> Dict:
        """Monte Carlo simulation for DCF
        
        Args:
            simulations: Number of simulations
            growth_std: Standard deviation of growth rates
            
        Returns:
            Dict with simulation results
        """
        fair_values = []
        
        np.random.seed(42)
        
        for _ in range(simulations):
            # Randomize growth rates
            randomized = [
                max(-0.5, min(1.0, g + np.random.normal(0, growth_std)))
                for g in base_growth_rates
            ]
            
            result = self.calculate(
                symbol, current_price, shares_outstanding,
                fcf_last, randomized, beta, debt, cash
            )
            fair_values.append(result.fair_value)
        
        fair_values = np.array(fair_values)
        
        return {
            'mean': float(fair_values.mean()),
            'median': float(np.median(fair_values)),
            'std': float(fair_values.std()),
            'p5': float(np.percentile(fair_values, 5)),
            'p25': float(np.percentile(fair_values, 25)),
            'p75': float(np.percentile(fair_values, 75)),
            'p95': float(np.percentile(fair_values, 95)),
            'min': float(fair_values.min()),
            'max': float(fair_values.max()),
            'simulations': simulations
        }


# Test
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    # Example: BBRI-like stock
    model = DCFModel()
    
    result = model.calculate(
        symbol='BBRI',
        current_price=4850,
        shares_outstanding=125_000_000_000,  # 125B shares
        fcf_last=45_000_000_000_000,          # 45T IDR
        growth_rates=[0.12, 0.10, 0.08, 0.07, 0.06],  # 5-year growth
        beta=0.9,
        debt=50_000_000_000_000,              # 50T IDR debt
        cash=20_000_000_000_000               # 20T IDR cash
    )
    
    print(f"\n=== DCF Valuation: {result.symbol} ===")
    print(f"Current Price: {result.current_price:,.0f} IDR")
    print(f"Fair Value: {result.fair_value:,.0f} IDR")
    print(f"Upside/Downside: {result.upside_downside:+.1f}%")
    print(f"Margin of Safety: {result.margin_of_safety:.1f}%")
    print(f"\nGrowth Rate (avg): {result.growth_rate:.1%}")
    print(f"Discount Rate (WACC): {result.discount_rate:.1%}")
    print(f"Terminal Growth: {result.terminal_growth:.1%}")
    print(f"\nProjected FCF (IDR):")
    for i, fcf in enumerate(result.projected_fcf, 1):
        print(f"  Year {i}: {fcf/1e12:.1f}T")
    print(f"\nTerminal Value: {result.terminal_value/1e12:.1f}T IDR")
    print(f"Enterprise Value: {result.enterprise_value/1e12:.1f}T IDR")
    print(f"Equity Value: {result.equity_value/1e12:.1f}T IDR")
    
    # Sensitivity analysis
    print(f"\n=== Sensitivity Analysis ===")
    sensitivity = model.sensitivity_analysis(
        'BBRI', 4850, 125e9, 45e12,
        [0.12, 0.10, 0.08, 0.07, 0.06],
        beta=0.9, debt=50e12, cash=20e12
    )
    
    print(f"WACC range: {[f'{w:.0%}' for w in sensitivity['wacc_range']]}")
    print(f"Growth range: {[f'{g:.0%}' for g in sensitivity['growth_range']]}")
    
    # Monte Carlo
    print(f"\n=== Monte Carlo Simulation (1000 runs) ===")
    mc = model.monte_carlo_simulation(
        'BBRI', 4850, 125e9, 45e12,
        [0.12, 0.10, 0.08, 0.07, 0.06],
        beta=0.9, debt=50e12, cash=20e12
    )
    
    print(f"Mean Fair Value: {mc['mean']:,.0f} IDR")
    print(f"Median Fair Value: {mc['median']:,.0f} IDR")
    print(f"5th Percentile: {mc['p5']:,.0f} IDR")
    print(f"95th Percentile: {mc['p95']:,.0f} IDR")
