cmake_minimum_required (VERSION 2.8.12)
project (CPlantBox)

# set compiler options
set(RELEASE_OPTS "-std=c++17 -fno-strict-aliasing -fstrict-overflow -fno-finite-math-only -O3 -march=native -funroll-loops -g0 ")
set(CMAKE_CXX_FLAGS_RELEASE "${RELEASE_WARNING_OPTS} ${RELEASE_OPTS}")
set(CMAKE_CXX_FLAGS_DEBUG "-std=c++17 -O0 -ggdb -Wall")

# set default build type to release Release
set(CMAKE_BUILD_TYPE Release)

# add source directory to the include path
include_directories(${PROJECT_SOURCE_DIR}/src/structural)
include_directories(${PROJECT_SOURCE_DIR}/src/functional)
include_directories(${PROJECT_SOURCE_DIR}/src/visualisation)
include_directories(${PROJECT_SOURCE_DIR}/src/external/)

# add subdirectories
add_subdirectory(src)
add_subdirectory(debug_test)
#add_subdirectory(tutorial)

# build tutorial (TODO)
# INCLUDE(UseLATEX.cmake)
