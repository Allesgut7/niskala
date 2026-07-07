// Niskala - Configuration Header
// Version: 1.0.0

#pragma once

#include <string>
#include <map>
#include <vector>
#include <any>

namespace niskala {

class Config {
public:
    Config();
    ~Config();
    
    // Load configuration from file
    bool load(const std::string& filepath);
    
    // Save configuration to file
    bool save(const std::string& filepath);
    
    // Get configuration value
    template<typename T>
    T get(const std::string& key, const T& default_value = T{}) const;
    
    // Set configuration value
    template<typename T>
    void set(const std::string& key, const T& value);
    
    // Get default watchlist
    std::vector<std::string> get_watchlist() const;
    
    // Get refresh interval in seconds
    int get_refresh_interval() const;
    
    // Get theme
    std::string get_theme() const;
    
private:
    std::map<std::string, std::any> data_;
    
    // Default values
    static const std::vector<std::string> DEFAULT_WATCHLIST;
    static const int DEFAULT_REFRESH_INTERVAL;
    static const std::string DEFAULT_THEME;
};

} // namespace niskala
