// Niskala - Fear & Greed Gauge Widget Implementation
// Version: 1.0.0

#include "tui/widgets/fear_greed_gauge.h"
#include <ftxui/ftxui.hpp>

using namespace ftxui;

namespace niskala {

void FearGreedGauge::set_label(const std::string& label) {
    label_ = label;
}

void FearGreedGauge::set_score(int score) {
    score_ = score;
}

void FearGreedGauge::set_status(const std::string& status) {
    status_ = status;
}

Element FearGreedGauge::render() {
    auto clr = Color::Yellow;
    if (score_ <= 25) clr = Color::Red;
    else if (score_ <= 45) clr = Color::Yellow;
    else if (score_ >= 75) clr = Color::Green;
    else if (score_ >= 55) clr = Color::Cyan;

    Elements items;
    items.push_back(text(label_) | bold | center);
    items.push_back(text(std::to_string(score_)) | color(clr) | bold | center);
    items.push_back(text(status_) | color(clr) | center);
    
    return vbox(items) | border | flex;
}

} // namespace niskala
