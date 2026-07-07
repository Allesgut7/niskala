// Niskala - Dashboard Screen Implementation
// Version: 1.0.2 (Added real sentiment news feed)

#include "tui/screens/dashboard_screen.h"
#include "core/common/config.h"
#include "core/common/types.h"
#include "core/common/utils.h"
#include "core/market_data/data_aggregator.h"
#include "core/market_data/sentiment_provider.h"
#include "core/fear_greed/multi_region.h"
#include <ftxui/ftxui.hpp>

using namespace ftxui;

namespace niskala {

DashboardScreen::DashboardScreen(
    std::shared_ptr<Config> config,
    std::shared_ptr<DataAggregator> data_aggregator,
    std::shared_ptr<MultiRegionFearGreed> fear_greed)
    : config_(config),
      data_aggregator_(data_aggregator),
      fear_greed_(fear_greed) {
    // Initialize sentiment provider
    sentiment_provider_ = std::make_shared<SentimentProvider>();
}

void DashboardScreen::refresh() {
    watchlist_data_ = data_aggregator_->get_watchlist();
    global_indices_ = data_aggregator_->get_global_indices();
    commodities_    = data_aggregator_->get_commodities();
    forex_          = data_aggregator_->get_forex();
    ihsg_           = data_aggregator_->get_ihsg();
    ticker_offset_++;
    
    // Fetch news with sentiment (only if provider available)
    if (sentiment_provider_ && sentiment_provider_->is_available()) {
        try {
            news_articles_ = sentiment_provider_->fetch_news(10);
        } catch (const std::exception& e) {
            // Keep old news on error
        }
    }
}

bool DashboardScreen::on_event(Event event) {
    if (event == Event::ArrowUp && selected_row_ > 0) {
        selected_row_--;
        return true;
    }
    if (event == Event::ArrowDown &&
        selected_row_ < static_cast<int>(watchlist_data_.size()) - 1) {
        selected_row_++;
        return true;
    }
    return false;
}

// ---- Render sub-components ----

Element DashboardScreen::render_top_banner() {
    // Global indices, commodity, forex in a single row
    Elements items;
    
    // IHSG
    {
        auto c = ihsg_.change >= 0 ? Color::Green : Color::Red;
        std::string txt = " IHSG " + format_price(ihsg_.price)
                        + " " + format_pct(ihsg_.change_pct) + " ";
        items.push_back(text(txt) | color(c) | bold);
    }
    
    // Global indices
    for (const auto& idx : global_indices_) {
        if (idx.symbol == "^JKSE") continue;
        auto c = idx.change >= 0 ? Color::Green : Color::Red;
        std::string label = idx.name.empty() ? idx.symbol : idx.name;
        std::string txt = " " + label + " " + format_price(idx.price)
                        + " " + format_pct(idx.change_pct) + " ";
        items.push_back(text(txt) | color(c));
    }
    
    // Commodities
    for (const auto& cmd : commodities_) {
        auto c = cmd.change >= 0 ? Color::Green : Color::Red;
        std::string label = cmd.name.empty() ? cmd.symbol : cmd.name;
        std::string txt = " " + label + " " + format_price(cmd.price)
                        + " " + format_pct(cmd.change_pct) + " ";
        items.push_back(text(txt) | color(c));
    }
    
    // Forex
    for (const auto& fx : forex_) {
        auto c = fx.change >= 0 ? Color::Green : Color::Red;
        std::string label = fx.name.empty() ? fx.symbol : fx.name;
        std::string txt = " " + label + " " + format_price(fx.price)
                        + " " + format_pct(fx.change_pct) + " ";
        items.push_back(text(txt) | color(c));
    }
    
    return hbox(items) | border | bgcolor(Color::DarkBlue);
}

Element DashboardScreen::render_bottom_banner() {
    auto gainers = data_aggregator_->get_top_gainers(5);
    auto losers  = data_aggregator_->get_top_losers(5);
    
    Elements gainer_items;
    for (const auto& s : gainers) {
        gainer_items.push_back(
            text(s.symbol + " +" + format_pct(s.change_pct, 1))
            | color(Color::Green)
        );
        gainer_items.push_back(text(" | ") | color(Color::GrayLight));
    }
    
    Elements loser_items;
    for (const auto& s : losers) {
        loser_items.push_back(
            text(s.symbol + " " + format_pct(s.change_pct, 1))
            | color(Color::Red)
        );
        loser_items.push_back(text(" | ") | color(Color::GrayLight));
    }
    
    Elements banner_items;
    banner_items.push_back(text(" GAIN: ") | bold | color(Color::Green));
    banner_items.push_back(hbox(gainer_items));
    banner_items.push_back(filler());
    banner_items.push_back(text(" LOSE: ") | bold | color(Color::Red));
    banner_items.push_back(hbox(loser_items));
    
    return hbox(banner_items);
}

Element DashboardScreen::render_running_trade() {
    // Scrolling ticker of recent trades
    std::string ticker_text = " ";
    
    for (size_t i = 0; i < watchlist_data_.size(); i++) {
        const auto& s = watchlist_data_[i];
        ticker_text += s.symbol + " " + format_price(s.price)
                    + " " + format_number(s.volume) + " ";
    }
    
    // Scroll effect
    if (ticker_offset_ > 0) {
        size_t offset = ticker_offset_ % ticker_text.size();
        ticker_text = ticker_text.substr(offset) + ticker_text.substr(0, offset);
    }
    
    return text(ticker_text) | color(Color::Yellow) | border;
}

Element DashboardScreen::render_stock_table() {
    // Header
    Elements header_items;
    header_items.push_back(text("SYMBOL")  | bold | size(WIDTH, EQUAL, 8));
    header_items.push_back(text("NAME")    | bold | size(WIDTH, EQUAL, 12));
    header_items.push_back(text("PRICE")   | bold | size(WIDTH, EQUAL, 10));
    header_items.push_back(text("CHG")     | bold | size(WIDTH, EQUAL, 8));
    header_items.push_back(text("CHG%")    | bold | size(WIDTH, EQUAL, 8));
    header_items.push_back(text("VOLUME")  | bold | size(WIDTH, EQUAL, 12));
    header_items.push_back(text("SECTOR")  | bold | size(WIDTH, EQUAL, 12));
    auto header = hbox(header_items);
    
    // Rows
    Elements rows;
    for (int i = 0; i < static_cast<int>(watchlist_data_.size()); i++) {
        const auto& s = watchlist_data_[i];
        
        auto c = s.change >= 0 ? Color::Green : Color::Red;
        bool selected = (i == selected_row_);
        
        Elements row_items;
        row_items.push_back(text(s.symbol) | bold | size(WIDTH, EQUAL, 8));
        row_items.push_back(text(s.name.substr(0, 10)) | size(WIDTH, EQUAL, 12));
        row_items.push_back(text(format_price(s.price)) | size(WIDTH, EQUAL, 10));
        row_items.push_back(text(format_pct(s.change, 0)) | color(c) | size(WIDTH, EQUAL, 8));
        row_items.push_back(text(format_pct(s.change_pct)) | color(c) | size(WIDTH, EQUAL, 8));
        row_items.push_back(text(format_number(s.volume)) | size(WIDTH, EQUAL, 12));
        row_items.push_back(text(s.sector.substr(0, 10)) | size(WIDTH, EQUAL, 12));
        
        auto row = hbox(row_items);
        
        if (selected) {
            row = row | inverted;
        }
        
        rows.push_back(row);
    }
    
    Elements table_items;
    table_items.push_back(header);
    table_items.push_back(separator());
    table_items.push_back(vbox(rows) | vscroll_indicator | yframe);
    
    return vbox(table_items) | border | flex;
}

Element DashboardScreen::render_news_feed() {
    Elements items;
    
    if (news_articles_.empty()) {
        // Show placeholder if no news available
        items.push_back(text("  Loading news...") | dim);
    } else {
        // Display real news with sentiment
        for (size_t i = 0; i < std::min(news_articles_.size(), size_t(10)); i++) {
            const auto& article = news_articles_[i];
            
            // Format: [SOURCE] TITLE - [STOCKS] (SENTIMENT)
            std::string source_padded = article.source.substr(0, 6);
            source_padded.resize(6, ' ');
            
            // Title (truncate to fit)
            std::string title = article.title.substr(0, 50);
            
            // Affected stocks (max 3)
            std::string stocks_str;
            if (!article.tickers.empty()) {
                size_t max_tickers = std::min(article.tickers.size(), size_t(3));
                for (size_t j = 0; j < max_tickers; j++) {
                    stocks_str += article.tickers[j];
                    if (j < max_tickers - 1) stocks_str += ",";
                }
            } else {
                stocks_str = "-";
            }
            
            // Sentiment indicator
            std::string sentiment_icon;
            Color sentiment_color;
            if (article.sentiment_score > 20) {
                sentiment_icon = "↑";  // Bullish
                sentiment_color = Color::Green;
            } else if (article.sentiment_score < -20) {
                sentiment_icon = "↓";  // Bearish
                sentiment_color = Color::Red;
            } else {
                sentiment_icon = "→";  // Neutral
                sentiment_color = Color::Yellow;
            }
            
            // Build news line
            Elements line_parts;
            line_parts.push_back(text(" " + source_padded + " ") | dim);
            line_parts.push_back(text(title) | color(sentiment_color));
            line_parts.push_back(text(" [") | dim);
            line_parts.push_back(text(stocks_str) | bold);
            line_parts.push_back(text("] ") | dim);
            line_parts.push_back(text(sentiment_icon) | color(sentiment_color) | bold);
            
            items.push_back(hbox(line_parts));
        }
    }
    
    Elements feed_items;
    feed_items.push_back(text(" News Feed (AI Sentiment)") | bold);
    feed_items.push_back(separator());
    feed_items.push_back(vbox(items) | vscroll_indicator | yframe);
    
    return vbox(feed_items) | border | flex;
}

Element DashboardScreen::render_fear_greed() {
    // Fear & Greed gauges for 3 regions
    auto fg = fear_greed_->calculate_all();
    
    auto make_gauge = [](const std::string& label, const FearGreedResult& fg) {
        auto c = Color::Yellow;
        if (fg.score <= 25) c = Color::Red;
        else if (fg.score <= 45) c = Color::Yellow;
        else if (fg.score >= 75) c = Color::Green;
        else if (fg.score >= 55) c = Color::Cyan;
        
        Elements gauge_items;
        gauge_items.push_back(text(label) | bold | center);
        gauge_items.push_back(text(std::to_string(fg.score)) | color(c) | bold | center);
        gauge_items.push_back(text(fg.status) | color(c) | center);
        
        return vbox(gauge_items) | border | flex;
    };
    
    Elements gauge_row;
    gauge_row.push_back(make_gauge("ID", fg.indonesia));
    gauge_row.push_back(make_gauge("ASIA", fg.asia));
    gauge_row.push_back(make_gauge("GLOB", fg.global));
    
    return hbox(gauge_row);
}

Element DashboardScreen::render_sector_heatmap() {
    // Simple sector heatmap using hbox/vbox grid
    std::vector<std::pair<std::string, double>> sectors = {
        {"FIN", 2.1}, {"BSC", -0.5}, {"CON", 1.3},
        {"IND", 0.8}, {"HEA", -1.2}, {"TEC", 3.4},
        {"ENE", 0.2}, {"PRO", -0.3}, {"TRA", 1.7},
    };
    
    // Create 3x3 grid manually
    Elements grid_rows;
    for (int row = 0; row < 3; row++) {
        Elements row_cells;
        for (int col = 0; col < 3; col++) {
            int idx = row * 3 + col;
            if (idx < static_cast<int>(sectors.size())) {
                const auto& [name, chg] = sectors[idx];
                auto c = chg >= 0 ? Color::Green : Color::Red;
                
                Elements cell_items;
                cell_items.push_back(text(name) | bold | center);
                cell_items.push_back(text(format_pct(chg)) | center);
                
                row_cells.push_back(vbox(cell_items) | border | color(c) | flex);
            }
        }
        grid_rows.push_back(hbox(row_cells));
    }
    
    Elements heatmap_items;
    heatmap_items.push_back(text(" Sector Heatmap") | bold);
    heatmap_items.push_back(vbox(grid_rows));
    
    return vbox(heatmap_items) | border | flex;
}

Element DashboardScreen::render_status_bar() {
    Elements status_items;
    status_items.push_back(text("1:Dashboard 2:Market 3:Chart 4:Screener 5:Portfolio 6:News 7:Settings | F1-F7 also work | q:Quit"));
    status_items.push_back(filler());
    status_items.push_back(text("Niskala v1.0.0"));
    
    return hbox(status_items) | bgcolor(Color::DarkBlue);
}

Element DashboardScreen::render() {
    Elements main_items;
    main_items.push_back(render_top_banner());
    main_items.push_back(render_running_trade());
    
    Elements content_row;
    content_row.push_back(vbox({render_stock_table()}) | flex);
    
    Elements right_panel;
    right_panel.push_back(render_fear_greed());
    right_panel.push_back(render_news_feed());
    content_row.push_back(vbox(right_panel) | size(WIDTH, GREATER_THAN, 40));
    
    main_items.push_back(hbox(content_row) | flex);
    main_items.push_back(render_bottom_banner());
    main_items.push_back(render_status_bar());
    
    return vbox(main_items) | flex;
}

} // namespace niskala
