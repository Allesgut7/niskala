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
    ui/widgets/CandlestickChart.cpp
    ui/widgets/OrderBookWidget.cpp
    ui/widgets/FearGreedGauge.cpp
    ui/widgets/SectorHeatmap.cpp
    ui/widgets/SentimentGauge.cpp
    ui/widgets/TopBannerWidget.cpp
    ui/screens/DashboardScreen.cpp
)

set(HEADERS
    app/MainWindow.h
    ui/theme/ThemeManager.h
    ui/widgets/CommandBar.h
    ui/widgets/CandlestickChart.h
    ui/widgets/OrderBookWidget.h
    ui/widgets/FearGreedGauge.h
    ui/widgets/SectorHeatmap.h
    ui/widgets/SentimentGauge.h
    ui/widgets/TopBannerWidget.h
    ui/screens/DashboardScreen.h
)

set(RESOURCES
    resources/resources.qrc
)

add_executable(niskala-ui ${SOURCES} ${HEADERS} ${RESOURCES})

target_include_directories(niskala-ui PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/app
    ${CMAKE_CURRENT_SOURCE_DIR}/ui
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
