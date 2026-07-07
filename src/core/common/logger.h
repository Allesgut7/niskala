// Niskala - Logger Header
// Version: 1.0.0

#pragma once

#include <string>
#include <fstream>
#include <iostream>
#include <mutex>
#include <chrono>
#include <iomanip>
#include <sstream>

namespace niskala {

enum class LogLevel {
    DEBUG,
    INFO,
    WARNING,
    ERROR,
    FATAL
};

class Logger {
public:
    static Logger& instance() {
        static Logger logger;
        return logger;
    }
    
    void set_level(LogLevel level) { level_ = level; }
    void set_file(const std::string& filepath) {
        std::lock_guard<std::mutex> lock(mutex_);
        if (file_.is_open()) file_.close();
        file_.open(filepath, std::ios::app);
    }
    
    void log(LogLevel level, const std::string& message,
             const std::string& file = "", int line = 0) {
        if (level < level_) return;
        
        std::lock_guard<std::mutex> lock(mutex_);
        
        auto now = std::chrono::system_clock::now();
        auto time = std::chrono::system_clock::to_time_t(now);
        
        std::ostringstream oss;
        oss << "[" << std::put_time(std::localtime(&time), "%Y-%m-%d %H:%M:%S") << "] "
            << "[" << level_to_string(level) << "] ";
        
        if (!file.empty()) {
            oss << file << ":" << line << " - ";
        }
        
        oss << message << "\n";
        
        std::string formatted = oss.str();
        
        if (file_.is_open()) {
            file_ << formatted;
            file_.flush();
        }
        
        if (level >= LogLevel::ERROR) {
            std::cerr << formatted;
        }
    }
    
    void debug(const std::string& msg, const std::string& file = "", int line = 0) {
        log(LogLevel::DEBUG, msg, file, line);
    }
    
    void info(const std::string& msg, const std::string& file = "", int line = 0) {
        log(LogLevel::INFO, msg, file, line);
    }
    
    void warning(const std::string& msg, const std::string& file = "", int line = 0) {
        log(LogLevel::WARNING, msg, file, line);
    }
    
    void error(const std::string& msg, const std::string& file = "", int line = 0) {
        log(LogLevel::ERROR, msg, file, line);
    }
    
    void fatal(const std::string& msg, const std::string& file = "", int line = 0) {
        log(LogLevel::FATAL, msg, file, line);
    }
    
private:
    Logger() : level_(LogLevel::INFO) {}
    ~Logger() { if (file_.is_open()) file_.close(); }
    
    Logger(const Logger&) = delete;
    Logger& operator=(const Logger&) = delete;
    
    std::string level_to_string(LogLevel level) {
        switch (level) {
            case LogLevel::DEBUG:   return "DEBUG";
            case LogLevel::INFO:    return "INFO ";
            case LogLevel::WARNING: return "WARN ";
            case LogLevel::ERROR:   return "ERROR";
            case LogLevel::FATAL:   return "FATAL";
            default: return "?????";
        }
    }
    
    LogLevel level_;
    std::ofstream file_;
    std::mutex mutex_;
};

// Convenience macros
#define LOG_DEBUG(msg) niskala::Logger::instance().debug(msg, __FILE__, __LINE__)
#define LOG_INFO(msg)  niskala::Logger::instance().info(msg, __FILE__, __LINE__)
#define LOG_WARN(msg)  niskala::Logger::instance().warning(msg, __FILE__, __LINE__)
#define LOG_ERROR(msg) niskala::Logger::instance().error(msg, __FILE__, __LINE__)
#define LOG_FATAL(msg) niskala::Logger::instance().fatal(msg, __FILE__, __LINE__)

} // namespace niskala
