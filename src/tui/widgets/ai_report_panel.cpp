// Niskala - AI Report Panel Widget Implementation
// Version: 1.0.0

#include "tui/widgets/ai_report_panel.h"
#include <ftxui/ftxui.hpp>

using namespace ftxui;

namespace niskala {

void AIReportPanel::set_signals(const std::vector<AISignal>& signals) {
    signals_ = signals;
}

Element AIReportPanel::render() {
    Elements items;
    for (const auto& sig : signals_) {
        auto clr = sig.signal == "BUY"  ? Color::Green
                 : sig.signal == "SELL" ? Color::Red
                 : Color::Yellow;
        
        Elements sig_items;
        sig_items.push_back(text(sig.symbol) | bold | size(WIDTH, EQUAL, 8));
        sig_items.push_back(text(sig.signal) | color(clr) | size(WIDTH, EQUAL, 6));
        sig_items.push_back(text(std::to_string(sig.confidence) + "%") | size(WIDTH, EQUAL, 6));
        sig_items.push_back(text(sig.reason) | dim);
        
        items.push_back(hbox(sig_items));
    }
    if (items.empty()) {
        items.push_back(text(" No AI signals available") | dim);
    }
    
    Elements panel_items;
    panel_items.push_back(text(" AI Analysis Report") | bold);
    panel_items.push_back(separator());
    panel_items.push_back(vbox(items) | vscroll_indicator | yframe);
    
    return vbox(panel_items) | border | flex;
}

} // namespace niskala
