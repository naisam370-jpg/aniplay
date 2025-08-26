cmake_minimum_required(VERSION 3.16)
project(aniplay VERSION 0.1 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find OpenGL
find_package(OpenGL REQUIRED)

# Find GLFW
find_package(PkgConfig REQUIRED)
pkg_check_modules(GLFW REQUIRED glfw3)

# Find mpv
pkg_check_modules(MPV REQUIRED mpv)

# Add include directories
include_directories(
    ${GLFW_INCLUDE_DIRS}
    ${MPV_INCLUDE_DIRS}
)

# Collect sources
set(SOURCES
    src/main.cpp
)

# Create executable
add_executable(${PROJECT_NAME} ${SOURCES})

# Link against OpenGL, GLFW, and mpv
target_link_libraries(${PROJECT_NAME}
    OpenGL::GL
    ${GLFW_LIBRARIES}
    ${MPV_LIBRARIES}
)

# Install target
install(TARGETS ${PROJECT_NAME} DESTINATION bin)

# License notice
message(STATUS "aniplay is licensed under the GNU GPL v3")
