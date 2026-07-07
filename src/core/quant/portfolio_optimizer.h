// Niskala - Portfolio Optimizer Header
// Version: 1.0.0

#pragma once

#include "core/common/types.h"
#include <vector>
#include <string>
#include <map>
#include <memory>

namespace niskala {

struct OptimizedPortfolio {
    std::map<std::string, double> weights; // symbol -> weight (0.0 to 1.0)
    double expected_return = 0.0;
    double expected_risk = 0.0;
    double sharpe_ratio = 0.0;
};

class PortfolioOptimizer {
public:
    PortfolioOptimizer();
    ~PortfolioOptimizer();

    // Run mean-variance optimization
    OptimizedPortfolio optimize(const std::vector<std::string>& symbols);

private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace niskala
