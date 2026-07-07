// Niskala - Order Book Widget Header
// Version: 1.0.0

#pragma once

#include "core/common/types.h"
#include <ftxui/ftxui.hpp>
#include <vector>
#include <string>

namespace niskala {

using namespace ftxui;

class OrderBook {
public:
    OrderBook() = default;
    ~OrderBook() = default;

    void set_symbol(const std::string& symbol);
    void set_bids(const std::vector<OrderBookLevel>& bids);
    void set_asks(const std::vector<OrderBookLevel>& asks);
    Element render();

private:
    std::string symbol_;
    std::vector<OrderBookLevel> bids_;
    std::vector<OrderBookLevel> asks_;
};

} // namespace niskala
