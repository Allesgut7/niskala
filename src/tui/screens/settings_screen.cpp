// Niskala - Settings Screen Implementation
// Version: 1.0.0

#include "tui/screens/settings_screen.h"
#include "core/common/config.h"
#include "core/common/types.h"
#include "core/market_data/data_aggregator.h"
#include <ftxui/ftxui.hpp>

using namespace ftxui;

namespace niskala {

SettingsScreen::SettingsScreen(
    std::shared_ptr<Config> config,
    std::shared_ptr<DataAggregator> data_aggregator)
    : config_(config),
      data_aggregator_(data_aggregator) {
}

void SettingsScreen::refresh() {
    // Reload settings
}

bool SettingsScreen::on_event(Event event) {
    if (event == Event::ArrowUp && selected_row_ > 0) {
        selected_row_--;
        return true;
    }
    return false;
}

Element SettingsScreen::render() {
    Elements items;
    
    // Header
    items.push_back(text(" Settings") | bold);
    items.push_back(separator());
    
    // General settings
    items.push_back(text(" GENERAL") | bold | color(Color::Cyan));
    items.push_back(text("  App Name:      Niskala"));
    items.push_back(text("  Version:       1.0.0"));
    items.push_back(text("  Theme:         Dark"));
    items.push_back(text("  Language:      Bahasa Indonesia"));
    items.push_back(separator());
    
    // Data settings
    items.push_back(text(" DATA") | bold | color(Color::Green));
    items.push_back(text("  Refresh Rate:  30 seconds"));
    items.push_back(text("  Data Source:   Yahoo Finance"));
    items.push_back(text("  Cache:         Enabled"));
    items.push_back(text("  Market Hours:  09:00 - 16:00 WIB"));
    items.push_back(separator());
    
    // Watchlist
    items.push_back(text(" WATCHLIST") | bold | color(Color::Yellow));
    auto watchlist = config_->get_watchlist();
    for (size_t i = 0; i < watchlist.size() && i < 10; i++) {
        std::string line = "  " + std::to_string(i + 1) + ". " + watchlist[i];
        items.push_back(text(line));
    }
    items.push_back(separator());
    
    // Keyboard shortcuts
    items.push_back(text(" KEYBOARD SHORTCUTS") | bold | color(Color::Magenta));
    items.push_back(text("  1 / F1   Dashboard"));
    items.push_back(text("  2 / F2   Market Overview"));
    items.push_back(text("  3 / F3   Chart"));
    items.push_back(text("  4 / F4   Screener"));
    items.push_back(text("  5 / F5   Portfolio"));
    items.push_back(text("  6 / F6   News Feed"));
    items.push_back(text("  7 / F7   Settings (this screen)"));
    items.push_back(text("  q        Quit"));
    items.push_back(separator());
    
    items.push_back(text(" Press 1 or F1 to return to Dashboard") | dim);
    
    return vbox(items) | border | flex;
}

} // namespace niskala
