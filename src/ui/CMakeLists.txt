cmake_minimum_required(VERSION 3.20)
project(niskala-ui LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTORCC ON)

find_package(Qt6 REQUIRED COMPONENTS Core Gui Widgets Charts Network)

set(SOURCES
    main.cpp
    app/MainWindow.cpp
    ui/theme/ThemeManager.cpp
    ui/widgets/CommandBar.cpp
    ui/widgets/NavigationBar.cpp
    ui/widgets/BreakingNewsTicker.cpp
    ui/widgets/MarketIndexCard.cpp
    ui/widgets/MarketIndicesStrip.cpp
    ui/widgets/CommodityTable.cpp
    ui/widgets/MarketBreadthWidget.cpp
    ui/widgets/SectorPerformanceWidget.cpp
    ui/widgets/CandlestickChart.cpp
    ui/widgets/ChartToolbarWidget.cpp
    ui/widgets/OrderBookWidget.cpp
    ui/widgets/FearGreedGauge.cpp
    ui/widgets/SectorHeatmap.cpp
    ui/widgets/SentimentGauge.cpp
    ui/widgets/TopBannerWidget.cpp
    ui/widgets/RunningTradeTicker.cpp
    ui/widgets/BottomBanner.cpp
    ui/widgets/AIMarketRegimeWidget.cpp
    ui/widgets/ForeignFlowWidget.cpp
    ui/widgets/FooterWidget.cpp
    ui/screens/DashboardScreen.cpp
    ui/screens/ChartScreen.cpp
    ui/screens/ScreenerScreen.cpp
    ui/screens/SettingsScreen.cpp
    ui/screens/PortfolioScreen.cpp
    ui/screens/MarketOverviewScreen.cpp
    ui/screens/NewsScreen.cpp
    core/PythonBridge.cpp
    core/DataManager.cpp
)

set(HEADERS
    app/MainWindow.h
    ui/theme/ThemeManager.h
    ui/widgets/CommandBar.h
    ui/widgets/NavigationBar.h
    ui/widgets/BreakingNewsTicker.h
    ui/widgets/MarketIndexCard.h
    ui/widgets/MarketIndicesStrip.h
    ui/widgets/CommodityTable.h
    ui/widgets/MarketBreadthWidget.h
    ui/widgets/SectorPerformanceWidget.h
    ui/widgets/CandlestickChart.h
    ui/widgets/ChartToolbarWidget.h
    ui/widgets/OrderBookWidget.h
    ui/widgets/FearGreedGauge.h
    ui/widgets/SectorHeatmap.h
    ui/widgets/SentimentGauge.h
    ui/widgets/TopBannerWidget.h
    ui/widgets/RunningTradeTicker.h
    ui/widgets/BottomBanner.h
    ui/widgets/AIMarketRegimeWidget.h
    ui/widgets/ForeignFlowWidget.h
    ui/widgets/FooterWidget.h
    ui/screens/DashboardScreen.h
    ui/screens/ChartScreen.h
    ui/screens/ScreenerScreen.h
    ui/screens/SettingsScreen.h
    ui/screens/PortfolioScreen.h
    ui/screens/MarketOverviewScreen.h
    ui/screens/NewsScreen.h
    core/PythonBridge.h
    core/DataManager.h
)

set(RESOURCES
    resources/resources.qrc
)

add_executable(niskala-ui ${SOURCES} ${HEADERS} ${RESOURCES})

target_include_directories(niskala-ui PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/app
    ${CMAKE_CURRENT_SOURCE_DIR}/ui
    ${CMAKE_CURRENT_SOURCE_DIR}/core
)

target_link_libraries(niskala-ui PRIVATE
    Qt6::Core
    Qt6::Gui
    Qt6::Widgets
    Qt6::Charts
    Qt6::Network
)

set_target_properties(niskala-ui PROPERTIES
    OUTPUT_NAME "niskala"
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin"
)
