// Niskala - Sector Heatmap Widget Implementation
// Version: 1.0.0

#include "tui/widgets/sector_heatmap.h"
#include <ftxui/ftxui.hpp>

using namespace ftxui;

namespace niskala {

void SectorHeatmap::set_sectors(const std::vector<SectorPerformance>& sectors) {
    sectors_ = sectors;
}

Element SectorHeatmap::render() {
    Elements cells;
    for (const auto& s : sectors_) {
        auto clr = s.change_pct >= 0 ? Color::Green : Color::Red;
        
        Elements cell_items;
        cell_items.push_back(text(s.name) | bold | center);
        cell_items.push_back(text(std::to_string(s.change_pct) + "%") | center);
        
        cells.push_back(vbox(cell_items) | border | color(clr) | flex);
    }
    
    // Create simple grid using hbox rows
    Elements grid_rows;
    for (size_t i = 0; i < cells.size(); i += 3) {
        Elements row;
        for (size_t j = i; j < std::min(i + 3, cells.size()); j++) {
            row.push_back(cells[j]);
        }
        grid_rows.push_back(hbox(row));
    }
    
    Elements heatmap_items;
    heatmap_items.push_back(text(" Sector Heatmap") | bold);
    heatmap_items.push_back(vbox(grid_rows));
    
    return vbox(heatmap_items) | border | flex;
}

} // namespace niskala
