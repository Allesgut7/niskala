// Niskala - Cache Manager Header
// Version: 1.0.0

#pragma once

#include "core/common/types.h"
#include <string>
#include <map>
#include <chrono>
#include <mutex>

namespace niskala {

template<typename T>
struct CacheEntry {
    T data;
    std::chrono::system_clock::time_point timestamp;
};

class CacheManager {
public:
    CacheManager(int ttl_seconds = 5);
    ~CacheManager();
    
    // Cache operations
    void put(const std::string& key, const StockQuote& data);
    bool get(const std::string& key, StockQuote& data);
    void clear();
    bool is_valid(const std::string& key);
    
    // Statistics
    int size() const;
    int hit_count() const { return hits_; }
    int miss_count() const { return misses_; }
    double hit_rate() const;
    
private:
    std::map<std::string, CacheEntry<StockQuote>> cache_;
    int ttl_seconds_;
    mutable std::mutex mutex_;
    
    int hits_;
    int misses_;
    
    bool is_expired(const CacheEntry<StockQuote>& entry) const;
};

} // namespace niskala
