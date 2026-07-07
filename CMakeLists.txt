cmake_minimum_required(VERSION 3.20)
project(niskala VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

include(FetchContent)
set(FETCHCONTENT_QUIET OFF)

# FTXUI v7.0.0
FetchContent_Declare(ftxui
    GIT_REPOSITORY https://github.com/ArthurSonzogni/ftxui
    GIT_TAG v7.0.0
    GIT_SHALLOW TRUE
)

# nlohmann/json
FetchContent_Declare(json
    GIT_REPOSITORY https://github.com/nlohmann/json
    GIT_TAG v3.11.3
    GIT_SHALLOW TRUE
)

# cpp-httplib
FetchContent_Declare(httplib
    GIT_REPOSITORY https://github.com/yhirose/cpp-httplib
    GIT_TAG v0.15.3
    GIT_SHALLOW TRUE
)

# pybind11
find_package(pybind11 QUIET)
if(NOT pybind11_FOUND)
    # Try common locations
    foreach(_pyver "3.11" "3.10" "3.12")
        set(_pybind11_dir "$ENV{HOME}/.local/lib/python${_pyver}/site-packages/pybind11/share/cmake/pybind11")
        if(EXISTS "${_pybind11_dir}")
            set(pybind11_DIR "${_pybind11_dir}")
            break()
        endif()
    endforeach()
    find_package(pybind11 REQUIRED)
endif()

# SQLite3
find_package(SQLite3 REQUIRED)

FetchContent_MakeAvailable(ftxui json httplib)

# Main executable
add_executable(niskala
    src/main.cpp
    # Core - Common
    src/core/common/config.cpp
    # Core - Market Data
    src/core/market_data/data_aggregator.cpp
    src/core/market_data/yfinance_provider.cpp
    src/core/market_data/akshare_provider.cpp
    src/core/market_data/cache_manager.cpp
    src/core/market_data/sentiment_provider.cpp
    # Core - AI
    src/core/ai/sentiment_analyzer.cpp
    src/core/ai/news_scraper.cpp
    src/core/ai/llm_client.cpp
    src/core/ai/impact_mapper.cpp
    # Core - Fear & Greed
    src/core/fear_greed/calculator.cpp
    src/core/fear_greed/multi_region.cpp
    # Core - Quant (Phase 2 stubs)
    src/core/quant/backtest_engine.cpp
    src/core/quant/factor_analyzer.cpp
    src/core/quant/portfolio_optimizer.cpp
    src/core/quant/risk_metrics.cpp
    src/core/quant/signal_generator.cpp
    # TUI
    src/tui/app.cpp
    # TUI - Screens
    src/tui/screens/dashboard_screen.cpp
    src/tui/screens/market_screen.cpp
    src/tui/screens/chart_screen.cpp
    src/tui/screens/news_screen.cpp
    src/tui/screens/screener_screen.cpp
    src/tui/screens/portfolio_screen.cpp
    src/tui/screens/settings_screen.cpp
    # TUI - Widgets
    src/tui/widgets/top_banner.cpp
    src/tui/widgets/bottom_banner.cpp
    src/tui/widgets/running_trade_ticker.cpp
    src/tui/widgets/stock_table.cpp
    src/tui/widgets/chart_widget.cpp
    src/tui/widgets/order_book.cpp
    src/tui/widgets/news_feed.cpp
    src/tui/widgets/news_feed_sentiment.cpp
    src/tui/widgets/fear_greed_gauge.cpp
    src/tui/widgets/sentiment_gauge.cpp
    src/tui/widgets/sector_heatmap.cpp
    src/tui/widgets/ai_report_panel.cpp
)

target_link_libraries(niskala PRIVATE
    ftxui::screen
    ftxui::dom
    ftxui::component
    nlohmann_json::nlohmann_json
    httplib::httplib
    pybind11::embed
    SQLite::SQLite3
)

target_include_directories(niskala PRIVATE
    ${CMAKE_SOURCE_DIR}/src
)

# Create data directories
file(MAKE_DIRECTORY ${CMAKE_SOURCE_DIR}/data/cache)
file(MAKE_DIRECTORY ${CMAKE_SOURCE_DIR}/data/local_db)

# Install
install(TARGETS niskala DESTINATION bin)
