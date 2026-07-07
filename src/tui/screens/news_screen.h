// Niskala - News Screen Header
// Version: 1.0.0

#pragma once

#include "tui/screens/screen_interface.h"
#include "core/common/types.h"
#include <memory>
#include <vector>

namespace niskala {

class Config;
class DataAggregator;

class NewsScreen : public ScreenBase {
public:
    NewsScreen(
        std::shared_ptr<Config> config,
        std::shared_ptr<DataAggregator> data_aggregator
    );
    ~NewsScreen() override = default;

    Element render() override;
    bool on_event(Event event) override;
    void refresh() override;
    std::string name() const override { return "News"; }

private:
    std::shared_ptr<Config> config_;
    std::shared_ptr<DataAggregator> data_aggregator_;

    std::vector<NewsArticle> articles_;
    int selected_row_ = 0;
};

} // namespace niskala
