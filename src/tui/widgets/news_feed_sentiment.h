// Niskala - News Feed Sentiment Widget Header
// Version: 1.0.0

#pragma once

#include "core/common/types.h"
#include <ftxui/ftxui.hpp>
#include <vector>
#include <string>

namespace niskala {

using namespace ftxui;

class NewsFeedSentiment {
public:
    NewsFeedSentiment() = default;
    ~NewsFeedSentiment() = default;

    void set_articles(const std::vector<NewsArticle>& articles);
    Element render();

private:
    std::vector<NewsArticle> articles_;
    int bullish_count_ = 0;
    int bearish_count_ = 0;
    int neutral_count_ = 0;
};

} // namespace niskala
