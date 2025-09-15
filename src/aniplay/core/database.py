import sqlite3
import os
from contextlib import contextmanager
from typing import List, Optional, Dict, Any
from ..models.anime import Anime
from ..models.episode import Episode
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.ensure_database()
    
    def ensure_database(self):
        """Create database and tables if they don't exist"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Read schema from file
        schema_path = os.path.join(os.path.dirname(__file__), '../../data/sql/schema.sql')
        if os.path.exists(schema_path):
            with open(schema_path, 'r') as f:
                schema = f.read()
        else:
            schema = self._get_default_schema()
        
        with self.get_connection() as conn:
            conn.executescript(schema)
    
    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    # Anime operations
    def add_anime(self, anime: Anime) -> int:
        with self.get_connection() as conn:
            cursor = conn.execute('''
                INSERT INTO anime (name, path, cover_path, description, year, rating, 
                                 status, mal_id, total_episodes, is_favorite)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (anime.name, anime.path, anime.cover_path, anime.description,
                  anime.year, anime.rating, anime.status, anime.mal_id,
                  anime.total_episodes, anime.is_favorite))
            return cursor.lastrowid
    
    def get_all_anime(self, sort_by: str = "name", reverse: bool = False) -> List[Anime]:
        valid_sorts = ["name", "date_added", "last_watched", "rating", "year"]
        if sort_by not in valid_sorts:
            sort_by = "name"
        
        order = "DESC" if reverse else "ASC"
        
        with self.get_connection() as conn:
            rows = conn.execute(f'SELECT * FROM anime ORDER BY {sort_by} {order}').fetchall()
            return [self._row_to_anime(row) for row in rows]
    
    def search_anime(self, query: str) -> List[Anime]:
        with self.get_connection() as conn:
            rows = conn.execute('''
                SELECT * FROM anime 
                WHERE name LIKE ? OR description LIKE ?
                ORDER BY name
            ''', (f'%{query}%', f'%{query}%')).fetchall()
            return [self._row_to_anime(row) for row in rows]
    
    def get_favorites(self) -> List[Anime]:
        with self.get_connection() as conn:
            rows = conn.execute('SELECT * FROM anime WHERE is_favorite = 1 ORDER BY name').fetchall()
            return [self._row_to_anime(row) for row in rows]
    
    def get_recently_watched(self, limit: int = 10) -> List[Anime]:
        with self.get_connection() as conn:
            rows = conn.execute('''
                SELECT * FROM anime 
                WHERE last_watched IS NOT NULL 
                ORDER BY last_watched DESC 
                LIMIT ?
            ''', (limit,)).fetchall()
            return [self._row_to_anime(row) for row in rows]
    
    # Episode operations
    def add_episode(self, episode: Episode) -> int:
        with self.get_connection() as conn:
            cursor = conn.execute('''
                INSERT INTO episodes (anime_id, episode_number, title, file_path, 
                                    duration, thumbnail_path)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (episode.anime_id, episode.episode_number, episode.title,
                  episode.file_path, episode.duration, episode.thumbnail_path))
            return cursor.lastrowid
    
    def get_episodes(self, anime_id: int) -> List[Episode]:
        with self.get_connection() as conn:
            rows = conn.execute('''
                SELECT e.*, wp.progress_seconds, wp.is_watched, wp.last_watched
                FROM episodes e
                LEFT JOIN watch_progress wp ON e.id = wp.episode_id
                WHERE e.anime_id = ?
                ORDER BY e.episode_number
            ''', (anime_id,)).fetchall()
            return [self._row_to_episode(row) for row in rows]
    
    # Watch progress operations
    def update_progress(self, episode_id: int, progress_seconds: int, is_watched: bool = False):
        with self.get_connection() as conn:
            conn.execute('''
                INSERT OR REPLACE INTO watch_progress 
                (episode_id, progress_seconds, is_watched, last_watched)
                VALUES (?, ?, ?, ?)
            ''', (episode_id, progress_seconds, is_watched, datetime.now()))
            
            # Update anime last_watched
            conn.execute('''
                UPDATE anime SET last_watched = ? 
                WHERE id = (SELECT anime_id FROM episodes WHERE id = ?)
            ''', (datetime.now(), episode_id))
    
    # Settings operations
    def get_setting(self, key: str, default: Any = None) -> Any:
        with self.get_connection() as conn:
            row = conn.execute('SELECT value FROM user_settings WHERE key = ?', (key,)).fetchone()
            if row:
                # Try to parse as JSON for complex values
                import json
                try:
                    return json.loads(row['value'])
                except (json.JSONDecodeError, TypeError):
                    return row['value']
            return default
    
    def set_setting(self, key: str, value: Any):
        import json
        if not isinstance(value, str):
            value = json.dumps(value)
        
        with self.get_connection() as conn:
            conn.execute('''
                INSERT OR REPLACE INTO user_settings (key, value)
                VALUES (?, ?)
            ''', (key, value))
    
    # Helper methods
    def _row_to_anime(self, row) -> Anime:
        return Anime(
            id=row['id'],
            name=row['name'],
            path=row['path'],
            cover_path=row['cover_path'],
            description=row['description'],
            year=row['year'],
            rating=row['rating'] or 0.0,
            status=row['status'],
            mal_id=row['mal_id'],
            total_episodes=row['total_episodes'] or 0,
            date_added=datetime.fromisoformat(row['date_added']) if row['date_added'] else None,
            last_watched=datetime.fromisoformat(row['last_watched']) if row['last_watched'] else None,
            is_favorite=bool(row['is_favorite'])
        )
    
    def _row_to_episode(self, row) -> Episode:
        return Episode(
            id=row['id'],
            anime_id=row['anime_id'],
            episode_number=row['episode_number'],
            title=row['title'],
            file_path=row['file_path'],
            duration=row['duration'] or 0,
            thumbnail_path=row['thumbnail_path'],
            date_added=datetime.fromisoformat(row['date_added']) if row['date_added'] else None,
            progress_seconds=row['progress_seconds'] or 0,
            is_watched=bool(row['is_watched']) if row['is_watched'] is not None else False,
            last_watched=datetime.fromisoformat(row['last_watched']) if row['last_watched'] else None
        )
    
    def _get_default_schema(self) -> str:
        # Fallback schema if file doesn't exist
        return '''
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
        '''