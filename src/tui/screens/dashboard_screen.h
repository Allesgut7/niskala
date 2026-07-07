// Niskala - Dashboard Screen Header
// Version: 1.0.0

#pragma once

#include "tui/screens/screen_interface.h"
#include "core/common/types.h"
#include <memory>
#include <vector>

namespace niskala {

class Config;
class DataAggregator;
class MultiRegionFearGreed;
class SentimentProvider;
struct NewsArticle;

class DashboardScreen : public ScreenBase {
public:
    DashboardScreen(
        std::shared_ptr<Config> config,
        std::shared_ptr<DataAggregator> data_aggregator,
        std::shared_ptr<MultiRegionFearGreed> fear_greed
    );
    ~DashboardScreen() override = default;
    
    Element render() override;
    bool on_event(Event event) override;
    void refresh() override;
    std::string name() const override { return "Dashboard"; }
    
private:
    std::shared_ptr<Config> config_;
    std::shared_ptr<DataAggregator> data_aggregator_;
    std::shared_ptr<MultiRegionFearGreed> fear_greed_;
    
    // Sub-renders
    Element render_top_banner();
    Element render_bottom_banner();
    Element render_running_trade();
    Element render_stock_table();
    Element render_news_feed();
    Element render_fear_greed();
    Element render_sector_heatmap();
    Element render_status_bar();
    
    // Data
    std::vector<StockQuote> watchlist_data_;
    std::vector<StockQuote> global_indices_;
    std::vector<StockQuote> commodities_;
    std::vector<StockQuote> forex_;
    StockQuote ihsg_;
    std::vector<NewsArticle> news_articles_;
    
    // Sentiment provider
    std::shared_ptr<SentimentProvider> sentiment_provider_;
    
    // State
    int selected_row_ = 0;
    SortColumn sort_column_ = SortColumn::Symbol;
    SortDirection sort_direction_ = SortDirection::Ascending;
    
    // Ticker state
    int ticker_offset_ = 0;
};

} // namespace niskala
