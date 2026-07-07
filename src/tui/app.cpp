// Niskala - TUI Application Implementation
// Version: 1.0.0

#include "tui/app.h"
#include "tui/screens/dashboard_screen.h"
#include "tui/screens/market_screen.h"
#include "tui/screens/chart_screen.h"
#include "tui/screens/news_screen.h"
#include "tui/screens/screener_screen.h"
#include "tui/screens/portfolio_screen.h"
#include "tui/screens/settings_screen.h"
#include "core/common/config.h"
#include "core/common/logger.h"
#include "core/common/types.h"
#include "core/market_data/data_aggregator.h"
#include "core/fear_greed/multi_region.h"

#include <ftxui/screen/screen.hpp>
#include <ftxui/dom/elements.hpp>
#include <ftxui/component/component.hpp>
#include <ftxui/component/screen_interactive.hpp>
#include <thread>
#include <chrono>

using namespace ftxui;

namespace niskala {

TUIApp::TUIApp(std::shared_ptr<Config> config,
               std::shared_ptr<DataAggregator> data_aggregator,
               std::shared_ptr<MultiRegionFearGreed> fear_greed)
    : config_(config),
      data_aggregator_(data_aggregator),
      fear_greed_(fear_greed) {
}

TUIApp::~TUIApp() {
    stop();
}

void TUIApp::initialize() {
    LOG_INFO("Initializing Niskala TUI...");

    // Ensure default watchlist
    auto watchlist = config_->get_watchlist();
    if (watchlist.empty()) {
        LOG_INFO("No watchlist found, using defaults");
    }

    // Create screen instances
    setup_screens();

    LOG_INFO("TUI initialized with " + std::to_string(watchlist.size()) + " watchlist stocks");
}

void TUIApp::setup_screens() {
    dashboard_ = std::make_shared<DashboardScreen>(config_, data_aggregator_, fear_greed_);
    market_    = std::make_shared<MarketScreen>(config_, data_aggregator_);
    chart_     = std::make_shared<ChartScreen>(config_, data_aggregator_);
    news_      = std::make_shared<NewsScreen>(config_, data_aggregator_);
    screener_  = std::make_shared<ScreenerScreen>(config_, data_aggregator_);
    portfolio_ = std::make_shared<PortfolioScreen>(config_, data_aggregator_);
    settings_  = std::make_shared<SettingsScreen>(config_, data_aggregator_);
}

void TUIApp::run() {
    running_ = true;
    initialize();

    // Create FTXUI interactive screen
    auto screen = ScreenInteractive::Fullscreen();

    // Current screen accessor
    auto get_current_screen = [this]() -> std::shared_ptr<ScreenBase> {
        switch (current_screen_) {
            case Screen::Dashboard: return dashboard_;
            case Screen::Market:    return market_;
            case Screen::Chart:     return chart_;
            case Screen::News:      return news_;
            case Screen::Screener:  return screener_;
            case Screen::Portfolio: return portfolio_;
            case Screen::Settings:  return settings_;
            default: return dashboard_;
        }
    };

    // Initial data refresh
    try {
        dashboard_->refresh();
    } catch (const std::exception& e) {
        LOG_ERROR("Initial refresh failed: " + std::string(e.what()));
    }

    // Main component
    int refresh_counter = 0;
    int refresh_interval = config_->get_refresh_interval();

    auto main_component = Renderer([&] {
        auto current = get_current_screen();

        // Auto-refresh data
        refresh_counter++;
        if (refresh_counter >= refresh_interval * 10) {
            refresh_counter = 0;
            try {
                current->refresh();
            } catch (const std::exception& e) {
                LOG_ERROR("Refresh failed: " + std::string(e.what()));
            }
        }

        return current->render();
    });

    // Event handler
    main_component = CatchEvent(main_component, [&](Event event) {
        // Quit
        if (event == Event::Character('q') || event == Event::Escape) {
            running_ = false;
            screen.ExitLoopClosure()();
            return true;
        }

        // Screen navigation: F1-F7
        if (event == Event::F1) {
            current_screen_ = Screen::Dashboard;
            try { dashboard_->refresh(); } catch (...) {}
            return true;
        }
        if (event == Event::F2) {
            current_screen_ = Screen::Market;
            try { market_->refresh(); } catch (...) {}
            return true;
        }
        if (event == Event::F3) {
            current_screen_ = Screen::Chart;
            try { chart_->refresh(); } catch (...) {}
            return true;
        }
        if (event == Event::F4) {
            current_screen_ = Screen::Screener;
            try { screener_->refresh(); } catch (...) {}
            return true;
        }
        if (event == Event::F5) {
            current_screen_ = Screen::Portfolio;
            try { portfolio_->refresh(); } catch (...) {}
            return true;
        }
        if (event == Event::F6) {
            current_screen_ = Screen::News;
            try { news_->refresh(); } catch (...) {}
            return true;
        }
        if (event == Event::F7) {
            current_screen_ = Screen::Settings;
            try { settings_->refresh(); } catch (...) {}
            return true;
        }

        // Number keys as alternative navigation
        if (event == Event::Character('1')) {
            current_screen_ = Screen::Dashboard;
            return true;
        }
        if (event == Event::Character('2')) {
            current_screen_ = Screen::Market;
            return true;
        }
        if (event == Event::Character('3')) {
            current_screen_ = Screen::Chart;
            return true;
        }
        if (event == Event::Character('4')) {
            current_screen_ = Screen::Screener;
            return true;
        }
        if (event == Event::Character('5')) {
            current_screen_ = Screen::Portfolio;
            return true;
        }
        if (event == Event::Character('6')) {
            current_screen_ = Screen::News;
            return true;
        }
        if (event == Event::Character('7')) {
            current_screen_ = Screen::Settings;
            return true;
        }

        // Forward to current screen
        auto current = get_current_screen();
        return current->on_event(event);
    });

    // Run the main loop
    screen.Loop(main_component);
}

void TUIApp::stop() {
    running_ = false;
}

bool TUIApp::is_running() const {
    return running_;
}

} // namespace niskala
