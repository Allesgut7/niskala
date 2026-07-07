// Niskala - Chart Screen Header
// Version: 1.0.0

#pragma once

#include "tui/screens/screen_interface.h"
#include <memory>
#include <string>

namespace niskala {

class Config;
class DataAggregator;

class ChartScreen : public ScreenBase {
public:
    ChartScreen(
        std::shared_ptr<Config> config,
        std::shared_ptr<DataAggregator> data_aggregator
    );
    ~ChartScreen() override = default;

    Element render() override;
    bool on_event(Event event) override;
    void refresh() override;
    std::string name() const override { return "Chart"; }

private:
    std::shared_ptr<Config> config_;
    std::shared_ptr<DataAggregator> data_aggregator_;

    std::string selected_symbol_;
    int timeframe_index_ = 0;
};

} // namespace niskala
