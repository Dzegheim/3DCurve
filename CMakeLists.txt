cmake_minimum_required(VERSION 3.10)  # CMake version check
project(Curve)                        # Create project
set(CMAKE_CXX_STANDARD 17)            # Enable c++17 standard
set(CMAKE_CXX_COMPILER g++)           # Force g++
set(CMAKE_VERBOSE_MAKEFILE ON)        # Verbose

set(SOURCE_FILES  "Curve.cpp" 
	"Pipeline.cpp" 
	"ExploreDirectory.cpp"
	)

find_package(Boost 1.65 QUIET REQUIRED COMPONENTS system filesystem)
if(NOT Boost_FOUND)
    message(FATAL_ERROR "Boost Not found")
endif()

#Checking if jsoncons library is found, you may want to edit the path
#if you're not storing it in the same place as me
#To find the library go to https://github.com/danielaparker/jsoncons
if(NOT EXISTS "/usr/include/jsoncons/")
	message (FATAL_ERROR "Library jsoncons not found, please check the path if you're sure you have it, or download it at https://github.com/danielaparker/jsoncons")
endif()

add_executable("${PROJECT_NAME}" ${SOURCE_FILES})
target_link_libraries("${PROJECT_NAME}" boost_system boost_filesystem)

set(CMAKE_BUILD_TYPE Release)

set(CMAKE_CXX_FLAGS "-W -Wall -Wextra -Wpedantic -fdiagnostics-color=always")
set(CMAKE_CXX_FLAGS_DEBUG "-O0 -g")
set(CMAKE_CXX_FLAGS_RELEASE "-O3")
set(EXECUTABLE_OUTPUT_PATH ./)