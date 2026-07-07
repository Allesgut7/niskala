// Niskala - Bottom Banner Widget Header
// Version: 1.0.0

#pragma once

#include "core/common/types.h"
#include <ftxui/ftxui.hpp>
#include <vector>
#include <string>

namespace niskala {

using namespace ftxui;

class BottomBanner {
public:
    BottomBanner() = default;
    ~BottomBanner() = default;

    void set_gainers(const std::vector<StockQuote>& gainers);
    void set_losers(const std::vector<StockQuote>& losers);
    Element render();

private:
    std::vector<StockQuote> gainers_;
    std::vector<StockQuote> losers_;
};

} // namespace niskala
