// Niskala - Portfolio Screen Header
// Version: 1.0.0

#pragma once

#include "tui/screens/screen_interface.h"
#include <memory>
#include <vector>

namespace niskala {

class Config;
class DataAggregator;

class PortfolioScreen : public ScreenBase {
public:
    PortfolioScreen(
        std::shared_ptr<Config> config,
        std::shared_ptr<DataAggregator> data_aggregator
    );
    ~PortfolioScreen() override = default;

    Element render() override;
    bool on_event(Event event) override;
    void refresh() override;
    std::string name() const override { return "Portfolio"; }

private:
    std::shared_ptr<Config> config_;
    std::shared_ptr<DataAggregator> data_aggregator_;

    int selected_row_ = 0;
};

} // namespace niskala
