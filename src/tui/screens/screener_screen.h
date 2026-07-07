// Niskala - Screener Screen Header
// Version: 1.0.0

#pragma once

#include "tui/screens/screen_interface.h"
#include "core/common/types.h"
#include <memory>
#include <vector>
#include <string>

namespace niskala {

class Config;
class DataAggregator;

class ScreenerScreen : public ScreenBase {
public:
    ScreenerScreen(
        std::shared_ptr<Config> config,
        std::shared_ptr<DataAggregator> data_aggregator
    );
    ~ScreenerScreen() override = default;

    Element render() override;
    bool on_event(Event event) override;
    void refresh() override;
    std::string name() const override { return "Screener"; }

private:
    std::shared_ptr<Config> config_;
    std::shared_ptr<DataAggregator> data_aggregator_;

    std::vector<StockQuote> results_;
    std::string filter_text_;
    int selected_row_ = 0;
};

} // namespace niskala
