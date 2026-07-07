// Niskala - Sentiment Analyzer Implementation
// Version: 1.0.0

#include "core/ai/sentiment_analyzer.h"
#include <string>

namespace niskala {

struct SentimentAnalyzer::Impl {
    // TODO: Python/FinBERT process handle
};

SentimentAnalyzer::SentimentAnalyzer()
    : impl_(std::make_unique<Impl>()) {
}

SentimentAnalyzer::~SentimentAnalyzer() = default;

int SentimentAnalyzer::analyze(const std::string& /*text*/) {
    // TODO: Call FinBERT via Python subprocess
    // Returns score from -100 (bearish) to +100 (bullish)
    return 0;
}

} // namespace niskala
