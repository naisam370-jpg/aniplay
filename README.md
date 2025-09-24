# AniPlay - Anime Library Manager

A professional anime player with MyAnimeList integration, featuring automatic cover art fetching, library management, and wide format support via MPV.

## Features

- 🎌 **Anime Library Management** - Organize your anime collection with folder-based structure
- 🖼️ **Automatic Cover Art** - Fetches covers from MyAnimeList.net database
- 📝 **Anime Information** - Display descriptions, ratings, and metadata
- 🎥 **Professional Video Player** - Wide format support via MPV backend
- 🔍 **Smart Search** - Find anime in your library quickly
- 💾 **Local Database** - Cache anime information for offline browsing
- 🎨 **Modern UI** - Clean, responsive interface designed for anime lovers

## Setup

### Library Structure
Create your anime library with this folder structure:
```
anime-library/
├── Attack on Titan/
│   ├── Season 1/
│   │   ├── Episode 01.mkv
│   │   └── Episode 02.mkv
│   └── Season 2/
├── Death Note/
│   ├── Episode 01.mkv
│   └── Episode 02.mkv
└── Your Anime Name/
    └── episodes...
```

### Development

```bash
# Install dependencies
npm install

# Run in development mode
npm run dev -- --disable-gpu --no-sandbox

# Build for production
npm run build

# Package for Linux
npm run package-linux
```

## Requirements

- Node.js 18+
- MPV installed on system
- Linux (primary target)
- Internet connection for initial cover/metadata fetching

## How It Works

1. **Library Scanning**: AniPlay scans your `anime-library/` directory
2. **MAL Integration**: Searches MyAnimeList for each anime folder name
3. **Cover Fetching**: Downloads and caches cover images to `covers/`
4. **Database Storage**: Stores anime metadata in local SQLite database
5. **Smart Playback**: Opens episodes with MPV when selected

## License

GPL-3.0-only
