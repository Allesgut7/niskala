// Niskala - Fear & Greed Calculator Implementation
// Version: 1.0.0

#include "core/fear_greed/calculator.h"
#include "core/common/logger.h"

namespace niskala {

FearGreedResult FearGreedCalculator::calculate(const std::string& region) {
    FearGreedResult result;
    
    std::string index;
    if (region == "indonesia") index = "^JKSE";
    else if (region == "asia") index = "^N225";
    else index = "^GSPC";
    
    int volatility = calc_volatility(index);
    int breadth    = calc_breadth(index);
    int momentum   = calc_momentum(index);
    int volume     = calc_volume(index);
    int sentiment  = calc_sentiment();
    int safe_haven = calc_safe_haven(index);
    
    result.components["volatility"] = volatility;
    result.components["breadth"]    = breadth;
    result.components["momentum"]   = momentum;
    result.components["volume"]     = volume;
    result.components["sentiment"]  = sentiment;
    result.components["safe_haven"] = safe_haven;
    
    result.score = static_cast<int>(
        volatility * 0.25 +
        breadth * 0.15 +
        momentum * 0.25 +
        volume * 0.15 +
        sentiment * 0.10 +
        safe_haven * 0.10
    );
    
    result.status = (result.score <= 25) ? "Extreme Fear" :
                    (result.score <= 45) ? "Fear" :
                    (result.score <= 55) ? "Neutral" :
                    (result.score <= 75) ? "Greed" : "Extreme Greed";
    
    return result;
}

MultiRegionFearGreedResult FearGreedCalculator::calculate_all() {
    MultiRegionFearGreedResult result;
    result.indonesia = calculate("indonesia");
    result.asia = calculate("asia");
    result.global = calculate("global");
    
    result.overall.score = static_cast<int>(
        result.indonesia.score * 0.4 +
        result.asia.score * 0.3 +
        result.global.score * 0.3
    );
    result.overall.status = (result.overall.score <= 25) ? "Extreme Fear" :
                            (result.overall.score <= 45) ? "Fear" :
                            (result.overall.score <= 55) ? "Neutral" :
                            (result.overall.score <= 75) ? "Greed" : "Extreme Greed";
    
    return result;
}

int FearGreedCalculator::calc_volatility(const std::string& symbol) {
    // Placeholder - lower vol = higher score
    return 65;
}

int FearGreedCalculator::calc_breadth(const std::string& symbol) {
    return 70;
}

int FearGreedCalculator::calc_momentum(const std::string& symbol) {
    return 72;
}

int FearGreedCalculator::calc_volume(const std::string& symbol) {
    return 68;
}

int FearGreedCalculator::calc_sentiment() {
    return 60;
}

int FearGreedCalculator::calc_safe_haven(const std::string& symbol) {
    return 55;
}

} // namespace niskala
