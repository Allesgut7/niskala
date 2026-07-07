// Niskala - Backtest Engine Header
// Version: 1.0.0

#pragma once

#include "core/common/types.h"
#include <vector>
#include <string>
#include <memory>

namespace niskala {

struct BacktestResult {
    double total_return = 0.0;
    double sharpe_ratio = 0.0;
    double max_drawdown = 0.0;
    int total_trades = 0;
    int winning_trades = 0;
    int losing_trades = 0;
    std::vector<TradeRecord> trades;
};

class BacktestEngine {
public:
    BacktestEngine();
    ~BacktestEngine();

    // Run a backtest with given parameters
    BacktestResult run();

    // Set strategy parameters
    void set_symbol(const std::string& symbol);
    void set_start_date(const std::string& date);
    void set_end_date(const std::string& date);

private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace niskala
