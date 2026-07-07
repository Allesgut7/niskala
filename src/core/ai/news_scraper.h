// Niskala - News Scraper Header
// Version: 1.0.0

#pragma once

#include "core/common/types.h"
#include <vector>
#include <string>
#include <memory>

namespace niskala {

class NewsScraper {
public:
    NewsScraper();
    ~NewsScraper();

    // Fetch recent news articles
    std::vector<NewsArticle> fetch_news();

    // Fetch news for a specific symbol
    std::vector<NewsArticle> fetch_news_for(const std::string& symbol);

private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace niskala
