// Niskala - Stock Table Widget Implementation
// Version: 1.0.0

#include "tui/widgets/stock_table.h"
#include <ftxui/ftxui.hpp>
#include <algorithm>

using namespace ftxui;

namespace niskala {

void StockTable::set_data(const std::vector<StockQuote>& stocks) {
    stocks_ = stocks;
}

void StockTable::set_sort(SortColumn column, SortDirection direction) {
    sort_column_ = column;
    sort_direction_ = direction;
}

void StockTable::sort() {
    std::sort(stocks_.begin(), stocks_.end(),
        [this](const StockQuote& a, const StockQuote& b) {
            bool asc = (sort_direction_ == SortDirection::Ascending);
            switch (sort_column_) {
                case SortColumn::Symbol:    return asc ? a.symbol < b.symbol : a.symbol > b.symbol;
                case SortColumn::Price:     return asc ? a.price < b.price : a.price > b.price;
                case SortColumn::Change:    return asc ? a.change < b.change : a.change > b.change;
                case SortColumn::ChangePct: return asc ? a.change_pct < b.change_pct : a.change_pct > b.change_pct;
                case SortColumn::Volume:    return asc ? a.volume < b.volume : a.volume > b.volume;
                case SortColumn::MarketCap: return asc ? a.market_cap < b.market_cap : a.market_cap > b.market_cap;
                case SortColumn::Sector:    return asc ? a.sector < b.sector : a.sector > b.sector;
            }
            return false;
        });
}

void StockTable::set_selected_row(int row) {
    selected_row_ = row;
}

int StockTable::selected_row() const {
    return selected_row_;
}

Element StockTable::render() {
    Elements header_items;
    header_items.push_back(text("SYMBOL") | bold | size(WIDTH, EQUAL, 8));
    header_items.push_back(text("PRICE")  | bold | size(WIDTH, EQUAL, 10));
    header_items.push_back(text("CHG%")   | bold | size(WIDTH, EQUAL, 8));
    header_items.push_back(text("VOLUME") | bold | size(WIDTH, EQUAL, 12));
    header_items.push_back(text("SECTOR") | bold | size(WIDTH, EQUAL, 12));
    auto header = hbox(header_items);

    Elements rows;
    for (int i = 0; i < static_cast<int>(stocks_.size()); i++) {
        const auto& s = stocks_[i];
        auto clr = s.change >= 0 ? Color::Green : Color::Red;
        
        Elements row_items;
        row_items.push_back(text(s.symbol) | bold | size(WIDTH, EQUAL, 8));
        row_items.push_back(text(std::to_string(s.price)) | size(WIDTH, EQUAL, 10));
        row_items.push_back(text(std::to_string(s.change_pct)) | color(clr) | size(WIDTH, EQUAL, 8));
        row_items.push_back(text(std::to_string(s.volume)) | size(WIDTH, EQUAL, 12));
        row_items.push_back(text(s.sector) | size(WIDTH, EQUAL, 12));
        
        auto row = hbox(row_items);
        if (i == selected_row_) row = row | inverted;
        rows.push_back(row);
    }

    Elements table_items;
    table_items.push_back(header);
    table_items.push_back(separator());
    table_items.push_back(vbox(rows) | vscroll_indicator | yframe);
    
    return vbox(table_items) | border | flex;
}

} // namespace niskala
