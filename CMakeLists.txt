cmake_minimum_required(VERSION 3.10)
project(aniplay_backend)

set(CMAKE_CXX_STANDARD 17)

find_package(PkgConfig REQUIRED)
pkg_check_modules(MPV REQUIRED mpv)

add_library(aniplay SHARED src/aniplay.cpp)
target_include_directories(aniplay PRIVATE ${MPV_INCLUDE_DIRS})
target_link_libraries(aniplay ${MPV_LIBRARIES})
