import sqlite3
import os
from pathlib import Path

class DatabaseManager:
    def __init__(self):
        base_dir = Path(__file__).parent.parent.absolute()
        self.db_path = base_dir / "aniplay.db"
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        """Creates the full schema. Note: This only runs if the .db file is new/deleted."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Anime Table
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

            # Episode Table - Including 'title' and 'episode_num'
            cursor.execute('''CREATE TABLE IF NOT EXISTS episodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                anime_id INTEGER,
                file_path TEXT UNIQUE,
                file_hash TEXT UNIQUE,
                season INTEGER,
                title TEXT,
                episode_num INTEGER,
                thumbnail_path TEXT,
                last_position REAL DEFAULT 0,
                is_watched INTEGER DEFAULT 0,
                FOREIGN KEY(anime_id) REFERENCES anime(id) ON DELETE CASCADE
            )''')
            conn.commit()

    def get_or_create_anime(self, title, path, poster=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO anime (title, folder_path, poster_path)
                VALUES (?, ?, ?)
                ON CONFLICT(folder_path) DO UPDATE SET
                poster_path = COALESCE(excluded.poster_path, anime.poster_path)
                RETURNING id
            ''', (title, path, poster))
            res = cursor.fetchone()
            return res[0] if res else None

    def add_episode(self, anime_id, file_path, season, episode, title, file_hash, thumbnail_path):
        """Saves the title extracted by the scanner."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO episodes (anime_id, file_path, file_hash, season, title, episode_num, thumbnail_path)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(file_hash) DO UPDATE SET
                file_path = excluded.file_path,
                title = COALESCE(excluded.title, episodes.title),
                thumbnail_path = COALESCE(excluded.thumbnail_path, episodes.thumbnail_path)
            ''', (anime_id, file_path, file_hash, season, title, episode, thumbnail_path))
            conn.commit()

    def get_episodes(self, anime_id):
        """Returns 5 columns for the UI to unpack."""
        query = """
                SELECT id, file_path, thumbnail_path, title, episode_num 
                FROM episodes 
                WHERE anime_id = ? 
                ORDER BY episode_num ASC
                """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (anime_id,))
            return cursor.fetchall()

    def get_library(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, poster_path, rating FROM anime ORDER BY title ASC")
            return cursor.fetchall()

    def get_anime_details(self, anime_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM anime WHERE id = ?", (anime_id,))
            return cursor.fetchone()

    def update_anime_metadata(self, anime_id, mal_id, rating, synopsis, genres):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE anime SET mal_id=?, rating=?, synopsis=?, genres=? WHERE id=?",
                           (mal_id, rating, synopsis, genres, anime_id))
            conn.commit()