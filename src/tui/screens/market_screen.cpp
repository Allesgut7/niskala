// Niskala - Market Screen Implementation
// Version: 1.0.0

#include "tui/screens/market_screen.h"
#include "core/common/config.h"
#include "core/common/types.h"
#include "core/common/utils.h"
#include "core/market_data/data_aggregator.h"
#include <ftxui/ftxui.hpp>

using namespace ftxui;

namespace niskala {

MarketScreen::MarketScreen(
    std::shared_ptr<Config> config,
    std::shared_ptr<DataAggregator> data_aggregator)
    : config_(config),
      data_aggregator_(data_aggregator) {
}

void MarketScreen::refresh() {
    stocks_ = data_aggregator_->get_watchlist();
}

bool MarketScreen::on_event(Event event) {
    if (event == Event::ArrowUp && selected_row_ > 0) {
        selected_row_--;
        return true;
    }
    if (event == Event::ArrowDown &&
        selected_row_ < static_cast<int>(stocks_.size()) - 1) {
        selected_row_++;
        return true;
    }
    return false;
}

Element MarketScreen::render() {
    Elements items;
    
    // Header
    items.push_back(text(" Market Overview") | bold);
    items.push_back(separator());
    
    // Market Indices section
    {
        auto indices = data_aggregator_->get_global_indices();
        Elements idx_items;
        idx_items.push_back(text(" MARKET INDICES") | bold | color(Color::Cyan));
        
        for (const auto& idx : indices) {
            auto c = idx.change >= 0 ? Color::Green : Color::Red;
            std::string label = idx.name.empty() ? idx.symbol : idx.name;
            std::string line = "  " + label + "  " + format_price(idx.price) 
                             + "  " + format_pct(idx.change_pct);
            idx_items.push_back(text(line) | color(c));
        }
        items.push_back(vbox(idx_items));
    }
    
    items.push_back(separator());
    
    // Commodities section
    {
        auto commodities = data_aggregator_->get_commodities();
        Elements cmd_items;
        cmd_items.push_back(text(" COMMODITIES") | bold | color(Color::Yellow));
        
        for (const auto& cmd : commodities) {
            auto c = cmd.change >= 0 ? Color::Green : Color::Red;
            std::string label = cmd.name.empty() ? cmd.symbol : cmd.name;
            std::string line = "  " + label + "  " + format_price(cmd.price) 
                             + "  " + format_pct(cmd.change_pct);
            cmd_items.push_back(text(line) | color(c));
        }
        items.push_back(vbox(cmd_items));
    }
    
    items.push_back(separator());
    
    // Forex section
    {
        auto forex = data_aggregator_->get_forex();
        Elements fx_items;
        fx_items.push_back(text(" FOREX") | bold | color(Color::Magenta));
        
        for (const auto& fx : forex) {
            auto c = fx.change >= 0 ? Color::Green : Color::Red;
            std::string label = fx.name.empty() ? fx.symbol : fx.name;
            std::string line = "  " + label + "  " + format_price(fx.price) 
                             + "  " + format_pct(fx.change_pct);
            fx_items.push_back(text(line) | color(c));
        }
        items.push_back(vbox(fx_items));
    }
    
    items.push_back(separator());
    
    // Top Gainers section
    {
        auto gainers = data_aggregator_->get_top_gainers(5);
        Elements gain_items;
        gain_items.push_back(text(" TOP GAINERS") | bold | color(Color::Green));
        
        for (const auto& s : gainers) {
            std::string line = "  " + s.symbol + "  " + format_price(s.price) 
                             + "  +" + format_pct(s.change_pct);
            gain_items.push_back(text(line) | color(Color::Green));
        }
        items.push_back(vbox(gain_items));
    }
    
    items.push_back(separator());
    
    // Top Losers section
    {
        auto losers = data_aggregator_->get_top_losers(5);
        Elements loss_items;
        loss_items.push_back(text(" TOP LOSERS") | bold | color(Color::Red));
        
        for (const auto& s : losers) {
            std::string line = "  " + s.symbol + "  " + format_price(s.price) 
                             + "  " + format_pct(s.change_pct);
            loss_items.push_back(text(line) | color(Color::Red));
        }
        items.push_back(vbox(loss_items));
    }
    
    items.push_back(separator());
    items.push_back(text(" Press 1 or F1 to return to Dashboard") | dim);
    
    return vbox(items) | border | flex;
}

} // namespace niskala
