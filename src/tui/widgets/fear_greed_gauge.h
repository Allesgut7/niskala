// Niskala - Fear & Greed Gauge Widget Header
// Version: 1.0.0

#pragma once

#include "core/common/types.h"
#include <ftxui/ftxui.hpp>
#include <string>

namespace niskala {

using namespace ftxui;

// Forward declare
struct FearGreedResult;

class FearGreedGauge {
public:
    FearGreedGauge() = default;
    ~FearGreedGauge() = default;

    void set_label(const std::string& label);
    void set_score(int score);
    void set_status(const std::string& status);
    Element render();

private:
    std::string label_ = "FGI";
    int score_ = 50;
    std::string status_ = "Neutral";
};

} // namespace niskala
