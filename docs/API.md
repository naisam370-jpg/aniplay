# AniPlay API Documentation

## IPC Events

### Library Events
- `library:scan` - Scan anime library and fetch MAL data
- `library:get-all` - Get all anime from database
- `library:search` - Search anime library
- `anime:get-episodes` - Get episodes for specific anime

### Video Events
- `video:load` - Load a video file for playback
- `video:play` - Start playback
- `video:pause` - Pause playback
- `video:seek` - Seek to specific time

### File Events
- `file:select-library` - Open directory selection dialog

## Database Schema

### Anime Table
- id (INTEGER PRIMARY KEY)
- title (TEXT)
- path (TEXT UNIQUE)
- cover (TEXT)
- description (TEXT)
- score (REAL)
- episodes (INTEGER)
- status (TEXT)
- genres (TEXT)
- year (INTEGER)
- created_at (DATETIME)
- updated_at (DATETIME)

### Watch History Table
- id (INTEGER PRIMARY KEY)
- anime_id (INTEGER)
- episode_path (TEXT)
- position (REAL)
- duration (REAL)
- watched_at (DATETIME)

## MyAnimeList Integration

The app automatically searches MyAnimeList.net for anime information based on folder names in your library. It fetches:

- Anime title and synopsis
- Cover art
- Score and episode count
- Status and genres
- Release year

Cover images are cached locally in the `covers/` directory.
