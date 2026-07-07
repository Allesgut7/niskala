// Niskala - Configuration Implementation
// Version: 1.0.0

#include "core/common/config.h"
#include <fstream>
#include <nlohmann/json.hpp>

using json = nlohmann::json;

namespace niskala {

const std::vector<std::string> Config::DEFAULT_WATCHLIST = {
    "BBCA", "BBRI", "BMRI", "TLKM", "GOTO", "ADRO", "UNVR", "ICBP", "ASII", "PGAS"
};

const int Config::DEFAULT_REFRESH_INTERVAL = 5;
const std::string Config::DEFAULT_THEME = "dark";

Config::Config() {
    // Set default values
    data_["watchlist"] = DEFAULT_WATCHLIST;
    data_["refresh_interval"] = DEFAULT_REFRESH_INTERVAL;
    data_["theme"] = DEFAULT_THEME;
}

Config::~Config() = default;

bool Config::load(const std::string& filepath) {
    try {
        std::ifstream file(filepath);
        if (!file.is_open()) {
            return false;
        }
        
        json j;
        file >> j;
        
        // Parse watchlist
        if (j.contains("watchlist")) {
            std::vector<std::string> watchlist;
            for (const auto& item : j["watchlist"]) {
                watchlist.push_back(item.get<std::string>());
            }
            data_["watchlist"] = watchlist;
        }
        
        // Parse refresh interval
        if (j.contains("refresh_interval")) {
            data_["refresh_interval"] = j["refresh_interval"].get<int>();
        }
        
        // Parse theme
        if (j.contains("theme")) {
            data_["theme"] = j["theme"].get<std::string>();
        }
        
        return true;
        
    } catch (const std::exception& e) {
        return false;
    }
}

bool Config::save(const std::string& filepath) {
    try {
        json j;
        
        // Save watchlist
        auto watchlist = get_watchlist();
        j["watchlist"] = watchlist;
        
        // Save refresh interval
        j["refresh_interval"] = get_refresh_interval();
        
        // Save theme
        j["theme"] = get_theme();
        
        std::ofstream file(filepath);
        file << j.dump(4);
        
        return true;
        
    } catch (const std::exception& e) {
        return false;
    }
}

std::vector<std::string> Config::get_watchlist() const {
    try {
        return std::any_cast<std::vector<std::string>>(data_.at("watchlist"));
    } catch (...) {
        return DEFAULT_WATCHLIST;
    }
}

int Config::get_refresh_interval() const {
    try {
        return std::any_cast<int>(data_.at("refresh_interval"));
    } catch (...) {
        return DEFAULT_REFRESH_INTERVAL;
    }
}

std::string Config::get_theme() const {
    try {
        return std::any_cast<std::string>(data_.at("theme"));
    } catch (...) {
        return DEFAULT_THEME;
    }
}

} // namespace niskala
