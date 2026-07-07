// Niskala - Order Book Widget Implementation
// Version: 1.0.0

#include "tui/widgets/order_book.h"
#include <ftxui/ftxui.hpp>

using namespace ftxui;

namespace niskala {

void OrderBook::set_symbol(const std::string& symbol) {
    symbol_ = symbol;
}

void OrderBook::set_bids(const std::vector<OrderBookLevel>& bids) {
    bids_ = bids;
}

void OrderBook::set_asks(const std::vector<OrderBookLevel>& asks) {
    asks_ = asks;
}

Element OrderBook::render() {
    Elements bid_rows;
    for (const auto& b : bids_) {
        Elements bid_items;
        bid_items.push_back(text(std::to_string(b.price)) | color(Color::Green) | size(WIDTH, EQUAL, 10));
        bid_items.push_back(text(std::to_string(b.volume)) | size(WIDTH, EQUAL, 10));
        bid_rows.push_back(hbox(bid_items));
    }

    Elements ask_rows;
    for (const auto& a : asks_) {
        Elements ask_items;
        ask_items.push_back(text(std::to_string(a.price)) | color(Color::Red) | size(WIDTH, EQUAL, 10));
        ask_items.push_back(text(std::to_string(a.volume)) | size(WIDTH, EQUAL, 10));
        ask_rows.push_back(hbox(ask_items));
    }

    Elements bids_col;
    bids_col.push_back(text("BIDS") | bold | color(Color::Green));
    bids_col.push_back(vbox(bid_rows));
    
    Elements asks_col;
    asks_col.push_back(text("ASKS") | bold | color(Color::Red));
    asks_col.push_back(vbox(ask_rows));
    
    Elements inner;
    inner.push_back(vbox(bids_col) | flex);
    inner.push_back(separator());
    inner.push_back(vbox(asks_col) | flex);
    
    Elements outer;
    outer.push_back(text(" Order Book: " + symbol_) | bold);
    outer.push_back(separator());
    outer.push_back(hbox(inner));
    
    return vbox(outer) | border;
}

} // namespace niskala
