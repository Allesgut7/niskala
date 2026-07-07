// Niskala - TUI Application Header
// Version: 1.0.0

#pragma once

#include <memory>
#include <string>
#include <vector>
#include <atomic>

namespace niskala {

class Config;
class DataAggregator;
class MultiRegionFearGreed;
class DashboardScreen;
class MarketScreen;
class ChartScreen;
class NewsScreen;
class ScreenerScreen;
class PortfolioScreen;
class SettingsScreen;

class TUIApp {
public:
    TUIApp(std::shared_ptr<Config> config,
           std::shared_ptr<DataAggregator> data_aggregator,
           std::shared_ptr<MultiRegionFearGreed> fear_greed);

    ~TUIApp();

    void run();
    void stop();
    bool is_running() const;

private:
    std::shared_ptr<Config> config_;
    std::shared_ptr<DataAggregator> data_aggregator_;
    std::shared_ptr<MultiRegionFearGreed> fear_greed_;

    std::atomic<bool> running_{false};

    enum class Screen {
        Dashboard,
        Market,
        Chart,
        News,
        Screener,
        Portfolio,
        Settings
    };

    Screen current_screen_ = Screen::Dashboard;

    // Screen instances
    std::shared_ptr<DashboardScreen> dashboard_;
    std::shared_ptr<MarketScreen> market_;
    std::shared_ptr<ChartScreen> chart_;
    std::shared_ptr<NewsScreen> news_;
    std::shared_ptr<ScreenerScreen> screener_;
    std::shared_ptr<PortfolioScreen> portfolio_;
    std::shared_ptr<SettingsScreen> settings_;

    void initialize();
    void setup_screens();
};

} // namespace niskala
