cmake_minimum_required(VERSION 3.16)
project(aniplay LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Qt6 REQUIRED COMPONENTS Widgets OpenGL)

add_executable(aniplay
    src/main.cpp
    src/mpvwidget.cpp
    src/mpvwidget.h
)

target_link_libraries(aniplay PRIVATE
    Qt6::Widgets
    Qt6::OpenGL
    mpv
)

# Enable Qt moc, rcc, uic automatically
set_target_properties(aniplay PROPERTIES
    AUTOMOC ON
    AUTOUIC ON
    AUTORCC ON
)
