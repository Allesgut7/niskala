// Niskala - Sentiment Gauge Widget Header
// Version: 1.0.0

#pragma once

#include "core/common/types.h"
#include <ftxui/ftxui.hpp>
#include <string>

namespace niskala {

using namespace ftxui;

class SentimentGauge {
public:
    SentimentGauge() = default;
    ~SentimentGauge() = default;

    void set_label(const std::string& label);
    void set_score(int score); // -100 to +100
    Element render();

private:
    std::string label_ = "Sentiment";
    int score_ = 0;
};

} // namespace niskala
