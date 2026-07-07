// Niskala - Portfolio Screen Implementation
// Version: 1.0.0

#include "tui/screens/portfolio_screen.h"
#include "core/common/config.h"
#include "core/common/types.h"
#include "core/common/utils.h"
#include "core/market_data/data_aggregator.h"
#include <ftxui/ftxui.hpp>

using namespace ftxui;

namespace niskala {

PortfolioScreen::PortfolioScreen(
    std::shared_ptr<Config> config,
    std::shared_ptr<DataAggregator> data_aggregator)
    : config_(config),
      data_aggregator_(data_aggregator) {
}

void PortfolioScreen::refresh() {
    // Portfolio data would come from trading engine
}

bool PortfolioScreen::on_event(Event event) {
    if (event == Event::ArrowUp && selected_row_ > 0) {
        selected_row_--;
        return true;
    }
    return false;
}

Element PortfolioScreen::render() {
    Elements items;
    
    // Header
    items.push_back(text(" Portfolio") | bold);
    items.push_back(separator());
    
    // Portfolio summary
    items.push_back(text(" PORTFOLIO SUMMARY") | bold | color(Color::Cyan));
    items.push_back(text("  Balance:      Rp 100,000,000") | bold);
    items.push_back(text("  Invested:     Rp 0"));
    items.push_back(text("  Unrealized:   Rp 0"));
    items.push_back(text("  Realized:     Rp 0"));
    items.push_back(text("  Total P&L:    Rp 0 (0.00%)"));
    items.push_back(separator());
    
    // Positions header
    items.push_back(text(" OPEN POSITIONS") | bold | color(Color::Green));
    items.push_back(separator());
    
    // Header row
    Elements header_items;
    header_items.push_back(text("SYMBOL") | bold | size(WIDTH, EQUAL, 8));
    header_items.push_back(text("QTY") | bold | size(WIDTH, EQUAL, 8));
    header_items.push_back(text("AVG") | bold | size(WIDTH, EQUAL, 10));
    header_items.push_back(text("CURRENT") | bold | size(WIDTH, EQUAL, 10));
    header_items.push_back(text("P&L") | bold | size(WIDTH, EQUAL, 10));
    header_items.push_back(text("P&L%") | bold | size(WIDTH, EQUAL, 8));
    
    items.push_back(hbox(header_items));
    items.push_back(separator());
    
    // Placeholder positions (empty for now)
    items.push_back(text("  No open positions") | dim);
    items.push_back(text("  Start trading to see your positions here"));
    
    items.push_back(separator());
    
    // Trade history section
    items.push_back(text(" RECENT TRADES") | bold | color(Color::Yellow));
    items.push_back(separator());
    
    // Header row
    Elements trade_header;
    trade_header.push_back(text("DATE") | bold | size(WIDTH, EQUAL, 10));
    trade_header.push_back(text("SYMBOL") | bold | size(WIDTH, EQUAL, 8));
    trade_header.push_back(text("SIDE") | bold | size(WIDTH, EQUAL, 6));
    trade_header.push_back(text("QTY") | bold | size(WIDTH, EQUAL, 8));
    trade_header.push_back(text("PRICE") | bold | size(WIDTH, EQUAL, 10));
    trade_header.push_back(text("P&L") | bold | size(WIDTH, EQUAL, 10));
    
    items.push_back(hbox(trade_header));
    items.push_back(separator());
    
    // Placeholder trades
    items.push_back(text("  No recent trades") | dim);
    items.push_back(text("  Your trade history will appear here"));
    
    items.push_back(separator());
    items.push_back(text(" Press 1 or F1 to return to Dashboard") | dim);
    
    return vbox(items) | border | flex;
}

} // namespace niskala
