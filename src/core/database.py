import sqlite3
from pathlib import Path

class DatabaseManager:
    class DatabaseManager:
        def __init__(self):
            # This ensures the DB is always in the same folder as this script
            base_dir = Path(__file__).parent.parent.absolute()
            self.db_path = base_dir / "aniplay.db"
            self.conn = sqlite3.connect(self.db_path)
            self.create_tables()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL;")  # High-speed concurrent access
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Anime Table: Stores Series level info + Metadata from API
            cursor.execute('''CREATE TABLE IF NOT EXISTS anime (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                folder_path TEXT UNIQUE,
                poster_path TEXT,
                mal_id INTEGER,
                rating REAL,
                synopsis TEXT,
                genres TEXT
            )''')

            # Episodes Table: Stores specific file info
            cursor.execute('''CREATE TABLE IF NOT EXISTS episodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                anime_id INTEGER,
                file_path TEXT UNIQUE,
                file_hash TEXT UNIQUE,
                season INTEGER,
                episode_num INTEGER,
                thumbnail_path TEXT,
                last_position REAL DEFAULT 0,
                is_watched INTEGER DEFAULT 0,
                FOREIGN KEY(anime_id) REFERENCES anime(id) ON DELETE CASCADE
            )''')
            conn.commit()

    def get_or_create_anime(self, title, path, poster=None):
        """Returns the ID of an anime, creating it if it doesn't exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO anime (title, folder_path, poster_path)
                VALUES (?, ?, ?)
                ON CONFLICT(folder_path) DO UPDATE SET
                poster_path = COALESCE(excluded.poster_path, anime.poster_path)
                RETURNING id
            ''', (title, path, poster))
            result = cursor.fetchone()
            return result[0] if result else None

    def update_anime_metadata(self, anime_id, mal_id, rating, synopsis, genres):
        """Updates the metadata fetched from Jikan API."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE anime SET 
                mal_id = ?, rating = ?, synopsis = ?, genres = ?
                WHERE id = ?
            ''', (mal_id, rating, synopsis, genres, anime_id))
            conn.commit()

    def add_episode(self, anime_id, file_path, season, episode, file_hash, thumbnail_path):
        """Adds or updates an episode entry."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO episodes (anime_id, file_path, file_hash, season, episode_num, thumbnail_path)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(file_hash) DO UPDATE SET
                file_path = excluded.file_path,
                thumbnail_path = COALESCE(excluded.thumbnail_path, episodes.thumbnail_path)
            ''', (anime_id, file_path, file_hash, season, episode, thumbnail_path))
            conn.commit()

    def get_library(self):
        """Returns all anime for the Library grid view."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, poster_path, rating FROM anime ORDER BY title ASC")
            return cursor.fetchall()

    def get_anime_details(self, anime_id):
        """Returns full details for a specific anime."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM anime WHERE id = ?", (anime_id,))
            return cursor.fetchone()

    def get_episodes(self, anime_id, season=1):
        """Returns episodes for a specific anime and season."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT episode_num, thumbnail_path, file_path 
                FROM episodes 
                WHERE anime_id = ? AND season = ?
                ORDER BY episode_num ASC
            """, (anime_id, season))
            return cursor.fetchall()