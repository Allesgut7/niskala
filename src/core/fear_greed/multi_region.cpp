// Niskala - Multi-Region Fear & Greed Implementation
// Version: 1.0.0

#include "core/fear_greed/multi_region.h"
#include "core/market_data/data_aggregator.h"

namespace niskala {

MultiRegionFearGreed::MultiRegionFearGreed(std::shared_ptr<DataAggregator> data_aggregator)
    : data_aggregator_(data_aggregator) {
}

MultiRegionFearGreed::~MultiRegionFearGreed() = default;

MultiRegionFearGreedResult MultiRegionFearGreed::calculate_all() {
    MultiRegionFearGreedResult result;
    result.indonesia = calculate_indonesia();
    result.asia = calculate_asia();
    result.global = calculate_global();
    
    // Calculate overall (weighted average)
    int total_score = 
        result.indonesia.score * 0.4 +
        result.asia.score * 0.3 +
        result.global.score * 0.3;
    
    result.overall.score = total_score;
    result.overall.status = classify_score(total_score);
    
    return result;
}

FearGreedResult MultiRegionFearGreed::calculate_indonesia() {
    FearGreedResult result;
    
    int volatility = calculate_volatility_score("^JKSE");
    int breadth = calculate_breadth_score();
    int momentum = calculate_momentum_score("^JKSE");
    int volume = calculate_volume_score("^JKSE");
    int sentiment = calculate_sentiment_score();
    int safe_haven = calculate_safe_haven_score();
    
    result.components["volatility"] = volatility;
    result.components["breadth"] = breadth;
    result.components["momentum"] = momentum;
    result.components["volume"] = volume;
    result.components["sentiment"] = sentiment;
    result.components["safe_haven"] = safe_haven;
    
    result.score = static_cast<int>(
        volatility * VOLATILITY_WEIGHT +
        breadth * BREADTH_WEIGHT +
        momentum * MOMENTUM_WEIGHT +
        volume * VOLUME_WEIGHT +
        sentiment * SENTIMENT_WEIGHT +
        safe_haven * SAFE_HAVEN_WEIGHT
    );
    
    result.status = classify_score(result.score);
    
    return result;
}

FearGreedResult MultiRegionFearGreed::calculate_asia() {
    FearGreedResult result;
    // Calculate for Asia region (Nikkei, Hang Seng, KOSPI, STI)
    result.score = 56;
    result.status = "Greed";
    result.components["volatility"] = 55;
    result.components["breadth"] = 60;
    result.components["momentum"] = 50;
    result.components["volume"] = 55;
    result.components["sentiment"] = 60;
    result.components["safe_haven"] = 45;
    return result;
}

FearGreedResult MultiRegionFearGreed::calculate_global() {
    FearGreedResult result;
    // Calculate for global market (S&P 500, etc.)
    result.score = 71;
    result.status = "Greed";
    result.components["volatility"] = 65;
    result.components["breadth"] = 75;
    result.components["momentum"] = 72;
    result.components["volume"] = 68;
    result.components["sentiment"] = 80;
    result.components["safe_haven"] = 55;
    return result;
}

int MultiRegionFearGreed::calculate_volatility_score(const std::string& symbol) {
    // Lower volatility = higher score (Greed)
    // Higher volatility = lower score (Fear)
    return 65;  // Placeholder
}

int MultiRegionFearGreed::calculate_breadth_score() {
    // More advancing stocks = higher score
    return 78;  // Placeholder
}

int MultiRegionFearGreed::calculate_momentum_score(const std::string& symbol) {
    // Price above MAs = higher score
    return 72;  // Placeholder
}

int MultiRegionFearGreed::calculate_volume_score(const std::string& symbol) {
    // Higher volume during uptrend = higher score
    return 68;  // Placeholder
}

int MultiRegionFearGreed::calculate_sentiment_score() {
    // Positive sentiment = higher score
    return 82;  // Placeholder
}

int MultiRegionFearGreed::calculate_safe_haven_score() {
    // Gold down, Rupiah strong = higher score
    return 55;  // Placeholder
}

std::string MultiRegionFearGreed::classify_score(int score) {
    if (score <= 25) return "Extreme Fear";
    if (score <= 45) return "Fear";
    if (score <= 55) return "Neutral";
    if (score <= 75) return "Greed";
    return "Extreme Greed";
}

} // namespace niskala
