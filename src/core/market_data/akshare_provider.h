// Niskala - Akshare Provider Header
// Version: 1.0.0

#pragma once

#include "core/common/types.h"
#include <string>
#include <vector>

namespace niskala {

class AkshareProvider {
public:
    AkshareProvider();
    ~AkshareProvider();
    
    // Get stock quote
    StockQuote get_quote(const std::string& symbol);
    
    // Get global indices
    std::vector<StockQuote> get_indices();
    
    // Get commodity prices
    std::vector<StockQuote> get_commodities();
    
    // Get forex rates
    std::vector<StockQuote> get_forex_rates();
    
private:
    void* py_client_;
    
    void init_python();
    void cleanup_python();
};

} // namespace niskala
