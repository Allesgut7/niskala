// Niskala - Akshare Provider Implementation
// Version: 1.0.1 (Fixed Python initialization)

#include "core/market_data/akshare_provider.h"
#include "core/common/logger.h"
#include <pybind11/embed.h>
#include <pybind11/stl.h>
#include <filesystem>

namespace py = pybind11;

namespace niskala {

AkshareProvider::AkshareProvider() : py_client_(nullptr) {
    try {
        init_python();
    } catch (const std::exception& e) {
        LOG_ERROR("Akshare provider init failed (will use mock data): " + std::string(e.what()));
        py_client_ = nullptr;
    }
}

AkshareProvider::~AkshareProvider() {
    cleanup_python();
}

void AkshareProvider::init_python() {
    try {
        // Check if Python interpreter is initialized
        if (!Py_IsInitialized()) {
            LOG_WARN("Python interpreter not initialized, skipping Akshare setup");
            return;
        }
        
        py::module_ sys = py::module_::import("sys");
        py::list path = sys.attr("path");
        
        // Add python directory to path (use absolute path)
        std::string python_path = std::filesystem::absolute("python").string();
        
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
        }
        
        py::module_ data_sources = py::module_::import("data_sources");
        py::object client_class = data_sources.attr("AkshareClient");
        
        py_client_ = new py::object(client_class());
        
        LOG_INFO("Akshare provider initialized");
        
    } catch (const py::error_already_set& e) {
        LOG_ERROR("Python error in Akshare init: " + std::string(e.what()));
        py_client_ = nullptr;
    } catch (const std::exception& e) {
        LOG_ERROR("Failed to initialize Akshare provider: " + std::string(e.what()));
        py_client_ = nullptr;
    }
}

void AkshareProvider::cleanup_python() {
    if (py_client_) {
        try {
            delete static_cast<py::object*>(py_client_);
        } catch (...) {
            // Ignore cleanup errors
        }
        py_client_ = nullptr;
    }
}

StockQuote AkshareProvider::get_quote(const std::string& symbol) {
    StockQuote quote;
    
    if (!py_client_) {
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
        
    } catch (const std::exception& e) {
        LOG_ERROR("Akshare error for " + symbol + ": " + std::string(e.what()));
    }
    
    return quote;
}

std::vector<StockQuote> AkshareProvider::get_indices() {
    std::vector<StockQuote> quotes;
    // Not implemented yet
    return quotes;
}

std::vector<StockQuote> AkshareProvider::get_commodities() {
    std::vector<StockQuote> quotes;
    // Not implemented yet
    return quotes;
}

std::vector<StockQuote> AkshareProvider::get_forex_rates() {
    std::vector<StockQuote> quotes;
    // Not implemented yet
    return quotes;
}

} // namespace niskala
