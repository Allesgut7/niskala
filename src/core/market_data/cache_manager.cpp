// Niskala - Cache Manager Implementation
// Version: 1.0.0

#include "core/market_data/cache_manager.h"
#include "core/common/logger.h"

namespace niskala {

CacheManager::CacheManager(int ttl_seconds)
    : ttl_seconds_(ttl_seconds), hits_(0), misses_(0) {
    LOG_INFO("Cache manager initialized with TTL=" + std::to_string(ttl_seconds) + "s");
}

CacheManager::~CacheManager() {
    LOG_INFO("Cache stats - Hits: " + std::to_string(hits_) + 
             ", Misses: " + std::to_string(misses_) + 
             ", Hit rate: " + std::to_string(hit_rate() * 100) + "%");
}

void CacheManager::put(const std::string& key, const StockQuote& data) {
    std::lock_guard<std::mutex> lock(mutex_);
    
    CacheEntry<StockQuote> entry;
    entry.data = data;
    entry.timestamp = std::chrono::system_clock::now();
    
    cache_[key] = entry;
}

bool CacheManager::get(const std::string& key, StockQuote& data) {
    std::lock_guard<std::mutex> lock(mutex_);
    
    auto it = cache_.find(key);
    if (it == cache_.end()) {
        misses_++;
        return false;
    }
    
    if (is_expired(it->second)) {
        cache_.erase(it);
        misses_++;
        return false;
    }
    
    data = it->second.data;
    hits_++;
    return true;
}

void CacheManager::clear() {
    std::lock_guard<std::mutex> lock(mutex_);
    cache_.clear();
    LOG_INFO("Cache cleared");
}

bool CacheManager::is_valid(const std::string& key) {
    std::lock_guard<std::mutex> lock(mutex_);
    
    auto it = cache_.find(key);
    if (it == cache_.end()) {
        return false;
    }
    
    return !is_expired(it->second);
}

int CacheManager::size() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return cache_.size();
}

double CacheManager::hit_rate() const {
    int total = hits_ + misses_;
    if (total == 0) return 0.0;
    return static_cast<double>(hits_) / total;
}

bool CacheManager::is_expired(const CacheEntry<StockQuote>& entry) const {
    auto now = std::chrono::system_clock::now();
    auto elapsed = std::chrono::duration_cast<std::chrono::seconds>(now - entry.timestamp);
    return elapsed.count() >= ttl_seconds_;
}

} // namespace niskala
