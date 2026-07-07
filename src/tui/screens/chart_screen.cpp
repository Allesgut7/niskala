// Niskala - Chart Screen Implementation
// Version: 1.0.0

#include "tui/screens/chart_screen.h"
#include "core/common/config.h"
#include "core/common/types.h"
#include "core/common/utils.h"
#include "core/market_data/data_aggregator.h"
#include <ftxui/ftxui.hpp>
#include <cmath>

using namespace ftxui;

namespace niskala {

ChartScreen::ChartScreen(
    std::shared_ptr<Config> config,
    std::shared_ptr<DataAggregator> data_aggregator)
    : config_(config),
      data_aggregator_(data_aggregator) {
}

void ChartScreen::refresh() {
    // Fetch current data for selected symbol
}

bool ChartScreen::on_event(Event /*event*/) {
    return false;
}

Element ChartScreen::render() {
    Elements items;
    
    // Header
    items.push_back(text(" Chart - " + selected_symbol_) | bold);
    items.push_back(separator());
    
    // Chart area (simple ASCII chart)
    items.push_back(text(" PRICE CHART") | bold | color(Color::Cyan));
    items.push_back(separator());
    
    // Generate a simple ASCII chart
    int chart_height = 15;
    int chart_width = 60;
    
    // Mock price data for BBCA
    std::vector<double> prices = {
        9200, 9250, 9300, 9280, 9350, 9400, 9380, 9420, 9450, 9500,
        9480, 9520, 9550, 9600, 9580, 9620, 9650, 9700, 9680, 9720
    };
    
    if (!prices.empty()) {
        double min_price = *std::min_element(prices.begin(), prices.end());
        double max_price = *std::max_element(prices.begin(), prices.end());
        double range = max_price - min_price;
        
        // Draw chart rows
        for (int row = 0; row < chart_height; row++) {
            std::string line = "";
            double row_price = max_price - (range * row / chart_height);
            
            for (size_t col = 0; col < prices.size() && col < chart_width; col++) {
                if (std::abs(prices[col] - row_price) < range / chart_height) {
                    line += "*";
                } else {
                    line += " ";
                }
            }
            
            // Add price label on right side
            if (row == 0 || row == chart_height / 2 || row == chart_height - 1) {
                line += " " + format_price(row_price);
            }
            
            items.push_back(text(line));
        }
    }
    
    items.push_back(separator());
    
    // Chart info
    items.push_back(text(" Symbol: " + selected_symbol_) | dim);
    items.push_back(text(" Timeframe: 1D  |  Period: 20 days") | dim);
    items.push_back(text(" Press 1 or F1 to return to Dashboard") | dim);
    
    return vbox(items) | border | flex;
}

} // namespace niskala
