// Niskala - YFinance Provider Implementation
// Version: 1.0.1 (Fixed Python initialization)

#include "core/market_data/yfinance_provider.h"
#include "core/common/logger.h"
#include <pybind11/embed.h>
#include <pybind11/stl.h>
#include <filesystem>

namespace py = pybind11;

namespace niskala {

YFinanceProvider::YFinanceProvider() : py_module_(nullptr), py_client_(nullptr) {
    try {
        init_python();
    } catch (const std::exception& e) {
        LOG_ERROR("YFinance provider init failed (will use mock data): " + std::string(e.what()));
        py_client_ = nullptr;
    }
}

YFinanceProvider::~YFinanceProvider() {
    cleanup_python();
}

void YFinanceProvider::init_python() {
    try {
        // Check if Python interpreter is initialized
        if (!Py_IsInitialized()) {
            LOG_WARN("Python interpreter not initialized, skipping YFinance setup");
            return;
        }
        
        // Import Python module
        py::module_ sys = py::module_::import("sys");
        py::list path = sys.attr("path");
        
        // Add python directory to path (use absolute path)
        std::string python_path = std::filesystem::absolute("python").string();
        
        // Check if path already in sys.path
        bool path_exists = false;
        for (auto item : path) {
            std::string item_str = py::str(item);
            if (item_str == python_path || item_str == "python") {
                path_exists = true;
                break;
            }
        }
        
        if (!path_exists) {
            path.insert(0, python_path);
            LOG_INFO("Added to Python path: " + python_path);
        }
        
        py::module_ data_sources = py::module_::import("data_sources");
        py::object client_class = data_sources.attr("YFinanceClient");
        
        // Create client instance
        py_client_ = new py::object(client_class());
        
        LOG_INFO("YFinance provider initialized");
        
    } catch (const py::error_already_set& e) {
        LOG_ERROR("Python error in YFinance init: " + std::string(e.what()));
        py_client_ = nullptr;
    } catch (const std::exception& e) {
        LOG_ERROR("Failed to initialize YFinance provider: " + std::string(e.what()));
        py_client_ = nullptr;
    }
}

void YFinanceProvider::cleanup_python() {
    if (py_client_) {
        try {
            delete static_cast<py::object*>(py_client_);
        } catch (...) {
            // Ignore cleanup errors
        }
        py_client_ = nullptr;
    }
}

StockQuote YFinanceProvider::get_quote(const std::string& symbol) {
    StockQuote quote;
    
    if (!py_client_) {
        LOG_ERROR("YFinance client not initialized");
        return quote;
    }
    
    try {
        py::object* client = static_cast<py::object*>(py_client_);
        py::dict result = client->attr("get_stock")(symbol);
        
        quote.symbol = result["symbol"].cast<std::string>();
        quote.name = result["name"].cast<std::string>();
        quote.price = result["price"].cast<double>();
        quote.change = result["change"].cast<double>();
        quote.change_pct = result["change_pct"].cast<double>();
        quote.volume = result["volume"].cast<int64_t>();
        quote.market_cap = result["market_cap"].cast<int64_t>();
        quote.sector = result["sector"].cast<std::string>();
        quote.pe_ratio = result["pe_ratio"].cast<double>();
        quote.timestamp = result["timestamp"].cast<std::string>();
        
    } catch (const std::exception& e) {
        LOG_ERROR("Error fetching quote for " + symbol + ": " + std::string(e.what()));
    }
    
    return quote;
}

std::vector<StockQuote> YFinanceProvider::get_quotes(const std::vector<std::string>& symbols) {
    std::vector<StockQuote> quotes;
    
    if (!py_client_) {
        LOG_ERROR("YFinance client not initialized");
        return quotes;
    }
    
    try {
        py::object* client = static_cast<py::object*>(py_client_);
        py::list py_result = client->attr("get_stocks_batch")(symbols);
        
        for (auto item : py_result) {
            py::dict result = item.cast<py::dict>();
            
            StockQuote quote;
            quote.symbol = result["symbol"].cast<std::string>();
            quote.name = result["name"].cast<std::string>();
            quote.price = result["price"].cast<double>();
            quote.change = result["change"].cast<double>();
            quote.change_pct = result["change_pct"].cast<double>();
            quote.volume = result["volume"].cast<int64_t>();
            quote.market_cap = result["market_cap"].cast<int64_t>();
            quote.sector = result["sector"].cast<std::string>();
            quote.pe_ratio = result["pe_ratio"].cast<double>();
            quote.timestamp = result["timestamp"].cast<std::string>();
            
            quotes.push_back(quote);
        }
        
    } catch (const std::exception& e) {
        LOG_ERROR("Error fetching batch quotes: " + std::string(e.what()));
    }
    
    return quotes;
}

StockQuote YFinanceProvider::get_index(const std::string& symbol) {
    StockQuote quote;
    
    if (!py_client_) {
        LOG_ERROR("YFinance client not initialized");
        return quote;
    }
    
    try {
        py::object* client = static_cast<py::object*>(py_client_);
        py::dict result = client->attr("get_index")(symbol);
        
        quote.symbol = result["symbol"].cast<std::string>();
        quote.name = result["name"].cast<std::string>();
        quote.price = result["price"].cast<double>();
        quote.change = result["change"].cast<double>();
        quote.change_pct = result["change_pct"].cast<double>();
        quote.volume = result["volume"].cast<int64_t>();
        quote.timestamp = result["timestamp"].cast<std::string>();
        
    } catch (const std::exception& e) {
        LOG_ERROR("Error fetching index " + symbol + ": " + std::string(e.what()));
    }
    
    return quote;
}

StockQuote YFinanceProvider::get_commodity(const std::string& symbol) {
    return get_index(symbol);
}

StockQuote YFinanceProvider::get_forex(const std::string& symbol) {
    return get_index(symbol);
}

StockQuote YFinanceProvider::parse_stock_data(void* py_dict) {
    StockQuote quote;
    // Parsing handled inline in get_quote/get_quotes
    return quote;
}

} // namespace niskala
