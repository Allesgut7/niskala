// Niskala - Sector Heatmap Widget Header
// Version: 1.0.0

#pragma once

#include "core/common/types.h"
#include <ftxui/ftxui.hpp>
#include <vector>
#include <string>

namespace niskala {

using namespace ftxui;

class SectorHeatmap {
public:
    SectorHeatmap() = default;
    ~SectorHeatmap() = default;

    void set_sectors(const std::vector<SectorPerformance>& sectors);
    Element render();

private:
    std::vector<SectorPerformance> sectors_;
};

} // namespace niskala
