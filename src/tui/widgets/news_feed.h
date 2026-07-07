// Niskala - News Feed Widget Header
// Version: 1.0.0

#pragma once

#include "core/common/types.h"
#include <ftxui/ftxui.hpp>
#include <vector>
#include <string>

namespace niskala {

using namespace ftxui;

class NewsFeed {
public:
    NewsFeed() = default;
    ~NewsFeed() = default;

    void set_articles(const std::vector<NewsArticle>& articles);
    Element render();

private:
    std::vector<NewsArticle> articles_;
    int selected_row_ = 0;
};

} // namespace niskala
