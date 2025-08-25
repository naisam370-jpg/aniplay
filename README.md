# Aniplay

Aniplay is a simple media player built with **C++**, **Qt6**, and **libmpv**.  
It uses `QOpenGLWidget` for rendering and integrates with the `libmpv` API for smooth video playback.

---

## Requirements

### System Packages (Debian / Ubuntu)
Make sure your system is up to date:

```bash
sudo apt update && sudo apt upgrade

Install the required development libraries:

sudo apt install \
    build-essential \
    cmake \
    pkg-config \
    qt6-base-dev \
    qt6-base-dev-tools \
    qt6-openglwidgets-dev \
    libmpv-dev

Optional (for runtime testing)

sudo apt install mpv

Building

Clone the repository and build:

git clone https://github.com/yourusername/aniplay.git
cd aniplay
mkdir build && cd build
cmake ..
make -j$(nproc)

The resulting executable will be in ./build/aniplay.
Running

From the build directory:

./aniplay

Notes

    QOpenGLWidget requires the qt6-openglwidgets-dev package (not included in qt6-base-dev).

    If you see errors like fatal error: QOpenGLWidget: No such file or directory, install qt6-openglwidgets-dev.

    If you see OSError: Cannot find libmpv, ensure libmpv-dev is installed.