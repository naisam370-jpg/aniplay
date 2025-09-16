#!/bin/bash
# AniPlay Installation Script
# File: install.sh

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}$1${NC}"
}

# Check if script is run from correct directory
check_directory() {
    if [[ ! -f "src/aniplay/main.py" ]]; then
        print_error "This doesn't appear to be the AniPlay source directory."
        print_error "Please run this script from the root of the AniPlay project."
        exit 1
    fi
}

# Check Python version
check_python() {
    print_status "Checking Python version..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.8 or later."
        exit 1
    fi
    
    python_version=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
    required_version="3.8"
    
    if [[ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]]; then
        print_error "Python 3.8+ required, found $python_version"
        print_error "Please upgrade Python to 3.8 or later."
        exit 1
    fi
    
    print_status "Python $python_version found ✓"
}

# Check system dependencies
check_system_deps() {
    print_status "Checking system dependencies..."
    
    missing_deps=()
    
    # Check for ffmpeg/ffprobe (required for video metadata)
    if ! command -v ffprobe &> /dev/null; then
        missing_deps+=("ffmpeg")
    fi
    
    # Check for mpv (recommended player)
    if ! command -v mpv &> /dev/null; then
        print_warning "mpv not found - you can install it later or configure a different player"
    else
        print_status "mpv found ✓"
    fi
    
    # Check for pip
    if ! command -v pip3 &> /dev/null; then
        missing_deps+=("python3-pip")
    fi
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        print_error "Missing required dependencies: ${missing_deps[*]}"
        echo
        print_status "Install them with:"
        
        # Detect distribution and show appropriate command
        if command -v apt &> /dev/null; then
            echo "  sudo apt update && sudo apt install ${missing_deps[*]}"
        elif command -v dnf &> /dev/null; then
            echo "  sudo dnf install ${missing_deps[*]}"
        elif command -v pacman &> /dev/null; then
            echo "  sudo pacman -S ${missing_deps[*]}"
        elif command -v zypper &> /dev/null; then
            echo "  sudo zypper install ${missing_deps[*]}"
        else
            echo "  Please install: ${missing_deps[*]}"
        fi
        
        echo
        read -p "Continue installation anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        print_status "System dependencies satisfied ✓"
    fi
}

# Install Python dependencies
install_python_deps() {
    print_status "Installing Python dependencies..."
    
    # Check if requirements.txt exists
    if [[ ! -f "requirements.txt" ]]; then
        print_warning "requirements.txt not found, creating it..."
        cat > requirements.txt << EOF
PyQt5>=5.15.0
Pillow>=8.0.0
requests>=2.25.0
python-dateutil>=2.8.0
EOF
    fi
    
    # Install dependencies
    if pip3 install --user -r requirements.txt; then
        print_status "Python dependencies installed ✓"
    else
        print_error "Failed to install Python dependencies"
        exit 1
    fi
}

# Build C++ backend (optional)
build_backend() {
    print_status "Checking for C++ build tools..."
    
    if command -v cmake &> /dev/null && command -v make &> /dev/null; then
        print_status "Building C++ backend..."
        
        # Create build directory
        mkdir -p build
        cd build
        
        # Check if CMakeLists.txt exists in backend
        if [[ -f "../src/backend/CMakeLists.txt" ]]; then
            if cmake ../src/backend && make; then
                print_status "C++ backend built successfully ✓"
            else
                print_warning "C++ backend build failed, continuing without it"
            fi
        else
            print_warning "No C++ backend found, skipping build"
        fi
        
        cd ..
    else
        print_warning "cmake/make not found, skipping C++ backend build"
        print_status "You can install build tools with:"
        
        if command -v apt &> /dev/null; then
            echo "  sudo apt install cmake build-essential"
        elif command -v dnf &> /dev/null; then
            echo "  sudo dnf install cmake gcc-c++ make"
        elif command -v pacman &> /dev/null; then
            echo "  sudo pacman -S cmake base-devel"
        fi
    fi
}

# Create necessary directories
create_directories() {
    print_status "Creating application directories..."
    
    # Create XDG directories
    mkdir -p ~/.local/share/aniplay/library
    mkdir -p ~/.config/aniplay
    mkdir -p ~/.cache/aniplay/{covers,thumbnails}
    
    print_status "Application directories created ✓"
}

# Install desktop entry
install_desktop_entry() {
    print_status "Installing desktop entry..."
    
    # Create desktop entry if it doesn't exist
    if [[ ! -f "debian/aniplay.desktop" ]]; then
        mkdir -p debian
        cat > debian/aniplay.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=AniPlay
Comment=Anime Library Manager and Player
Exec=$(pwd)/src/aniplay/main.py
Icon=aniplay
Terminal=false
Categories=AudioVideo;Video;Player;Qt;
MimeType=video/mp4;video/x-matroska;video/avi;video/quicktime;video/webm;
Keywords=anime;video;player;media;library;
StartupNotify=true
StartupWMClass=aniplay
Path=$(pwd)
EOF
    fi
    
    # Install for current user
    mkdir -p ~/.local/share/applications
    cp debian/aniplay.desktop ~/.local/share/applications/
    
    # Update desktop database if available
    if command -v update-desktop-database &> /dev/null; then
        update-desktop-database ~/.local/share/applications/
    fi
    
    print_status "Desktop entry installed ✓"
}

