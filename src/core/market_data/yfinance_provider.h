// Niskala - YFinance Provider Header
// Version: 1.0.0

#pragma once

#include "core/common/types.h"
#include <string>
#include <vector>
#include <memory>

namespace niskala {

class YFinanceProvider {
public:
    YFinanceProvider();
    ~YFinanceProvider();
    
    // Get single stock quote
    StockQuote get_quote(const std::string& symbol);
    
    // Get multiple quotes
    std::vector<StockQuote> get_quotes(const std::vector<std::string>& symbols);
    
    // Get index data
    StockQuote get_index(const std::string& symbol);
    
    // Get commodity price
    StockQuote get_commodity(const std::string& symbol);
    
    // Get forex rate
    StockQuote get_forex(const std::string& symbol);
    
private:
    // Python module handle
    void* py_module_;
    void* py_client_;
    
    // Initialize Python bridge
    void init_python();
    void cleanup_python();
    
    // Convert Python dict to StockQuote
    StockQuote parse_stock_data(void* py_dict);
};

} // namespace niskala
