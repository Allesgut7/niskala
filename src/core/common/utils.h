// Niskala - Utilities Header
// Version: 1.0.0

#pragma once

#include <string>
#include <sstream>
#include <iomanip>
#include <vector>
#include <cmath>

namespace niskala {

// Format number with thousands separator
inline std::string format_number(double value, int decimals = 0) {
    std::ostringstream oss;
    oss << std::fixed << std::setprecision(decimals);
    
    if (value >= 1e12) {
        oss << value / 1e12 << "T";
    } else if (value >= 1e9) {
        oss << value / 1e9 << "B";
    } else if (value >= 1e6) {
        oss << value / 1e6 << "M";
    } else if (value >= 1e3 && decimals == 0) {
        oss << std::fixed << std::setprecision(0) << value;
    } else {
        oss << value;
    }
    
    return oss.str();
}

// Format percentage
inline std::string format_pct(double value, int decimals = 2) {
    std::ostringstream oss;
    oss << std::fixed << std::setprecision(decimals);
    if (value > 0) oss << "+";
    oss << value << "%";
    return oss.str();
}

// Format price in IDR
inline std::string format_price(double price) {
    std::ostringstream oss;
    oss.imbue(std::locale(""));
    oss << std::fixed << std::setprecision(0) << price;
    return oss.str();
}

// Get arrow symbol for change direction
inline std::string change_arrow(double change) {
    if (change > 0) return "+";
    if (change < 0) return "-";
    return " ";
}

// String split
inline std::vector<std::string> split(const std::string& s, char delimiter) {
    std::vector<std::string> tokens;
    std::string token;
    std::istringstream iss(s);
    while (std::getline(iss, token, delimiter)) {
        tokens.push_back(token);
    }
    return tokens;
}

// Trim whitespace
inline std::string trim(const std::string& s) {
    size_t start = s.find_first_not_of(" \t\n\r");
    if (start == std::string::npos) return "";
    size_t end = s.find_last_not_of(" \t\n\r");
    return s.substr(start, end - start + 1);
}

// To uppercase
inline std::string to_upper(const std::string& s) {
    std::string result = s;
    for (auto& c : result) c = std::toupper(c);
    return result;
}

} // namespace niskala