# Create command line shortcut
create_cli_shortcut() {
    print_status "Creating command line shortcut..."
    
    # Create local bin directory if it doesn't exist
    mkdir -p ~/.local/bin
    
    # Create wrapper script
    cat > ~/.local/bin/aniplay << EOF
#!/bin/bash
cd "$(dirname "\$0")/../../.."
exec python3 "$(pwd)/src/aniplay/main.py" "\$@"
EOF
    
    # Make it executable
    chmod +x ~/.local/bin/aniplay
    
    # Check if ~/.local/bin is in PATH
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        print_warning "~/.local/bin is not in your PATH"
        print_status "Add this to your ~/.bashrc or ~/.zshrc:"
        echo '  export PATH="$HOME/.local/bin:$PATH"'
        echo
        print_status "Or run AniPlay directly with: ~/.local/bin/aniplay"
    else
        print_status "Command line shortcut created ✓"
        print_status "You can now run 'aniplay' from anywhere"
    fi
}

# Set up database schema
setup_database() {
    print_status "Setting up database schema..."
    
    # Create SQL schema file if it doesn't exist
    if [[ ! -f "data/sql/schema.sql" ]]; then
        mkdir -p data/sql
        cat > data/sql/schema.sql << 'EOF'
-- AniPlay Database Schema
CREATE TABLE IF NOT EXISTS anime (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    path TEXT NOT NULL,
    cover_path TEXT,
    description TEXT,
    year INTEGER,
    rating REAL DEFAULT 0.0,
    status TEXT DEFAULT 'ongoing',
    mal_id INTEGER,
    total_episodes INTEGER DEFAULT 0,
    date_added DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_watched DATETIME,
    is_favorite BOOLEAN DEFAULT 0
);

CREATE TABLE IF NOT EXISTS episodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    anime_id INTEGER NOT NULL,
    episode_number INTEGER NOT NULL,
    title TEXT,
    file_path TEXT NOT NULL,
    duration INTEGER DEFAULT 0,
    thumbnail_path TEXT,
    date_added DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (anime_id) REFERENCES anime (id) ON DELETE CASCADE,
    UNIQUE(anime_id, episode_number)
);

CREATE TABLE IF NOT EXISTS watch_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    episode_id INTEGER NOT NULL,
    progress_seconds INTEGER DEFAULT 0,
    is_watched BOOLEAN DEFAULT 0,
    last_watched DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (episode_id) REFERENCES episodes (id) ON DELETE CASCADE,
    UNIQUE(episode_id)
);

CREATE TABLE IF NOT EXISTS user_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
EOF
    fi
    
    print_status "Database schema ready ✓"
}

# Test installation
test_installation() {
    print_status "Testing installation..."
    
    if python3 src/aniplay/main.py --version &> /dev/null; then
        print_status "Installation test passed ✓"
    else
        print_warning "Installation test failed, but this might be normal if not all files are in place yet"
    fi
}

# Main installation function
main() {
    print_header "╔══════════════════════════════════════════════════╗"
    print_header "║              AniPlay Installation                ║"
    print_header "╚══════════════════════════════════════════════════╝"
    echo
    
    # Run installation steps
    check_directory
    check_python
    check_system_deps
    install_python_deps
    build_backend
    create_directories
    setup_database
    install_desktop_entry
    create_cli_shortcut
    test_installation
    
    echo
    print_header "╔══════════════════════════════════════════════════╗"
    print_header "║            Installation Complete! 🎉             ║"
    print_header "╚══════════════════════════════════════════════════╝"
    echo
    print_status "AniPlay has been installed successfully!"
    echo
    print_status "📁 Library location: ~/.local/share/aniplay/library"
    print_status "⚙️  Config location: ~/.config/aniplay/"
    print_status "💾 Cache location: ~/.cache/aniplay/"
    echo
    print_status "🚀 To start AniPlay:"
    echo "   aniplay                    # If ~/.local/bin is in PATH"
    echo "   ~/.local/bin/aniplay       # Direct path"
    echo "   python3 src/aniplay/main.py  # From source directory"
    echo
    print_status "🔧 First time setup:"
    echo "   1. Launch AniPlay"
    echo "   2. Go to Settings → Library to configure your anime folder"
    echo "   3. Click the refresh button to scan your library"
    echo "   4. Enjoy your enhanced anime experience!"
    echo
    print_status "📖 For help and documentation:"
    echo "   https://github.com/naisam370-jpg/aniplay"
    echo
}

# Check if script is being sourced or executed
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi