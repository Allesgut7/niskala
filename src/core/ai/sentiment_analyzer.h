// Niskala - Sentiment Analyzer Header
// Version: 1.0.0

#pragma once

#include "core/common/types.h"
#include <string>
#include <memory>

namespace niskala {

class SentimentAnalyzer {
public:
    SentimentAnalyzer();
    ~SentimentAnalyzer();

    // Analyze text sentiment, returns score from -100 to +100
    int analyze(const std::string& text);

private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace niskala
