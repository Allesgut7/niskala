// Niskala - Top Banner Widget Header
// Version: 1.0.0

#pragma once

#include "core/common/types.h"
#include <ftxui/ftxui.hpp>
#include <vector>
#include <string>

namespace niskala {

using namespace ftxui;

class TopBanner {
public:
    TopBanner() = default;
    ~TopBanner() = default;

    void set_data(const std::vector<StockQuote>& quotes);
    Element render();

private:
    std::vector<StockQuote> quotes_;
};

} // namespace niskala
