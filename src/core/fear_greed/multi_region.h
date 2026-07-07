// Niskala - Multi-Region Fear & Greed Header
// Version: 1.0.0

#pragma once

#include <memory>
#include <string>
#include <map>

namespace niskala {

struct FearGreedResult {
    int score;           // 0-100
    std::string status;  // Extreme Fear, Fear, Neutral, Greed, Extreme Greed
    std::map<std::string, int> components;  // Individual indicator scores
};

struct MultiRegionFearGreedResult {
    FearGreedResult indonesia;
    FearGreedResult asia;
    FearGreedResult global;
    FearGreedResult overall;
};

class DataAggregator;  // Forward declaration

class MultiRegionFearGreed {
public:
    MultiRegionFearGreed(std::shared_ptr<DataAggregator> data_aggregator);
    ~MultiRegionFearGreed();
    
    // Calculate Fear & Greed for all regions
    MultiRegionFearGreedResult calculate_all();
    
    // Calculate Fear & Greed for specific region
    FearGreedResult calculate_indonesia();
    FearGreedResult calculate_asia();
    FearGreedResult calculate_global();
    
private:
    std::shared_ptr<DataAggregator> data_aggregator_;
    
    // Indicator weights
    static constexpr double VOLATILITY_WEIGHT = 0.20;
    static constexpr double BREADTH_WEIGHT = 0.20;
    static constexpr double MOMENTUM_WEIGHT = 0.20;
    static constexpr double VOLUME_WEIGHT = 0.15;
    static constexpr double SENTIMENT_WEIGHT = 0.15;
    static constexpr double SAFE_HAVEN_WEIGHT = 0.10;
    
    // Helper methods
    int calculate_volatility_score(const std::string& symbol);
    int calculate_breadth_score();
    int calculate_momentum_score(const std::string& symbol);
    int calculate_volume_score(const std::string& symbol);
    int calculate_sentiment_score();
    int calculate_safe_haven_score();
    
    std::string classify_score(int score);
};

} // namespace niskala
