#!/bin/bash
set -e

echo "[*] Updating package list..."
sudo apt update

echo "[*] Installing build tools..."
sudo apt install -y build-essential cmake pkg-config git

echo "[*] Installing MPV development libraries..."
sudo apt install -y libmpv-dev

echo "[*] Installing Qt6 (for PySide6 GUI)..."
sudo apt install -y qt6-base-dev

echo "[*] Installing Python + PySide6..."
sudo apt install -y python3 python3-pip
pip3 install --upgrade pip
pip3 install PySide6

echo "[*] All dependencies installed successfully!"
echo "Now you can build the backend:"
echo "  mkdir -p build && cd build && cmake .. && make"
echo
echo "Then run the GUI with:"
echo "  python3 gui.py"
