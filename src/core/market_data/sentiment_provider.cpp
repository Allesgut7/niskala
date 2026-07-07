// Niskala - Sentiment Provider Implementation
// Version: 1.0.1 (Fixed pybind11 type handling)

#include "core/market_data/sentiment_provider.h"
#include "core/common/logger.h"
#include "core/common/types.h"
#include <pybind11/embed.h>
#include <pybind11/stl.h>
#include <filesystem>

namespace niskala {

SentimentProvider::SentimentProvider() : py_client_(nullptr) {
    try {
        init_python();
    } catch (const std::exception& e) {
        LOG_ERROR("Sentiment provider init failed: " + std::string(e.what()));
        py_client_ = nullptr;
    }
}

SentimentProvider::~SentimentProvider() {
    if (py_client_) {
        try {
            delete static_cast<pybind11::object*>(py_client_);
        } catch (...) {}
        py_client_ = nullptr;
    }
}

void SentimentProvider::init_python() {
    try {
        if (!Py_IsInitialized()) {
            LOG_WARN("Python interpreter not initialized, skipping Sentiment setup");
            return;
        }
        
        pybind11::module_ sys = pybind11::module_::import("sys");
        pybind11::list path = sys.attr("path");
        
        std::string python_path = std::filesystem::absolute("python").string();
        
        bool path_exists = false;
        for (auto item : path) {
            std::string item_str = pybind11::str(item);
            if (item_str == python_path || item_str == "python") {
                path_exists = true;
                break;
            }
        }
        
        if (!path_exists) {
            path.insert(0, python_path);
        }
        
        pybind11::module_ data_sources = pybind11::module_::import("data_sources");
        pybind11::object client_class = data_sources.attr("SentimentClient");
        
        py_client_ = new pybind11::object(client_class(false));
        
        LOG_INFO("Sentiment provider initialized");
        
    } catch (const pybind11::error_already_set& e) {
        LOG_ERROR("Python error in Sentiment init: " + std::string(e.what()));
        py_client_ = nullptr;
    } catch (const std::exception& e) {
        LOG_ERROR("Failed to initialize Sentiment provider: " + std::string(e.what()));
        py_client_ = nullptr;
    }
}

std::vector<NewsArticle> SentimentProvider::fetch_news(int limit) {
    std::vector<NewsArticle> results;
    
    if (!py_client_) {
        // Return mock data when model not available
        LOG_WARN("Sentiment provider not available, using mock data");
        NewsArticle mock1;
        mock1.source = "CNBC";
        mock1.title = "BBRI naik 3% setelah laporan keuangan Q2";
        mock1.summary = "Bank Rakyat Indonesia melaporkan laba bersih naik 15%";
        mock1.sentiment_score = 45;
        mock1.sentiment_label = "POSITIVE";
        mock1.tickers = {"BBRI"};
        mock1.sectors = {"FINANCE"};
        results.push_back(mock1);
        
        NewsArticle mock2;
        mock2.source = "IDX";
        mock2.title = "Mining stocks rally on commodity prices";
        mock2.summary = "Saham pertambangan menguat seiring naiknya harga komoditas";
        mock2.sentiment_score = 30;
        mock2.sentiment_label = "POSITIVE";
        mock2.tickers = {"ADRO", "PTBA"};
        mock2.sectors = {"BASIC", "ENERGY"};
        results.push_back(mock2);
        
        NewsArticle mock3;
        mock3.source = "Kontan";
        mock3.title = "TLKM target price raised to 4,200";
        mock3.summary = "Analyst menaikkan target harga Telkom Indonesia";
        mock3.sentiment_score = 60;
        mock3.sentiment_label = "POSITIVE";
        mock3.tickers = {"TLKM"};
        mock3.sectors = {"INFRA"};
        results.push_back(mock3);
        
        NewsArticle mock4;
        mock4.source = "BI";
        mock4.title = "BI Rate tetap 6.25%";
        mock4.summary = "Bank Indonesia mempertahankan suku bunga acuan";
        mock4.sentiment_score = 0;
        mock4.sentiment_label = "NEUTRAL";
        mock4.tickers = {};
        mock4.sectors = {"FINANCE"};
        results.push_back(mock4);
        
        NewsArticle mock5;
        mock5.source = "Reuters";
        mock5.title = "GOTO merosot 5% setelah pengumuman PHK";
        mock5.summary = "Gojek Tokopedia memangkas 1000 karyawan";
        mock5.sentiment_score = -50;
        mock5.sentiment_label = "NEGATIVE";
        mock5.tickers = {"GOTO"};
        mock5.sectors = {"TECH"};
        results.push_back(mock5);
        
        return results;
    }
    
    try {
        pybind11::object* client = static_cast<pybind11::object*>(py_client_);
        pybind11::object fetch_method = client->attr("fetch_news");
        pybind11::list articles = fetch_method(limit);
        
        for (auto article_obj : articles) {
            pybind11::dict article = article_obj.cast<pybind11::dict>();
            
            NewsArticle news;
            news.source = article["source"].cast<std::string>();
            news.title = article["title"].cast<std::string>();
            news.summary = article["summary"].cast<std::string>();
            news.sentiment_score = article["sentiment_score"].cast<int>();
            news.sentiment_label = article["sentiment_label"].cast<std::string>();
            news.tickers = article["tickers"].cast<std::vector<std::string>>();
            news.sectors = article["sectors"].cast<std::vector<std::string>>();
            
            results.push_back(news);
        }
        
        LOG_INFO("Fetched " + std::to_string(results.size()) + " news articles");
        
    } catch (const pybind11::error_already_set& e) {
        LOG_ERROR("Python error fetching news: " + std::string(e.what()));
    } catch (const std::exception& e) {
        LOG_ERROR("Error fetching news: " + std::string(e.what()));
    }
    
    return results;
}

std::vector<NewsArticle> SentimentProvider::get_cached_news() {
    std::vector<NewsArticle> results;
    
    if (!py_client_) {
        return results;
    }
    
    try {
        pybind11::object* client = static_cast<pybind11::object*>(py_client_);
        pybind11::object get_method = client->attr("get_cached_news");
        pybind11::list articles = get_method();
        
        for (auto article_obj : articles) {
            pybind11::dict article = article_obj.cast<pybind11::dict>();
            
            NewsArticle news;
            news.source = article["source"].cast<std::string>();
            news.title = article["title"].cast<std::string>();
            news.summary = article["summary"].cast<std::string>();
            news.sentiment_score = article["sentiment_score"].cast<int>();
            news.sentiment_label = article["sentiment_label"].cast<std::string>();
            news.tickers = article["tickers"].cast<std::vector<std::string>>();
            news.sectors = article["sectors"].cast<std::vector<std::string>>();
            
            results.push_back(news);
        }
        
    } catch (const pybind11::error_already_set& e) {
        LOG_ERROR("Python error getting cached news: " + std::string(e.what()));
    } catch (const std::exception& e) {
        LOG_ERROR("Error getting cached news: " + std::string(e.what()));
    }
    
    return results;
}

} // namespace niskala
