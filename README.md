# AniPlay(PROTOTYPE)

AniPlay is an experimental anime/video library manager and player.  
It uses a **C++ backend** (libmpv) for media playback and a **Python (PySide6)** frontend for the GUI.  

---

## 📂 Project Structure
```sh

aniplay/
├── backend/
│ ├── CMakeLists.txt # Build rules for backend
│ ├── src/ # C++ source files (mpv wrapper, core logic)
│ └── include/ # C++ headers
├── gui.py # Python GUI (PySide6, communicates with backend)
├── install_deps.sh # Dependency installation script
└── README.md # Project documentation
```

---

## Requirements

- Debian 12 / Ubuntu 22.04 (or similar Linux)
- CMake ≥ 3.16
- GCC ≥ 10
- Python 3.9+
- `libmpv` development libraries
- Qt6 (via PySide6)

---

## Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/naisam370-jpg/aniplay.git
cd aniplay
chmod +x install_deps.sh
./install_deps.sh
```
## Build Backend
```bash
mkdir -p build
cd build
cmake ..
make
```
This produces a shared library that the GUI can call into.
## Run GUI
From the project root
```bash
python3 gui.py
```
## license 
GPLv3 