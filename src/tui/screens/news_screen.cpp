// Niskala - News Screen Implementation
// Version: 1.0.0

#include "tui/screens/news_screen.h"
#include "core/common/config.h"
#include "core/common/types.h"
#include "core/market_data/data_aggregator.h"
#include <ftxui/ftxui.hpp>

using namespace ftxui;

namespace niskala {

NewsScreen::NewsScreen(
    std::shared_ptr<Config> config,
    std::shared_ptr<DataAggregator> data_aggregator)
    : config_(config),
      data_aggregator_(data_aggregator) {
}

void NewsScreen::refresh() {
    // TODO: fetch news articles
}

bool NewsScreen::on_event(Event event) {
    if (event == Event::ArrowUp && selected_row_ > 0) {
        selected_row_--;
        return true;
    }
    if (event == Event::ArrowDown &&
        selected_row_ < static_cast<int>(articles_.size()) - 1) {
        selected_row_++;
        return true;
    }
    return false;
}

Element NewsScreen::render() {
    Elements items;
    items.push_back(text(" News Feed") | bold);
    items.push_back(separator());
    items.push_back(text(" (placeholder)") | dim);
    return vbox(items) | border | flex;
}

} // namespace niskala
