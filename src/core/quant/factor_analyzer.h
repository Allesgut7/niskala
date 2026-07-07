// Niskala - Factor Analyzer Header
// Version: 1.0.0

#pragma once

#include "core/common/types.h"
#include <vector>
#include <string>
#include <memory>

namespace niskala {

struct FactorExposure {
    std::string factor_name;
    double exposure = 0.0;
    double t_stat = 0.0;
    double p_value = 0.0;
};

class FactorAnalyzer {
public:
    FactorAnalyzer();
    ~FactorAnalyzer();

    // Analyze factor exposures for a stock
    std::vector<FactorExposure> analyze(const std::string& symbol);

private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace niskala
