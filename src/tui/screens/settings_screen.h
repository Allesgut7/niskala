// Niskala - Settings Screen Header
// Version: 1.0.0

#pragma once

#include "tui/screens/screen_interface.h"
#include <memory>
#include <string>

namespace niskala {

class Config;
class DataAggregator;

class SettingsScreen : public ScreenBase {
public:
    SettingsScreen(
        std::shared_ptr<Config> config,
        std::shared_ptr<DataAggregator> data_aggregator
    );
    ~SettingsScreen() override = default;

    Element render() override;
    bool on_event(Event event) override;
    void refresh() override;
    std::string name() const override { return "Settings"; }

private:
    std::shared_ptr<Config> config_;
    std::shared_ptr<DataAggregator> data_aggregator_;

    int selected_row_ = 0;
};

} // namespace niskala
