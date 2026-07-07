// Niskala - Screener Screen Implementation
// Version: 1.0.0

#include "tui/screens/screener_screen.h"
#include "core/common/config.h"
#include "core/common/types.h"
#include "core/common/utils.h"
#include "core/market_data/data_aggregator.h"
#include <ftxui/ftxui.hpp>

using namespace ftxui;

namespace niskala {

ScreenerScreen::ScreenerScreen(
    std::shared_ptr<Config> config,
    std::shared_ptr<DataAggregator> data_aggregator)
    : config_(config),
      data_aggregator_(data_aggregator) {
}

void ScreenerScreen::refresh() {
    results_ = data_aggregator_->get_watchlist();
}

bool ScreenerScreen::on_event(Event event) {
    if (event == Event::ArrowUp && selected_row_ > 0) {
        selected_row_--;
        return true;
    }
    if (event == Event::ArrowDown &&
        selected_row_ < static_cast<int>(results_.size()) - 1) {
        selected_row_++;
        return true;
    }
    return false;
}

Element ScreenerScreen::render() {
    Elements items;
    
    // Header
    items.push_back(text(" Stock Screener") | bold);
    items.push_back(separator());
    
    // Screener filters section
    items.push_back(text(" FILTERS") | bold | color(Color::Cyan));
    items.push_back(text("  Sector: All  |  Market Cap: All  |  P/E: < 20"));
    items.push_back(text("  Price Range: 500 - 10,000  |  Volume: > 1M"));
    items.push_back(separator());
    
    // Watchlist stocks as screener results
    results_ = data_aggregator_->get_watchlist();
    
    if (!results_.empty()) {
        // Header row
        Elements header_items;
        header_items.push_back(text("SYMBOL") | bold | size(WIDTH, EQUAL, 8));
        header_items.push_back(text("NAME") | bold | size(WIDTH, EQUAL, 12));
        header_items.push_back(text("PRICE") | bold | size(WIDTH, EQUAL, 10));
        header_items.push_back(text("CHG%") | bold | size(WIDTH, EQUAL, 8));
        header_items.push_back(text("VOLUME") | bold | size(WIDTH, EQUAL, 12));
        header_items.push_back(text("SECTOR") | bold | size(WIDTH, EQUAL, 12));
        
        items.push_back(hbox(header_items));
        items.push_back(separator());
        
        // Stock rows
        for (int i = 0; i < static_cast<int>(results_.size()); i++) {
            const auto& s = results_[i];
            auto c = s.change >= 0 ? Color::Green : Color::Red;
            bool selected = (i == selected_row_);
            
            Elements row_items;
            row_items.push_back(text(s.symbol) | bold | size(WIDTH, EQUAL, 8));
            row_items.push_back(text(s.name.substr(0, 12)) | size(WIDTH, EQUAL, 12));
            row_items.push_back(text(format_price(s.price)) | size(WIDTH, EQUAL, 10));
            row_items.push_back(text(format_pct(s.change_pct)) | color(c) | size(WIDTH, EQUAL, 8));
            row_items.push_back(text(format_number(s.volume)) | size(WIDTH, EQUAL, 12));
            row_items.push_back(text(s.sector.substr(0, 12)) | size(WIDTH, EQUAL, 12));
            
            auto row = hbox(row_items);
            if (selected) {
                row = row | inverted;
            }
            items.push_back(row);
        }
    } else {
        items.push_back(text("  No stocks found matching filters") | dim);
    }
    
    items.push_back(separator());
    items.push_back(text(" Found " + std::to_string(results_.size()) + " stocks") | dim);
    items.push_back(text(" Press 1 or F1 to return to Dashboard") | dim);
    
    return vbox(items) | border | flex;
}

} // namespace niskala
