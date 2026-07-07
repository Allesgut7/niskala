// Niskala - Running Trade Ticker Widget Implementation
// Version: 1.0.0

#include "tui/widgets/running_trade_ticker.h"
#include <ftxui/ftxui.hpp>

using namespace ftxui;

namespace niskala {

void RunningTradeTicker::set_trades(const std::vector<TradeRecord>& trades) {
    trades_ = trades;
}

void RunningTradeTicker::tick() {
    offset_++;
}

Element RunningTradeTicker::render() {
    std::string ticker_text;
    for (const auto& t : trades_) {
        ticker_text += t.symbol + " " + std::to_string(t.price)
                    + " " + std::to_string(t.volume) + " ";
    }
    if (ticker_text.empty()) {
        ticker_text = " No trades ";
    }
    return text(ticker_text) | color(Color::Yellow) | border;
}

} // namespace niskala
