// Niskala - News Feed Widget Implementation
// Version: 1.0.0

#include "tui/widgets/news_feed.h"
#include <ftxui/ftxui.hpp>

using namespace ftxui;

namespace niskala {

void NewsFeed::set_articles(const std::vector<NewsArticle>& articles) {
    articles_ = articles;
}

Element NewsFeed::render() {
    Elements items;
    for (const auto& a : articles_) {
        auto clr = a.sentiment_score > 0 ? Color::Green
                 : a.sentiment_score < 0 ? Color::Red
                 : Color::GrayLight;
        items.push_back(
            text(a.source + " | " + a.title) | color(clr)
        );
    }
    if (items.empty()) {
        items.push_back(text(" No news available") | dim);
    }
    
    Elements feed_items;
    feed_items.push_back(text(" News Feed") | bold);
    feed_items.push_back(separator());
    feed_items.push_back(vbox(items) | vscroll_indicator | yframe);
    
    return vbox(feed_items) | border | flex;
}

} // namespace niskala
