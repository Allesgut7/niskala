// Niskala - Sentiment Provider Interface
// Version: 1.0.1

#ifndef NISKALA_CORE_MARKET_DATA_SENTIMENT_PROVIDER_H
#define NISKALA_CORE_MARKET_DATA_SENTIMENT_PROVIDER_H

#include "core/common/types.h"
#include <string>
#include <vector>
#include <map>
#include <memory>

namespace niskala {

class SentimentProvider {
public:
    SentimentProvider();
    ~SentimentProvider();
    
    // Fetch news with sentiment analysis
    std::vector<NewsArticle> fetch_news(int limit = 20);
    
    // Get cached news without refetching
    std::vector<NewsArticle> get_cached_news();
    
    bool is_available() const { return py_client_ != nullptr; }
    
private:
    void init_python();
    void* py_client_;
};

} // namespace niskala

#endif // NISKALA_CORE_MARKET_DATA_SENTIMENT_PROVIDER_H
