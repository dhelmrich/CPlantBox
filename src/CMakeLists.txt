#
# 1. Make CPlantBox library
#

file(GLOB CPLANTSOURCE ./*.cpp)
file(GLOB CPLANTHEAD ./*.h)

add_library(CPlantBox SHARED                        
            ${CPLANTSOURCE}
            ${CPLANTHEAD}
			)

set_target_properties(CPlantBox PROPERTIES LIBRARY_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/)

#
# 2. Make CPlantBox Pyhthon binding
#
# find_package(pybind11 REQUIRED) 
set(PYBIND11_PYTHON_VERSION 3.7)
find_package( PythonInterp 3.7 REQUIRED )
find_package( PythonLibs 3.7 REQUIRED )
add_subdirectory(external/pybind11)
pybind11_add_module(plantbox SHARED 
            ${CPLANTSOURCE})
			
set_target_properties(plantbox PROPERTIES LIBRARY_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/)
