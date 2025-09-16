#!/usr/bin/env python3
"""
AniPlay Main Entry Point - Fixed Import Version
File: src/aniplay/main.py
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path so we can import aniplay modules
current_dir = Path(__file__).resolve().parent
src_dir = current_dir.parent
project_root = src_dir.parent

# Add to Python path
sys.path.insert(0, str(src_dir))

# Now we can import using absolute imports
try:
    from aniplay.gui.main_window import AniPlayMainWindow
    from aniplay.core.database import DatabaseManager
    from aniplay.utils.file_utils import ensure_directory
except ImportError as e:
    # Fallback: try to import from current directory structure
    print(f"Import error: {e}")
    print("Trying fallback imports...")
    
    # Add current directory to path
    sys.path.insert(0, str(current_dir))
    
    try:
        from gui.main_window import AniPlayMainWindow
        from core.database import DatabaseManager
        from utils.file_utils import ensure_directory
    except ImportError as e2:
        print(f"Fallback import also failed: {e2}")
        print("\n❌ Missing required files. Please ensure all modules are in place:")
        print("  - src/aniplay/gui/main_window.py")
        print("  - src/aniplay/core/database.py")
        print("  - src/aniplay/utils/file_utils.py")
        print("  - src/aniplay/models/anime.py")
        print("  - src/aniplay/models/episode.py")
        sys.exit(1)

import argparse
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QDir, QStandardPaths
from PyQt5.QtGui import QIcon

class AniPlayApplication:
    """Main AniPlay application class"""
    
    def __init__(self):
        self.app = None
        self.main_window = None
        self.setup_paths()
    
    def setup_paths(self):
        """Setup application data paths following XDG standards"""
        
        # Get user data directories
        if os.name == 'nt':  # Windows
            data_dir = os.path.join(os.path.expanduser("~"), "AppData", "Local", "AniPlay")
            config_dir = data_dir
            cache_dir = os.path.join(data_dir, "cache")
        else:  # Linux/macOS
            data_dir = os.path.join(
                os.environ.get('XDG_DATA_HOME', os.path.expanduser("~/.local/share")), 
                "aniplay"
            )
            config_dir = os.path.join(
                os.environ.get('XDG_CONFIG_HOME', os.path.expanduser("~/.config")), 
                "aniplay"
            )
            cache_dir = os.path.join(
                os.environ.get('XDG_CACHE_HOME', os.path.expanduser("~/.cache")), 
                "aniplay"
            )
        
        # Set up paths
        self.data_dir = Path(data_dir)
        self.config_dir = Path(config_dir)
        self.cache_dir = Path(cache_dir)
        
        # Default paths
        self.library_path = self.data_dir / "library"
        self.covers_path = self.cache_dir / "covers"
        self.thumbs_path = self.cache_dir / "thumbnails"
        self.db_path = self.data_dir / "aniplay.db"
        
        # Create directories
        for path in [self.data_dir, self.config_dir, self.cache_dir, 
                     self.library_path, self.covers_path, self.thumbs_path]:
            ensure_directory(str(path))
    
    def parse_arguments(self):
        """Parse command line arguments"""
        parser = argparse.ArgumentParser(
            description='AniPlay - Anime Library Manager and Player',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  aniplay                          # Start with default settings
  aniplay --library ~/Anime       # Use custom library path
  aniplay --scan-only              # Scan library and exit
  aniplay --debug                  # Enable debug logging
            """
        )
        
        parser.add_argument(
            '--library', '-l',
            type=str,
            help='Library directory path (default: ~/.local/share/aniplay/library)'
        )
        
        parser.add_argument(
            '--database', '-d',
            type=str,
            help='Database file path (default: ~/.local/share/aniplay/aniplay.db)'
        )
        
        parser.add_argument(
            '--scan-only',
            action='store_true',
            help='Scan library and exit (no GUI)'
        )
        
        parser.add_argument(
            '--rescan',
            action='store_true',
            help='Force rescan of entire library on startup'
        )
        
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Enable debug logging'
        )
        
        parser.add_argument(
            '--version', '-v',
            action='version',
            version='AniPlay 1.0.0'
        )
        
        # Add a test mode to check if everything is working
        parser.add_argument(
            '--test',
            action='store_true',
            help='Test installation and show status'
        )
        
        return parser.parse_args()
    
    def test_installation(self):
        """Test if all required components are available"""
        print("🔍 Testing AniPlay installation...\n")
        
        # Test Python modules
        modules_status = []
        required_modules = [
            ('PyQt5', 'PyQt5.QtWidgets'),
            ('Database', 'aniplay.core.database'),
            ('Models', 'aniplay.models.anime'),
            ('Utils', 'aniplay.utils.file_utils'),
        ]
        
        for name, module in required_modules:
            try:
                __import__(module)
                modules_status.append((name, "✅ OK"))
            except ImportError as e:
                modules_status.append((name, f"❌ Missing: {e}"))
        
        # Test system dependencies
        system_status = []
        import subprocess
        
        system_deps = [
            ('ffprobe', ['ffprobe', '-version']),
            ('mpv', ['mpv', '--version']),
        ]
        
        for name, cmd in system_deps:
            try:
                subprocess.run(cmd, capture_output=True, check=True, timeout=5)
                system_status.append((name, "✅ Available"))
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                system_status.append((name, "⚠️  Not found"))
        
        # Print results
        print("📦 Python Modules:")
        for name, status in modules_status:
            print(f"  {name:<15} {status}")
        
        print("\n🔧 System Dependencies:")
        for name, status in system_status:
            print(f"  {name:<15} {status}")
        
        print(f"\n📁 Data Directories:")
        print(f"  Library:     {self.library_path}")
        print(f"  Database:    {self.db_path}")
        print(f"  Covers:      {self.covers_path}")
        print(f"  Thumbnails:  {self.thumbs_path}")
        
        # Check if directories exist
        for name, path in [("Library", self.library_path), ("Covers", self.covers_path), 
                          ("Thumbnails", self.thumbs_path)]:
            status = "✅ Exists" if path.exists() else "⚠️  Will be created"
            print(f"  {name:<15} {status}")
        
        # Overall status
        python_ok = all("✅" in status for _, status in modules_status)
        print(f"\n🎯 Installation Status:")
        if python_ok:
            print("✅ Ready to run!")
            return True
        else:
            print("❌ Missing required components")
            return False
    
    def check_dependencies(self):
        """Check for required dependencies"""
        missing_deps = []
        
        # Check for ffmpeg/ffprobe (for video info and thumbnails)
        try:
            import subprocess
            subprocess.run(['ffprobe', '-version'], 
                         capture_output=True, check=True, timeout=10)
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            missing_deps.append("ffmpeg/ffprobe (for video metadata and thumbnails)")
        
        # Check for mpv (default player)
        try:
            subprocess.run(['mpv', '--version'], 
                         capture_output=True, check=True, timeout=10)
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            print("Warning: mpv not found. You can configure a different player in settings.")
        
        if missing_deps:
            deps_text = "\n".join(f"- {dep}" for dep in missing_deps)
            print(f"Missing dependencies:\n{deps_text}")
            print("\nPlease install the missing dependencies and try again.")
            print("On Ubuntu/Debian: sudo apt install ffmpeg mpv")
            print("On Arch: sudo pacman -S ffmpeg mpv")
            print("On Fedora: sudo dnf install ffmpeg mpv")
            return False
        
        return True
    
    def run_scan_only(self, library_path: str, db_path: str):
        """Run library scan without GUI"""
        try:
            from aniplay.core.library_scanner import LibraryScanner
        except ImportError:
            print("❌ Library scanner not available. Please ensure all files are installed.")
            return False
        
        print(f"Scanning library: {library_path}")
        
        # Initialize database and scanner
        db = DatabaseManager(str(db_path))
        scanner = LibraryScanner(db, str(self.covers_path), str(self.thumbs_path))
        
        try:
            stats = scanner.scan_library(library_path, update_existing=True)
            print(f"\nScan completed successfully!")
            print(f"- Anime added: {stats['anime_added']}")
            print(f"- Episodes added: {stats['episodes_added']}")
            print(f"- Updated: {stats['updated']}")
            print(f"- Errors: {stats['errors']}")
            return True
        except Exception as e:
            print(f"Scan failed: {e}")
            return False
    
    def run_gui(self, args):
        """Run the GUI application"""
        # Create Qt application
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("AniPlay")
        self.app.setApplicationVersion("1.0.0")
        self.app.setOrganizationName("AniPlay")
        
        # Set application icon if available
        icon_path = self.data_dir.parent / "share" / "icons" / "hicolor" / "64x64" / "apps" / "aniplay.png"
        if icon_path.exists():
            self.app.setWindowIcon(QIcon(str(icon_path)))
        
        # Use custom library path if provided
        library_path = args.library if args.library else str(self.library_path)
        db_path = args.database if args.database else str(self.db_path)
        
        # Ensure library directory exists
        if not ensure_directory(library_path):
            QMessageBox.critical(None, "Error", 
                               f"Could not create library directory:\n{library_path}")
            return False
        
        try:
            # Create main window
            self.main_window = AniPlayMainWindow(
                library_path=library_path,
                covers_path=str(self.covers_path),
                thumbs_path=str(self.thumbs_path),
                db_path=db_path
            )
            
            # Show window
            self.main_window.showMaximized()
            
            # Force rescan if requested
            if args.rescan:
                self.main_window.scan_library()
            
            # Run application
            return self.app.exec_() == 0
            
        except Exception as e:
            QMessageBox.critical(None, "Startup Error", 
                               f"Failed to start AniPlay:\n{str(e)}")
            print(f"Detailed error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def run(self):
        """Main application entry point"""
        # Parse arguments
        args = self.parse_arguments()
        
        # Test mode
        if args.test:
            return 0 if self.test_installation() else 1
        
        # Setup logging
        if args.debug:
            import logging
            logging.basicConfig(level=logging.DEBUG)
        
        # Use custom library path if provided
        library_path = args.library if args.library else str(self.library_path)
        db_path = args.database if args.database else str(self.db_path)
        
        # Scan-only mode
        if args.scan_only:
            return 0 if self.run_scan_only(library_path, db_path) else 1
        
        # Check dependencies for GUI mode
        if not self.check_dependencies():
            return 1
        
        # GUI mode
        success = self.run_gui(args)
        return 0 if success else 1


def main():
    """Entry point for the aniplay command"""
    app = AniPlayApplication()
    sys.exit(app.run())


if __name__ == "__main__":
    main()