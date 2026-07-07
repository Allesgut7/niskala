// Niskala - Backtest Engine Implementation
// Version: 1.0.0

#include "core/quant/backtest_engine.h"
#include <string>

namespace niskala {

struct BacktestEngine::Impl {
    std::string symbol;
    std::string start_date;
    std::string end_date;
};

BacktestEngine::BacktestEngine()
    : impl_(std::make_unique<Impl>()) {
}

BacktestEngine::~BacktestEngine() = default;

BacktestResult BacktestEngine::run() {
    // TODO: Run strategy simulation
    return BacktestResult{};
}

void BacktestEngine::set_symbol(const std::string& symbol) {
    impl_->symbol = symbol;
}

void BacktestEngine::set_start_date(const std::string& date) {
    impl_->start_date = date;
}

void BacktestEngine::set_end_date(const std::string& date) {
    impl_->end_date = date;
}

} // namespace niskala
