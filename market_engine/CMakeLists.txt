cmake_minimum_required(VERSION 3.18)
project(market_engine)

# Set C++17 standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Find Python and pybind11
find_package(Python COMPONENTS Interpreter Development REQUIRED)
find_package(pybind11 CONFIG REQUIRED)

# Compiler flags for optimization and warnings
if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    add_compile_options(-Wall -Wextra -Wpedantic -O3 -march=native)
elseif(MSVC)
    add_compile_options(/W4 /O2)
endif()

# Source files
set(SOURCES
    indicators.cpp
    bindings.cpp
)

# Create Python module
pybind11_add_module(market_engine ${SOURCES})

# Include directories
target_include_directories(market_engine PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

# Link libraries (add any additional libraries here if needed)
# target_link_libraries(market_engine PRIVATE somelib)

# Installation
install(TARGETS market_engine LIBRARY DESTINATION .)
