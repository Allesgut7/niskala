cmake_minimum_required(VERSION 3.20)
project(niskala LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTORCC ON)

find_package(Qt6 REQUIRED COMPONENTS Core Gui Widgets Network)

find_package(Qt6 COMPONENTS WebEngineWidgets QUIET)
if(Qt6WebEngineWidgets_FOUND)
    add_definitions(-DHAS_QTWEBENGINE)
    message(STATUS "Qt6 WebEngine found - Lightweight Charts enabled")
else()
    message(STATUS "Qt6 WebEngine not found - using QPainter chart fallback")
endif()

add_subdirectory(src/ui)
