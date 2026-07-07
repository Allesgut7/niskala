// Niskala - Risk Metrics Header
// Version: 1.0.0

#pragma once

#include "core/common/types.h"
#include <vector>
#include <string>
#include <memory>

namespace niskala {

struct RiskReport {
    double var_95 = 0.0;        // Value at Risk (95%)
    double var_99 = 0.0;        // Value at Risk (99%)
    double cvar_95 = 0.0;       // Conditional VaR
    double beta = 0.0;
    double volatility = 0.0;
    double max_drawdown = 0.0;
    double sharpe_ratio = 0.0;
};

class RiskMetrics {
public:
    RiskMetrics();
    ~RiskMetrics();

    // Calculate risk metrics for a symbol
    RiskReport calculate(const std::string& symbol);

    // Calculate portfolio risk
    RiskReport calculate_portfolio(const std::vector<std::string>& symbols,
                                   const std::vector<double>& weights);

private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace niskala
