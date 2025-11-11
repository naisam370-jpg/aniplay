import sqlite3
import os

class DatabaseManager:
    def __init__(self, db_path="aniplay.db"):
        self.db_path = db_path
        self.conn = None
        self.connect()
        self.create_table()

    def connect(self):
        """Establishes a connection to the SQLite database."""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row # Access columns by name
        return self.conn

    def close(self):
        """Closes the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def create_table(self):
        """Creates the 'anime_episodes' table if it doesn't exist and adds missing columns."""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS anime_episodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                episode INTEGER,
                cover_path TEXT,
                description TEXT,
                genres TEXT,
                last_watched TEXT,
                is_watched INTEGER DEFAULT 0,
                season INTEGER DEFAULT 1,
                sub_series_title TEXT -- New column for sub-series title
            )
        """)
        
        # Check and add 'season' column if missing (for backward compatibility)
        cursor.execute("PRAGMA table_info(anime_episodes)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'season' not in columns:
            cursor.execute("ALTER TABLE anime_episodes ADD COLUMN season INTEGER DEFAULT 1")
        if 'sub_series_title' not in columns:
            cursor.execute("ALTER TABLE anime_episodes ADD COLUMN sub_series_title TEXT")
        
        self.conn.commit()

    def add_episode(self, file_path, title, episode=None, season=1, sub_series_title=None, cover_path=None):
        """
        Adds a new anime episode to the database.
        If an episode with the same file_path already exists, it updates its data.
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO anime_episodes (file_path, title, episode, season, sub_series_title, cover_path)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(file_path) DO UPDATE SET
                    title = EXCLUDED.title,
                    episode = EXCLUDED.episode,
                    season = EXCLUDED.season,
                    sub_series_title = EXCLUDED.sub_series_title,
                    cover_path = COALESCE(EXCLUDED.cover_path, cover_path)
            """, (file_path, title, episode, season, sub_series_title, cover_path))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error adding/updating episode: {e}")
            return False

    def update_series_metadata(self, title, cover_path, description, genres):
        """Updates the metadata for all episodes with a matching title."""
        cursor = self.conn.cursor()
        try:
            # Convert genres list to a comma-separated string for storage
            genres_str = ", ".join(genres) if genres else ""
            cursor.execute("""
                UPDATE anime_episodes 
                SET cover_path = ?, description = ?, genres = ? 
                WHERE title = ?
            """, (cover_path, description, genres_str, title))
            self.conn.commit()
            print(f"Updated metadata for '{title}'")
            return True
        except sqlite3.Error as e:
            print(f"Error updating metadata for '{title}': {e}")
            return False

    def clear_all_cover_paths(self, title=None):
        """
        Sets the cover_path to NULL for all episodes in the database.
        If a title is provided, clears covers only for that series.
        """
        cursor = self.conn.cursor()
        try:
            if title:
                cursor.execute("UPDATE anime_episodes SET cover_path = NULL WHERE title = ?", (title,))
                print(f"Cleared cover paths for '{title}' in the database.")
            else:
                cursor.execute("UPDATE anime_episodes SET cover_path = NULL")
                print("Cleared all cover paths in the database.")
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error clearing cover paths: {e}")
            return False

    def get_all_episodes(self):
        """Retrieves all anime episodes from the database."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM anime_episodes ORDER BY title, sub_series_title, season, episode")
        return [dict(row) for row in cursor.fetchall()]

    def get_cover_path_for_title(self, title, sub_series_title=None):
        """
        Retrieves the cover_path for a given anime title and optional sub_series_title from the database.
        Returns the cover_path if found, otherwise None.
        """
        cursor = self.conn.cursor()
        if sub_series_title:
            cursor.execute("SELECT cover_path FROM anime_episodes WHERE title = ? AND sub_series_title = ? AND cover_path IS NOT NULL LIMIT 1", (title, sub_series_title))
        else:
            cursor.execute("SELECT cover_path FROM anime_episodes WHERE title = ? AND sub_series_title IS NULL AND cover_path IS NOT NULL LIMIT 1", (title,))
        result = cursor.fetchone()
        return result['cover_path'] if result else None

    def search_episodes(self, query):
        """
        Searches for episodes with titles matching the query.
        The search is case-insensitive.
        """
        cursor = self.conn.cursor()
        # Use a LIKE query with wildcards to search for the query string within the title
        cursor.execute("SELECT * FROM anime_episodes WHERE title LIKE ? ORDER BY title, season, episode", (f'%{query}%',))
        return [dict(row) for row in cursor.fetchall()]

    def get_episode_by_path(self, file_path):
        """Retrieves an episode by its file path."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM anime_episodes WHERE file_path = ?", (file_path,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def delete_episode(self, file_path):
        """Deletes an episode from the database by its file path."""
        cursor = self.conn.cursor()
        try:
            cursor.execute("DELETE FROM anime_episodes WHERE file_path = ?", (file_path,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error deleting episode: {e}")
            return False

    def update_watched_status(self, file_path, is_watched):
        """Updates the watched status of an episode."""
        cursor = self.conn.cursor()
        try:
            cursor.execute("UPDATE anime_episodes SET is_watched = ? WHERE file_path = ?", (1 if is_watched else 0, file_path))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error updating watched status: {e}")
            return False

if __name__ == '__main__':
    # Example Usage
    db_manager = DatabaseManager("test_aniplay.db")

    # Add some episodes
    db_manager.add_episode("/path/to/anime/Series A - S01E01.mkv", "Series A", 1, 1)
    db_manager.add_episode("/path/to/anime/Series A - S01E02.mkv", "Series A", 2, 1)
    db_manager.add_episode("/path/to/anime/Series A - S02E01.mkv", "Series A", 1, 2)
    db_manager.add_episode("/path/to/anime/Series B - 01.mp4", "Series B", 1) # Default season 1
    db_manager.add_episode("/path/to/anime/Series C - Movie.avi", "Series C")

    print("All episodes after adding:")
    for episode in db_manager.get_all_episodes():
        print(episode)

    # Update an episode
    db_manager.add_episode("/path/to/anime/Series A - S01E01.mkv", "Series A Updated", 1, 1)
    print("\nAll episodes after updating Series A - S01E01:")
    for episode in db_manager.get_all_episodes():
        print(episode)

    # Get a specific episode
    print("\nEpisode by path:")
    print(db_manager.get_episode_by_path("/path/to/anime/Series B - 01.mp4"))

    # Update watched status
    db_manager.update_watched_status("/path/to/anime/Series A - S01E01.mkv", True)
    print("\nSeries A - S01E01 watched status:")
    print(db_manager.get_episode_by_path("/path/to/anime/Series A - S01E01.mkv"))

    # Delete an episode
    db_manager.delete_episode("/path/to/anime/Series C - Movie.avi")
    print("\nAll episodes after deleting Series C - Movie:")
    for episode in db_manager.get_all_episodes():
        print(episode)

    db_manager.close()
    # Clean up test database
    if os.path.exists("test_aniplay.db"):
        os.remove("test_aniplay.db")
