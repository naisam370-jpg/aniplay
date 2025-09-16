# AniPlay

A modern, feature-rich anime library manager and player for Linux.

![AniPlay Screenshot](docs/screenshot.png)

## Features

### 🎯 Core Features
- **Smart Library Management** - Automatically scan and organize your anime collection
- **Episode Progress Tracking** - Never lose track of where you left off
- **Search & Filtering** - Quickly find any anime in your library
- **Favorites System** - Mark and easily access your favorite series
- **Recently Watched** - Quick access to recently viewed anime
- **Custom Metadata** - Fetch anime information from online databases

### 🎨 User Interface
- **Modern Design** - Clean, Netflix-inspired interface
- **Dark/Light Themes** - Choose your preferred appearance
- **Grid/List Views** - Multiple ways to browse your library
- **Keyboard Navigation** - Full keyboard support for power users
- **Responsive Layout** - Adapts to different screen sizes

### 🎥 Playback Features
- **Multiple Player Support** - Works with mpv, VLC, and other players
- **Resume Playback** - Continue from where you stopped
- **Auto-play Next** - Seamlessly watch series episodes
- **Progress Tracking** - Visual indicators for watched/unwatched episodes
- **Thumbnail Generation** - Beautiful episode previews

### 🔧 Advanced Features
- **Database Backend** - SQLite database for fast, reliable storage
- **Metadata Fetching** - Automatic anime information retrieval
- **Thumbnail Caching** - Fast loading with smart caching
- **Background Scanning** - Non-blocking library updates
- **Export/Import** - Backup and restore your library data

## Installation

### Prerequisites

```bash
# Ubuntu/Debian
sudo apt install python3 python3-pip ffmpeg mpv cmake build-essential

# Arch Linux
sudo pacman -S python python-pip ffmpeg mpv cmake base-devel

# Fedora
sudo dnf install python3 python3-pip ffmpeg mpv cmake gcc-c++
```

### Quick Install

1. **Clone the repository:**
   ```bash
   git clone https://github.com/naisam370-jpg/aniplay.git
   cd aniplay
   ```

2. **Run the installer:**
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

3. **Start AniPlay:**
   ```bash
   aniplay
   ```

### Manual Installation

```bash
# Install Python dependencies
pip3 install --user -r requirements.txt

# Build C++ backend (optional but recommended)
mkdir -p build && cd build
cmake ../src/backend && make && cd ..

# Run directly
python3 src/aniplay/main.py
```

## Usage

### First Time Setup

1. **Launch AniPlay** - The application will create necessary directories
2. **Configure Library Path** - Go to Settings → Library to set your anime folder
3. **Scan Library** - Click the refresh button or use Ctrl+R to scan for anime
4. **Enjoy!** - Browse your collection and start watching

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+F` | Focus search bar |
| `F5` | Refresh library |
| `F11` | Toggle fullscreen |
| `Esc` | Go back/Exit fullscreen |
| `Enter` | Open selected anime/Play episode |
| `Space` | Play/Pause (when available) |
| `←→↑↓` | Navigate grid |

### Command Line Usage

```bash
# Basic usage
aniplay

# Custom library path
aniplay --library ~/MyAnime

# Scan only (no GUI)
aniplay --scan-only

# Debug mode
aniplay --debug

# Show help
aniplay --help
```

## Configuration

AniPlay stores its configuration in standard XDG directories:

- **Config**: `~/.config/aniplay/`
- **Data**: `~/.local/share/aniplay/`
- **Cache**: `~/.cache/aniplay/`

### Settings File

The main configuration is stored in the database, but you can also use:
- `~/.config/aniplay/settings.json` - User preferences
- `/etc/aniplay/default.conf` - System-wide defaults

## Library Organization

AniPlay expects your anime to be organized like this:

```
library/
├── Anime Series 1/
│   ├── Episode 01.mkv
│   ├── Episode 02.mkv
│   └── ...
├── Anime Series 2/
│   ├── S01E01.mp4
│   ├── S01E02.mp4
│   └── ...
└── Movies/
    ├── Movie 1.mkv
    └── Movie 2.mp4
```

### Supported Formats

**Video**: MP4, MKV, AVI, MOV, WEBM, M4V, FLV, WMV
**Subtitles**: SRT, VTT, ASS, SSA (auto-detected)

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
git clone https://github.com/naisam370-jpg/aniplay.git
cd aniplay

# Install development dependencies
pip3 install -r requirements.txt -r requirements-dev.txt

# Run tests
pytest

# Code formatting
black src/
```

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Support (coming soon)

- 📖 **Documentation**: [Wiki](https://github.com/naisam370-jpg/aniplay/wiki)
- 🐛 **Bug Reports**: [Issues](https://github.com/naisam370-jpg/aniplay/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/naisam370-jpg/aniplay/discussions)
- 📧 **Email**: naisam370@gmail.com

## Roadmap

- [ ] **v1.1**: Web interface for remote access
- [ ] **v1.2**: Mobile companion app
- [ ] **v1.3**: Streaming service integration
- [ ] **v1.4**: Social features (watch parties, recommendations)
- [ ] **v2.0**: Cross-platform support (Windows, macOS)

## Acknowledgments

- **mpv** - Excellent media player backend
- **PyQt5** - Powerful GUI framework  
- **FFmpeg** - Media processing capabilities
- **MyAnimeList** - Anime metadata source
- **The Anime Community** - For inspiration and feedback

---

Made with ❤️ for anime fans by anime fans.