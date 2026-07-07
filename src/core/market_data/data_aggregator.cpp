// Niskala - Data Aggregator Implementation
// Version: 1.0.0

#include "core/market_data/data_aggregator.h"
#include "core/market_data/yfinance_provider.h"
#include "core/market_data/akshare_provider.h"
#include "core/market_data/cache_manager.h"
#include "core/common/config.h"
#include "core/common/logger.h"

namespace niskala {

DataAggregator::DataAggregator(std::shared_ptr<Config> config)
    : config_(config) {
    
    yfinance_ = std::make_shared<YFinanceProvider>();
    akshare_ = std::make_shared<AkshareProvider>();
    cache_ = std::make_shared<CacheManager>(config->get_refresh_interval());
    
    LOG_INFO("Data aggregator initialized");
}

DataAggregator::~DataAggregator() = default;

StockQuote DataAggregator::get_quote(const std::string& symbol) {
    // Check cache first
    StockQuote quote;
    if (cache_->get(symbol, quote)) {
        return quote;
    }
    
    // Fetch from yfinance
    quote = yfinance_->get_quote(symbol);
    
    // Cache the result
    cache_->put(symbol, quote);
    
    return quote;
}

std::vector<StockQuote> DataAggregator::get_watchlist() {
    std::vector<std::string> watchlist = config_->get_watchlist();
    
    // Try to fetch all at once for efficiency
    std::vector<StockQuote> quotes = yfinance_->get_quotes(watchlist);
    
    // Cache results
    for (const auto& quote : quotes) {
        cache_->put(quote.symbol, quote);
    }
    
    return quotes;
}

std::vector<StockQuote> DataAggregator::get_top_gainers(int limit) {
    std::vector<StockQuote> result;
    // Will be implemented with IDX data
    return result;
}

std::vector<StockQuote> DataAggregator::get_top_losers(int limit) {
    std::vector<StockQuote> result;
    // Will be implemented with IDX data
    return result;
}

StockQuote DataAggregator::get_ihsg() {
    return yfinance_->get_index("^JKSE");
}

std::vector<StockQuote> DataAggregator::get_global_indices() {
    std::vector<StockQuote> result;
    result.push_back(yfinance_->get_index("^JKSE"));   // IHSG
    result.push_back(yfinance_->get_index("^GSPC"));   // S&P 500
    result.push_back(yfinance_->get_index("^N225"));   // Nikkei
    result.push_back(yfinance_->get_index("^STI"));    // STI
    return result;
}

std::vector<StockQuote> DataAggregator::get_commodities() {
    std::vector<StockQuote> result;
    result.push_back(yfinance_->get_commodity("GC=F"));    // Gold
    result.push_back(yfinance_->get_commodity("CL=F"));    // Oil
    result.push_back(yfinance_->get_commodity("SI=F"));    // Silver
    return result;
}

std::vector<StockQuote> DataAggregator::get_forex() {
    std::vector<StockQuote> result;
    result.push_back(yfinance_->get_forex("USDIDR=X")); // USD/IDR
    result.push_back(yfinance_->get_forex("EURUSD=X")); // EUR/USD
    return result;
}

void DataAggregator::refresh() {
    cache_->clear();
    LOG_INFO("Cache refreshed");
}

} // namespace niskala
