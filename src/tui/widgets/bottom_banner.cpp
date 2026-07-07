// Niskala - Bottom Banner Widget Implementation
// Version: 1.0.0

#include "tui/widgets/bottom_banner.h"
#include <ftxui/ftxui.hpp>

using namespace ftxui;

namespace niskala {

void BottomBanner::set_gainers(const std::vector<StockQuote>& gainers) {
    gainers_ = gainers;
}

void BottomBanner::set_losers(const std::vector<StockQuote>& losers) {
    losers_ = losers;
}

Element BottomBanner::render() {
    Elements gainer_items;
    for (const auto& s : gainers_) {
        gainer_items.push_back(text(s.symbol) | color(Color::Green));
        gainer_items.push_back(text(" | ") | dim);
    }

    Elements loser_items;
    for (const auto& s : losers_) {
        loser_items.push_back(text(s.symbol) | color(Color::Red));
        loser_items.push_back(text(" | ") | dim);
    }

    Elements banner_items;
    banner_items.push_back(text(" GAIN: ") | bold | color(Color::Green));
    banner_items.push_back(hbox(gainer_items));
    banner_items.push_back(filler());
    banner_items.push_back(text(" LOSE: ") | bold | color(Color::Red));
    banner_items.push_back(hbox(loser_items));
    
    return hbox(banner_items);
}

} // namespace niskala
