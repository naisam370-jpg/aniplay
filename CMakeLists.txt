cmake_minimum_required(VERSION 3.16)
project(AniPlay LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_AUTOUIC ON)

find_package(Qt6 COMPONENTS Widgets OpenGL REQUIRED)

add_executable(aniplay
    src/main.cpp
    src/mainwindow.cpp
    src/mainwindow.h
    src/mpvwidget.cpp
    src/mpvwidget.h
)

target_link_libraries(aniplay
    Qt6::Widgets
    Qt6::OpenGL
    mpv
)
