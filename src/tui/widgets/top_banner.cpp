// Niskala - Top Banner Widget Implementation
// Version: 1.0.0

#include "tui/widgets/top_banner.h"
#include <ftxui/ftxui.hpp>

using namespace ftxui;

namespace niskala {

void TopBanner::set_data(const std::vector<StockQuote>& quotes) {
    quotes_ = quotes;
}

Element TopBanner::render() {
    Elements items;
    for (const auto& q : quotes_) {
        auto clr = q.change >= 0 ? Color::Green : Color::Red;
        items.push_back(text(q.symbol + " " + std::to_string(q.price)) | color(clr));
        items.push_back(text(" | ") | dim);
    }
    return hbox(items) | border | bgcolor(Color::DarkBlue);
}

} // namespace niskala
