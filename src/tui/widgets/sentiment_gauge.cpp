// Niskala - Sentiment Gauge Widget Implementation
// Version: 1.0.0

#include "tui/widgets/sentiment_gauge.h"
#include <ftxui/ftxui.hpp>

using namespace ftxui;

namespace niskala {

void SentimentGauge::set_label(const std::string& label) {
    label_ = label;
}

void SentimentGauge::set_score(int score) {
    score_ = score;
}

Element SentimentGauge::render() {
    auto clr = score_ > 0 ? Color::Green
             : score_ < 0 ? Color::Red
             : Color::GrayLight;

    Elements items;
    items.push_back(text(label_) | bold | center);
    items.push_back(text(std::to_string(score_)) | color(clr) | bold | center);
    items.push_back(text(score_ > 0 ? "BULLISH" : score_ < 0 ? "BEARISH" : "NEUTRAL") | color(clr) | center);
    
    return vbox(items) | border | flex;
}

} // namespace niskala
