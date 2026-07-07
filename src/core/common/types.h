// Niskala - Common Types
// Version: 1.0.0

#pragma once

#include <string>
#include <vector>
#include <map>
#include <chrono>
#include <cstdint>

namespace niskala {

// Stock quote
struct StockQuote {
    std::string symbol;
    std::string name;
    double price       = 0.0;
    double open        = 0.0;
    double high        = 0.0;
    double low         = 0.0;
    double close       = 0.0;
    double prev_close  = 0.0;
    double change      = 0.0;
    double change_pct  = 0.0;
    int64_t volume     = 0;
    int64_t market_cap = 0;
    double pe_ratio    = 0.0;
    double pb_ratio    = 0.0;
    double roe         = 0.0;
    std::string sector;
    std::string timestamp;
};

// Trade record
struct TradeRecord {
    std::string symbol;
    double price    = 0.0;
    int64_t volume  = 0;
    std::string side; // BUY, SELL
    std::string time;
};

// Order book level
struct OrderBookLevel {
    double price   = 0.0;
    int64_t volume = 0;
    int queue      = 0;
};

// News article
struct NewsArticle {
    std::string id;
    std::string title;
    std::string summary;
    std::string source;
    std::string url;
    std::string timestamp;
    std::vector<std::string> sectors;
    std::vector<std::string> tickers;
    int sentiment_score = 0; // -100 to +100
    std::string sentiment_label; // BULLISH, BEARISH, NEUTRAL
};

// Sector performance
struct SectorPerformance {
    std::string name;
    std::string code;
    double change_pct = 0.0;
    int64_t volume    = 0;
    int advancers     = 0;
    int decliners     = 0;
};

// AI signal
struct AISignal {
    std::string symbol;
    std::string signal; // BUY, HOLD, SELL
    int score       = 0; // -100 to +100
    int confidence  = 0; // 0-100
    std::string reason;
    std::string timestamp;
};

// Screen enum
enum class ScreenType {
    Dashboard,
    MarketOverview,
    Chart,
    Screener,
    Portfolio,
    NewsFeed,
    Settings,
    AIAnalysis,
    QuantLab,
    EconomicCalendar,
    StockDetail
};

// Sort direction
enum class SortDirection {
    Ascending,
    Descending
};

// Sort column
enum class SortColumn {
    Symbol,
    Price,
    Change,
    ChangePct,
    Volume,
    MarketCap,
    Sector
};

} // namespace niskala
