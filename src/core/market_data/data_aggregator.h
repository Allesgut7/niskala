// Niskala - Data Aggregator Header
// Version: 1.0.0

#pragma once

#include "core/common/types.h"
#include <memory>
#include <string>
#include <vector>

namespace niskala {

class Config;
class YFinanceProvider;
class AkshareProvider;
class CacheManager;

class DataAggregator {
public:
    DataAggregator(std::shared_ptr<Config> config);
    ~DataAggregator();

    StockQuote get_quote(const std::string& symbol);
    std::vector<StockQuote> get_watchlist();
    std::vector<StockQuote> get_top_gainers(int limit = 10);
    std::vector<StockQuote> get_top_losers(int limit = 10);
    StockQuote get_ihsg();
    std::vector<StockQuote> get_global_indices();
    std::vector<StockQuote> get_commodities();
    std::vector<StockQuote> get_forex();
    void refresh();

private:
    std::shared_ptr<Config> config_;
    std::shared_ptr<YFinanceProvider> yfinance_;
    std::shared_ptr<AkshareProvider> akshare_;
    std::shared_ptr<CacheManager> cache_;
};

} // namespace niskala
