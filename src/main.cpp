// Niskala - Main Entry Point
// Version: 1.0.1 (Added Python initialization)

#include <iostream>
#include <memory>
#include <string>
#include <filesystem>

#include <pybind11/embed.h>

#include "core/common/config.h"
#include "core/common/logger.h"
#include "core/market_data/data_aggregator.h"
#include "core/fear_greed/multi_region.h"
#include "tui/app.h"

namespace py = pybind11;

int main(int argc, char* argv[]) {
    // Initialize Python interpreter
    py::scoped_interpreter guard{};
    
    // Add venv site-packages to sys.path
    try {
        py::module_ sys = py::module_::import("sys");
        py::list path = sys.attr("path");
        
        std::string venv_site_packages = std::filesystem::absolute(".venv/lib/python3.10/site-packages").string();
        path.insert(0, venv_site_packages);
        
        std::cerr << "[DEBUG] Added venv site-packages to Python path: " << venv_site_packages << std::endl;
    } catch (const std::exception& e) {
        std::cerr << "[WARN] Failed to add venv to Python path: " << e.what() << std::endl;
    }
    
    // Initialize logger
    niskala::Logger::instance().set_level(niskala::LogLevel::INFO);
    niskala::Logger::instance().set_file("data/niskala.log");

    LOG_INFO("========================================");
    LOG_INFO("Niskala - Terminal Trading Indonesia");
    LOG_INFO("Version 1.0.0");
    LOG_INFO("========================================");

    try {
        // Determine config path
        std::string config_path = "config/default.json";
        for (int i = 1; i < argc; i++) {
            std::string arg = argv[i];
            if (arg == "--config" && i + 1 < argc) {
                config_path = argv[i + 1];
            }
            if (arg == "--help" || arg == "-h") {
                std::cout << "Niskala - Terminal Trading Indonesia\n\n"
                          << "Usage: niskala [OPTIONS]\n\n"
                          << "Options:\n"
                          << "  --config PATH   Config file path (default: config/default.json)\n"
                          << "  --help, -h      Show this help\n\n"
                          << "Keyboard shortcuts:\n"
                          << "  F1  Dashboard\n"
                          << "  F2  Market Overview\n"
                          << "  F3  Chart\n"
                          << "  F4  Screener\n"
                          << "  F5  Portfolio\n"
                          << "  F6  News Feed\n"
                          << "  F7  Settings\n"
                          << "  q   Quit\n";
                return 0;
            }
        }

        // Load configuration
        LOG_INFO("Loading config from: " + config_path);
        std::cerr << "[DEBUG] Loading config..." << std::endl;
        auto config = std::make_shared<niskala::Config>();
        if (!config->load(config_path)) {
            LOG_WARN("Config file not found, using defaults");
            std::cerr << "[DEBUG] Config file not found, using defaults" << std::endl;
        }

        // Initialize data aggregator
        LOG_INFO("Initializing data aggregator...");
        std::cerr << "[DEBUG] Initializing data aggregator..." << std::endl;
        auto data_aggregator = std::make_shared<niskala::DataAggregator>(config);

        // Initialize Fear & Greed calculator
        LOG_INFO("Initializing Fear & Greed calculator...");
        std::cerr << "[DEBUG] Initializing Fear & Greed calculator..." << std::endl;
        auto fear_greed = std::make_shared<niskala::MultiRegionFearGreed>(data_aggregator);

        // Initialize and run TUI
        LOG_INFO("Starting TUI application...");
        std::cerr << "[DEBUG] Starting TUI application..." << std::endl;
        auto app = std::make_shared<niskala::TUIApp>(config, data_aggregator, fear_greed);
        std::cerr << "[DEBUG] Calling app->run()..." << std::endl;
        app->run();

        LOG_INFO("Application terminated normally");

    } catch (const std::exception& e) {
        LOG_FATAL("Fatal error: " + std::string(e.what()));
        std::cerr << "Fatal error: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}
