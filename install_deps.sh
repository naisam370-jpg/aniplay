#!/usr/bin/env bash
set -e

echo ">>> Updating package index..."
sudo apt update

echo ">>> Installing build tools..."
sudo apt install -y build-essential cmake pkg-config git

echo ">>> Installing libraries (OpenGL, GLFW, mpv)..."
sudo apt install -y \
    libglfw3-dev \
    libmpv-dev \
    libglu1-mesa-dev \
    libx11-dev

echo ">>> All dependencies installed successfully!"
echo ">>> You can now proceed with building the project."