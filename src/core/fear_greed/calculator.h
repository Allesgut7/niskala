// Niskala - Fear & Greed Calculator Header
// Version: 1.0.0

#pragma once

#include "core/fear_greed/multi_region.h"
#include <string>

namespace niskala {

class FearGreedCalculator {
public:
    FearGreedCalculator() = default;
    ~FearGreedCalculator() = default;

    FearGreedResult calculate(const std::string& region);
    MultiRegionFearGreedResult calculate_all();

private:
    int calc_volatility(const std::string& symbol);
    int calc_breadth(const std::string& symbol);
    int calc_momentum(const std::string& symbol);
    int calc_volume(const std::string& symbol);
    int calc_sentiment();
    int calc_safe_haven(const std::string& symbol);
};

} // namespace niskala
