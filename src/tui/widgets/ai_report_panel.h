// Niskala - AI Report Panel Widget Header
// Version: 1.0.0

#pragma once

#include "core/common/types.h"
#include <ftxui/ftxui.hpp>
#include <vector>
#include <string>

namespace niskala {

using namespace ftxui;

class AIReportPanel {
public:
    AIReportPanel() = default;
    ~AIReportPanel() = default;

    void set_signals(const std::vector<AISignal>& signals);
    Element render();

private:
    std::vector<AISignal> signals_;
};

} // namespace niskala
