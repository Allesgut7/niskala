// Niskala - Running Trade Ticker Widget Header
// Version: 1.0.0

#pragma once

#include "core/common/types.h"
#include <ftxui/ftxui.hpp>
#include <vector>
#include <string>

namespace niskala {

using namespace ftxui;

class RunningTradeTicker {
public:
    RunningTradeTicker() = default;
    ~RunningTradeTicker() = default;

    void set_trades(const std::vector<TradeRecord>& trades);
    void tick();
    Element render();

private:
    std::vector<TradeRecord> trades_;
    int offset_ = 0;
};

} // namespace niskala
