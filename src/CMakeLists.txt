#
# 1. Make CPlantBox library
#

include(GenerateExportHeader)

include_directories(structural)
include_directories(functional)
include_directories(visualisation)

find_package (Eigen3 3.3 REQUIRED NO_MODULE)

if(UNIX)
  find_package(PkgConfig)
  if (PKG_CONFIG_FOUND)
    pkg_check_modules(TINYXML2 REQUIRED IMPORTED_TARGET tinyxml2)
    set(TINYXML2_INCLUDE_DIR PkgConfig::TINYXML2_INCLUDE_DIRS)
    set(TINYXML2_LIBRARY PkgConfig::TINYXML2)
  else()
    message(FATAL_ERROR "pkg-config not found, please install it")
  endif()
else()
  find_package(tinyxml2 CONFIG REQUIRED)
  set(TINYXML2_INCLUDE_DIR ${TINYXML2_INCLUDE_DIRS})
  set(TINYXML2_LIBRARY ${tinyxml2_shared_targets})
  include(${tinyxml2_shared_targets})
endif()

include_directories(external/)
#include_directories(external/tinyxml2/)
#set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)


message(STATUS "TinyXML2_LIBRARIES: ${TINYXML2_LIBRARY}")
message(STATUS "TinyXML2_INCLUDE_DIRS: ${TINYXML2_INCLUDE_DIR}")
message(STATUS "tinyxml2_shared_targets" ${tinyxml2_shared_targets})


add_library(CPlantBox SHARED
    structural/organparameter.cpp
    structural/rootparameter.cpp
		structural/seedparameter.cpp
		structural/leafparameter.cpp
		structural/stemparameter.cpp
    structural/Organ.cpp
    structural/Root.cpp
    structural/RootDelay.cpp            
    structural/Seed.cpp
		structural/Stem.cpp
		structural/Leaf.cpp
		structural/Plant.cpp
    structural/Organism.cpp
    structural/Plant.cpp            
    structural/RootSystem.cpp
    structural/MappedOrganism.cpp
    structural/sdf.cpp
    structural/SegmentAnalyser.cpp            
    structural/tropism.cpp
    structural/organparameter.h
    structural/rootparameter.h
		structural/seedparameter.h
		structural/leafparameter.h
		structural/stemparameter.h
    structural/Organ.h
    structural/Root.h
    structural/RootDelay.h            
    structural/Seed.h
		structural/Stem.h
		structural/Leaf.h
		structural/Plant.h
    structural/Organism.h
    structural/Plant.h            
    structural/RootSystem.h
    structural/MappedOrganism.h
    structural/sdf.h
    structural/SegmentAnalyser.h            
    structural/tropism.h    
    functional/XylemFlux.cpp
		functional/Photosynthesis.cpp
		functional/Perirhizal.cpp
		visualisation/Quaternion.h
		visualisation/CatmullRomSpline.h
		visualisation/PlantVisualiser.h
		visualisation/PlantVisualiser.cpp
		external/aabbcc/AABB.cc
    external/gauss_legendre/gauss_legendre.cpp       
)

target_link_libraries(CPlantBox 
  PRIVATE tinyxml2::tinyxml2
  PRIVATE  Eigen3::Eigen
						)

set_target_properties(CPlantBox PROPERTIES LIBRARY_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/)

target_include_directories(
                        CPlantBox
  PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}
  PUBLIC ${CMAKE_CURRENT_BINARY_DIR}
  PUBLIC ${CMAKE_SOURCE_DIR}/src
  PUBLIC ${CMAKE_SOURCE_DIR}/src/external
  PUBLIC ${CMAKE_SOURCE_DIR}/src/visualisation
  PRIVATE ${TINYXML2_INCLUDE_DIR}
  PRIVATE ${EIGEN3_INCLUDE_DIR}
  
)
#set_target_properties(CPlantBox PROPERTIES INSTALL_RPATH_USE_LINK_PATH TRUE)

export(TARGETS CPlantBox FILE CPlantBoxConfig.cmake)
export(PACKAGE CPlantBox)

if(UNIX)
install(TARGETS CPlantBox
        EXPORT CPlantBoxConfig
        LIBRARY DESTINATION ${CMAKE_CURRENT_BINARY_DIR}
        ARCHIVE DESTINATION ${CMAKE_CURRENT_BINARY_DIR}
        RUNTIME DESTINATION ${CMAKE_CURRENT_BINARY_DIR}
        INCLUDES DESTINATION ${CMAKE_SOURCE_DIR}/src
        INCLUDES DESTINATION ${CMAKE_SOURCE_DIR}/src/external
        INCLUDES DESTINATION ${CMAKE_SOURCE_DIR}/src/visualisation
        INCLUDES DESTINATION ${CMAKE_SOURCE_DIR}/src/structural
        )
else()
install(TARGETS CPlantBox
        EXPORT CPlantBoxConfig
        LIBRARY DESTINATION ${CMAKE_CURRENT_BINARY_DIR}/src/${CMAKE_BUILD_TYPE}
        RUNTIME DESTINATION ${CMAKE_CURRENT_BINARY_DIR}/src/${CMAKE_BUILD_TYPE}
        INCLUDES DESTINATION ${CMAKE_SOURCE_DIR}/src
        INCLUDES DESTINATION ${CMAKE_SOURCE_DIR}/src/external
        INCLUDES DESTINATION ${CMAKE_SOURCE_DIR}/src/visualisation
        INCLUDES DESTINATION ${CMAKE_SOURCE_DIR}/src/structural
        )
endif()

#
# 2. Make CPlantBox Pyhthon binding
#
if(UNIX)

	# find_package(pybind11 REQUIRED) 
	#set(PYBIND11_PYTHON_VERSION 3.7)
	find_package( PythonInterp 3.7 REQUIRED )
	find_package( PythonLibs 3.7 REQUIRED )
	add_subdirectory(external/pybind11)

	pybind11_add_module(plantbox SHARED 
				PyPlantBox.cpp   								
				)
	set_target_properties(plantbox PROPERTIES CMAKE_CPP_IMPLICIT_LINK_DIRECTORIES ${PROJECT_BINARY_DIR}/)
	# make sure that the python module can find the other one through the search paths
	set_target_properties(plantbox PROPERTIES INSTALL_RPATH_USE_LINK_PATH TRUE)
	# set Cplantbox to also build 
	# add search path for the library to the python module
	target_link_libraries(plantbox PRIVATE 
				CPlantBox)
target_include_directories(
                        plantbox
  PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}
  PUBLIC ${CMAKE_CURRENT_BINARY_DIR}
  PUBLIC ${CMAKE_SOURCE_DIR}/src
  PUBLIC ${CMAKE_SOURCE_DIR}/src/external
  PUBLIC ${CMAKE_SOURCE_DIR}/src/visualisation
)
			
	set_target_properties(plantbox PROPERTIES LIBRARY_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/) 

endif()



generate_export_header(CPlantBox
  EXPORT_FILE_NAME ${CMAKE_CURRENT_BINARY_DIR}/CPlantBox/export.hpp
)




