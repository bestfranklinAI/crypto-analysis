cmake_minimum_required(VERSION 3.18)
project(MarketEngine VERSION 1.0 LANGUAGES CXX)

# C++17 standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Optimization flags
if(CMAKE_BUILD_TYPE STREQUAL "Release")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3 -march=native")
endif()

# Find Python
find_package(Python3 COMPONENTS Interpreter Development REQUIRED)

# Find pybind11 - Try multiple methods
find_package(pybind11 CONFIG QUIET)

if(NOT pybind11_FOUND)
    # Try using Python to find pybind11
    execute_process(
        COMMAND ${Python3_EXECUTABLE} -m pybind11 --cmakedir
        OUTPUT_VARIABLE PYBIND11_CMAKE_DIR
        OUTPUT_STRIP_TRAILING_WHITESPACE
        RESULT_VARIABLE PYBIND11_CMAKE_RESULT
    )
    
    if(PYBIND11_CMAKE_RESULT EQUAL 0)
        message(STATUS "Found pybind11 at: ${PYBIND11_CMAKE_DIR}")
        list(APPEND CMAKE_PREFIX_PATH ${PYBIND11_CMAKE_DIR})
        find_package(pybind11 CONFIG REQUIRED)
    else()
        message(FATAL_ERROR "pybind11 not found. Install with: pip install pybind11")
    endif()
endif()

# Include directories
include_directories(include)

# Source files
set(SOURCES
    src/vwap.cpp
    src/rsi.cpp
    src/bindings.cpp
)

# Create Python module
pybind11_add_module(market_engine ${SOURCES})

# Link libraries
target_include_directories(market_engine PRIVATE include)

# Installation
install(TARGETS market_engine DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}/../app)