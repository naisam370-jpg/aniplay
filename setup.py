#!/usr/bin/env python3
"""
Setup script for AniPlay
File: setup.py
"""

from setuptools import setup, find_packages
from pathlib import Path
import subprocess
import sys

# Read version from __init__.py
def get_version():
    init_file = Path("src/aniplay/__init__.py")
    if init_file.exists():
        with open(init_file) as f:
            for line in f:
                if line.startswith("__version__"):
                    return line.split("=")[1].strip().strip('"\'')
    return "1.0.0"

# Read long description from README
def get_long_description():
    readme_file = Path("README.md")
    if readme_file.exists():
        with open(readme_file, encoding="utf-8") as f:
            return f.read()
    return ""

# Check if we can build C++ extensions
def can_build_cpp():
    try:
        subprocess.run(["cmake", "--version"], 
                      capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

# Base requirements
requirements = [
    "PyQt5>=5.15.0",
    "Pillow>=8.0.0",
    "requests>=2.25.0",
    "python-dateutil>=2.8.0",
]

# Optional requirements
extras_require = {
    "metadata": [
        "beautifulsoup4>=4.9.0",
        "lxml>=4.6.0",
    ],
    "dev": [
        "pytest>=6.0.0",
        "pytest-qt>=4.0.0",
        "black>=21.0.0",
        "flake8>=3.8.0",
        "mypy>=0.800",
    ],
    "build": [
        "wheel>=0.36.0",
        "setuptools>=50.0.0",
    ]
}

# All optional requirements
extras_require["all"] = sum(extras_require.values(), [])

setup(
    name="aniplay",
    version=get_version(),
    author="AniPlay Developer",
    author_email="developer@aniplay.org",
    description="A modern anime library manager and player for Linux",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/naisam370-jpg/aniplay",
    project_urls={
        "Bug Tracker": "https://github.com/naisam370-jpg/aniplay/issues",
        "Documentation": "https://github.com/naisam370-jpg/aniplay/wiki",
        "Source Code": "https://github.com/naisam370-jpg/aniplay",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={
        "aniplay": [
            "data/sql/*.sql",
            "data/ui/*.ui",
            "data/icons/*/*/*.png",
            "data/icons/*.svg",
        ],
    },
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require=extras_require,
    entry_points={
        "console_scripts": [
            "aniplay=aniplay.main:main",
            "aniplay-scan=aniplay.cli.scan:main",
        ],
        "gui_scripts": [
            "aniplay-gui=aniplay.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Video",
        "Topic :: Multimedia :: Video :: Display",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: C++",
        "Environment :: X11 Applications :: Qt",
        "Topic :: Desktop Environment",
    ],
    keywords="anime video player library manager qt5 media",
    zip_safe=False,
    cmdclass={},
)

# Post-install message
def print_post_install_message():
    print("""
╔══════════════════════════════════════════════════════════════╗
║                    AniPlay Installation Complete!            ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  🎉 Installation successful!                                 ║
║                                                              ║
║  📁 Default library location:                               ║
║     ~/.local/share/aniplay/library                          ║
║                                                              ║
║  🚀 To start AniPlay:                                        ║
║     aniplay                                                  ║
║                                                              ║
║  🔧 To scan library without GUI:                            ║
║     aniplay --scan-only                                     ║
║                                                              ║
║  📋 Required dependencies:                                   ║
║     • ffmpeg (for video thumbnails and metadata)            ║
║     • mpv (recommended media player)                        ║
║                                                              ║
║  💡 Install dependencies on Debian/Ubuntu:                  ║
║     sudo apt install ffmpeg mpv                             ║
║                                                              ║
║  📖 Documentation:                                           ║
║     https://github.com/naisam370-jpg/aniplay/wiki           ║
║                                                              ║
║  🐛 Report issues:                                           ║
║     https://github.com/naisam370-jpg/aniplay/issues         ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "install":
        # This will run after successful install
        import atexit
        atexit.register(print_post_install_message)