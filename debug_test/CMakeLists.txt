
# Projectname: ${projectname}
# PROJECTNAME: ${PROJECTNAME_UPPER}
# path: ${librarypath}

get_filename_component(Folder ${CMAKE_CURRENT_LIST_DIR} NAME)
string(REPLACE " " "_" Folder ${Folder})

message("This is ${Folder}")

file(GLOB TESTSOURCES ./*.cpp)
file(GLOB TESTHEADERS ./*.h)


add_executable(${Folder}
  ${TESTSOURCES}
  ${TESTHEADERS}
)

target_include_directories(${Folder}
  PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}
  PUBLIC ${CMAKE_CURRENT_BINARY_DIR}
  PUBLIC ${CMAKE_SOURCE_DIR}/src
  PUBLIC ${CMAKE_SOURCE_DIR}/src/external
  PUBLIC ${CMAKE_SOURCE_DIR}/src/visualisation
)
message(${CMAKE_BINARY_DIR}/src/${CMAKE_BUILD_TYPE}/)
target_link_directories(${Folder} PUBLIC ${CMAKE_BINARY_DIR}/src/${CMAKE_BUILD_TYPE}/
  PUBLIC ${CMAKE_BINARY_DIR}/debug_test/external/${CMAKE_BUILD_TYPE}/
)
set(RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})
target_link_libraries(${Folder} PUBLIC CPlantBox)

if(NOT UNIX)
# array of possible build types
list( APPEND CMAKE_CONFIGURATION_TYPES Debug Release )
# copy dlls to build directory for each build type
foreach( OUTPUTCONFIG ${CMAKE_CONFIGURATION_TYPES} )
    add_custom_command(TARGET ${Folder} PRE_LINK
      COMMAND ${CMAKE_COMMAND} -E copy_if_different "${CMAKE_BINARY_DIR}/src/${OUTPUTCONFIG}/CPlantBox.dll" "${CMAKE_BINARY_DIR}/debug_test/external/${OUTPUTCONFIG}/CPlantBox.dll"
    )
endforeach( OUTPUTCONFIG CMAKE_CONFIGURATION_TYPES )
endif()
