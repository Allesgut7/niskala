// Niskala - Chart Widget Header
// Version: 1.0.0

#pragma once

#include "core/common/types.h"
#include <ftxui/ftxui.hpp>
#include <vector>
#include <string>

namespace niskala {

using namespace ftxui;

class ChartWidget {
public:
    ChartWidget() = default;
    ~ChartWidget() = default;

    void set_symbol(const std::string& symbol);
    void set_prices(const std::vector<double>& prices);
    Element render();

private:
    std::string symbol_;
    std::vector<double> prices_;
};

} // namespace niskala
