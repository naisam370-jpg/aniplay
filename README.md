# Aniplay 🎥

A lightweight anime (or any video) player built in **C++** using **SDL2**, **OpenGL**, and **libmpv**.  
This project was originally started with Qt but was refactored to SDL2 for a simpler and more direct rendering pipeline.

---

## 🚀 Features
- Uses **libmpv** for playback (fast, reliable).
- **SDL2** for window and input handling.
- **OpenGL** for rendering video frames.
- Cross-platform (Linux, Windows, WSL2 with X11/Wayland).

---

## 📦 Dependencies

Install these before building:

### Debian / Ubuntu
```bash
sudo ./install_deps.sh
```
### Arch Linux
```bash
sudo pacman -S base-devel cmake sdl2 mpv mesa
```
### Fedora
```bash 
sudo dnf install @development-tools cmake SDL2-devel mpv-libs-devel mesa-libGL-devel
```

## Build Instructions
```bash
git clone https://github.com/yourname/aniplay.git
cd aniplay
mkdir build && cd build
cmake ..
make
```
## RUN
```bash
./aniplay '/path/to/video/file.mkv'
```
### Troubleshooting
cannot find ``` -lmpv ``` → Make sure ``` libmpv-dev ``` (Debian/Ubuntu) or `mpv-libs-devel` (Fedora) is installed.

undefined reference to `glClear` → Ensure `libgl1-mesa-dev` (or equivalent OpenGL dev package) is installed.

WSL users → You need X11/Wayland forwarding or a display server like **VcXsrv** for video output.

## License
This project is licensed under the **GNU General Public License v3.0 (GPLv3)**

see the LICENSE file for details