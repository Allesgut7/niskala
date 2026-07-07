// Niskala - Chart Widget Implementation
// Version: 1.0.0

#include "tui/widgets/chart_widget.h"
#include <ftxui/ftxui.hpp>

using namespace ftxui;

namespace niskala {

void ChartWidget::set_symbol(const std::string& symbol) {
    symbol_ = symbol;
}

void ChartWidget::set_prices(const std::vector<double>& prices) {
    prices_ = prices;
}

Element ChartWidget::render() {
    Elements items;
    items.push_back(text(" Chart: " + symbol_) | bold);
    items.push_back(separator());
    items.push_back(text(" (chart placeholder)") | dim);
    return vbox(items) | border | flex;
}

} // namespace niskala
