-- Anime series table
CREATE TABLE anime (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    path TEXT NOT NULL,
    cover_path TEXT,
    description TEXT,
    year INTEGER,
    rating REAL DEFAULT 0.0,
    status TEXT DEFAULT 'ongoing', -- ongoing, completed, planned
    mal_id INTEGER,
    total_episodes INTEGER DEFAULT 0,
    date_added DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_watched DATETIME,
    is_favorite BOOLEAN DEFAULT 0
);

-- Episodes table
CREATE TABLE episodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    anime_id INTEGER NOT NULL,
    episode_number INTEGER NOT NULL,
    title TEXT,
    file_path TEXT NOT NULL,
    duration INTEGER DEFAULT 0, -- in seconds
    thumbnail_path TEXT,
    date_added DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (anime_id) REFERENCES anime (id) ON DELETE CASCADE,
    UNIQUE(anime_id, episode_number)
);

-- Watch progress table
CREATE TABLE watch_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    episode_id INTEGER NOT NULL,
    progress_seconds INTEGER DEFAULT 0,
    is_watched BOOLEAN DEFAULT 0,
    last_watched DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (episode_id) REFERENCES episodes (id) ON DELETE CASCADE,
    UNIQUE(episode_id)
);

-- User settings/preferences
CREATE TABLE user_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

-- Search/filter history
CREATE TABLE search_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);