#
# 1. Make CPlantBox library
#

file(GLOB CPLANTSOURCE ./*.cpp)
file(GLOB CPLANTHEAD ./*.h)

add_library(tinyxml2
    "${PROJECT_SOURCE_DIR}/src/external/tinyxml2/tinyxml2.h"
    "${PROJECT_SOURCE_DIR}/src/external/tinyxml2/tinyxml2.cpp"
)
add_library(AABBCC
    "${PROJECT_SOURCE_DIR}/src/external/aabbcc/aabb.h"
    "${PROJECT_SOURCE_DIR}/src/external/aabbcc/aabb.cc"
)
add_library(gauss_legendre
    "${PROJECT_SOURCE_DIR}/src/external/gauss_legendre/gauss_legendre.h"
    "${PROJECT_SOURCE_DIR}/src/external/gauss_legendre/gauss_legendre.cpp"
)


set_target_properties(tinyxml2 PROPERTIES LIBRARY_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/)
set_target_properties(AABBCC PROPERTIES LIBRARY_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/)
set_target_properties(gauss_legendre PROPERTIES LIBRARY_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/)

add_library(CPlantBox SHARED                        
            ${CPLANTSOURCE}
            ${CPLANTHEAD}
			)

set_target_properties(CPlantBox PROPERTIES LIBRARY_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/)

#
# 2. Make CPlantBox Pyhthon binding
#
set(PYBIND11_PYTHON_VERSION 3.7)
find_package( PythonInterp 3.7 REQUIRED )
find_package( PythonLibs 3.7 REQUIRED )
find_package(pybind11 REQUIRED) 

message(Info " Adding ${PROJECT_SOURCE_DIR}/src/external/pybind11/include to list of dirs")

target_include_directories(CPlantBox
  PUBLIC "${PROJECT_SOURCE_DIR}/src/external/pybind11/include"
  PUBLIC ${PYTHON_INCLUDE_DIRS}
)

#add_subdirectory(external/pybind11)
pybind11_add_module(plantbox SHARED 
            ${CPLANTSOURCE})

target_include_directories(plantbox
  PUBLIC "${PROJECT_SOURCE_DIR}/src/external/pybind11/include"
  PUBLIC ${PYTHON_INCLUDE_DIRS}
)


target_link_libraries(plantbox LINK_PUBLIC ${PYTHON_LIBRARIES} tinyxml2 AABBCC gauss_legendre)
target_link_libraries(CPlantBox LINK_PUBLIC ${PYTHON_LIBRARIES} tinyxml2 AABBCC gauss_legendre)
			
set_target_properties(plantbox PROPERTIES LIBRARY_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/)
