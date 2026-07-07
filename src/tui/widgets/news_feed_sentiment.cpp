// Niskala - News Feed Sentiment Widget Implementation
// Version: 1.0.0

#include "tui/widgets/news_feed_sentiment.h"
#include <ftxui/ftxui.hpp>

using namespace ftxui;

namespace niskala {

void NewsFeedSentiment::set_articles(const std::vector<NewsArticle>& articles) {
    articles_ = articles;
    bullish_count_ = 0;
    bearish_count_ = 0;
    neutral_count_ = 0;
    for (const auto& a : articles_) {
        if (a.sentiment_score > 0) bullish_count_++;
        else if (a.sentiment_score < 0) bearish_count_++;
        else neutral_count_++;
    }
}

Element NewsFeedSentiment::render() {
    Elements items;
    items.push_back(text(" Sentiment Summary") | bold);
    items.push_back(separator());
    items.push_back(text("Bullish: " + std::to_string(bullish_count_)) | color(Color::Green));
    items.push_back(text("Bearish: " + std::to_string(bearish_count_)) | color(Color::Red));
    items.push_back(text("Neutral: " + std::to_string(neutral_count_)) | color(Color::GrayLight));
    
    return vbox(items) | border;
}

} // namespace niskala
