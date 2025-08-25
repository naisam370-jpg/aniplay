cmake_minimum_required(VERSION 3.16)
project(aniplay LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find dependencies
find_package(PkgConfig REQUIRED)
find_package(OpenGL REQUIRED)

pkg_check_modules(SDL2 REQUIRED sdl2)
pkg_check_modules(MPV REQUIRED mpv)

include_directories(
    ${SDL2_INCLUDE_DIRS}
    ${MPV_INCLUDE_DIRS}
)

add_executable(aniplay
    src/main.cpp
)

target_link_libraries(aniplay
    ${SDL2_LIBRARIES}
    ${MPV_LIBRARIES}
    OpenGL::GL
)
