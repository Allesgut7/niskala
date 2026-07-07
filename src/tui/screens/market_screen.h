// Niskala - Market Screen Header
// Version: 1.0.0

#pragma once

#include "tui/screens/screen_interface.h"
#include "core/common/types.h"
#include <memory>
#include <vector>

namespace niskala {

class Config;
class DataAggregator;

class MarketScreen : public ScreenBase {
public:
    MarketScreen(
        std::shared_ptr<Config> config,
        std::shared_ptr<DataAggregator> data_aggregator
    );
    ~MarketScreen() override = default;

    Element render() override;
    bool on_event(Event event) override;
    void refresh() override;
    std::string name() const override { return "Market"; }

private:
    std::shared_ptr<Config> config_;
    std::shared_ptr<DataAggregator> data_aggregator_;

    std::vector<StockQuote> stocks_;
    int selected_row_ = 0;
    SortColumn sort_column_ = SortColumn::Symbol;
    SortDirection sort_direction_ = SortDirection::Ascending;
};

} // namespace niskala
