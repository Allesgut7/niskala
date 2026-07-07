// Niskala - Stock Table Widget Header
// Version: 1.0.0

#pragma once

#include "core/common/types.h"
#include <ftxui/ftxui.hpp>
#include <vector>
#include <string>
#include <functional>

namespace niskala {

using namespace ftxui;

class StockTable {
public:
    StockTable() = default;
    ~StockTable() = default;

    void set_data(const std::vector<StockQuote>& stocks);
    void set_sort(SortColumn column, SortDirection direction);
    void sort();
    void set_selected_row(int row);
    int selected_row() const;
    Element render();

private:
    std::vector<StockQuote> stocks_;
    SortColumn sort_column_ = SortColumn::Symbol;
    SortDirection sort_direction_ = SortDirection::Ascending;
    int selected_row_ = 0;
};

} // namespace niskala
