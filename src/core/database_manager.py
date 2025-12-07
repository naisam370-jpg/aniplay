import sqlite3
import os

class DatabaseManager:
    def __init__(self, db_path="aniplay.db"):
        self.db_path = db_path
        self.conn = None
        self.connect()
        self.create_tables()
        self.migrate_data()

    def connect(self):
        """Establishes a connection to the SQLite database."""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row

    def close(self):
        """Closes the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def create_tables(self):
        """Creates the database tables if they don't exist."""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS anime_series (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT UNIQUE NOT NULL,
                mal_id INTEGER,
                anidb_id INTEGER,
                cover_path TEXT,
                description TEXT,
                genres TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS anime_episodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                series_id INTEGER NOT NULL,
                file_path TEXT UNIQUE NOT NULL,
                episode INTEGER,
                season INTEGER DEFAULT 1,
                sub_series_title TEXT,
                last_watched TEXT,
                is_watched INTEGER DEFAULT 0,
                FOREIGN KEY (series_id) REFERENCES anime_series (id)
            )
        """)
        self.conn.commit()

    def migrate_data(self):
        """Migrates data from the old table structure to the new one."""
        cursor = self.conn.cursor()
        cursor.execute("PRAGMA table_info(anime_episodes)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'title' in columns: # Old structure detected
            print("Old database structure detected. Migrating data...")
            cursor.execute("SELECT DISTINCT title FROM anime_episodes")
            series_titles = cursor.fetchall()

            for row in series_titles:
                title = row['title']
                cursor.execute("SELECT cover_path, description, genres FROM anime_episodes WHERE title = ? LIMIT 1", (title,))
                meta_row = cursor.fetchone()
                
                cursor.execute("INSERT OR IGNORE INTO anime_series (title, cover_path, description, genres) VALUES (?, ?, ?, ?)",
                               (title, meta_row['cover_path'], meta_row['description'], meta_row['genres']))
                self.conn.commit()
                
                cursor.execute("SELECT id FROM anime_series WHERE title = ?", (title,))
                series_id = cursor.fetchone()['id']

                cursor.execute("UPDATE anime_episodes SET series_id = ? WHERE title = ?", (series_id, title))

            # Create a new table without the old columns
            cursor.execute("""
                CREATE TABLE anime_episodes_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    series_id INTEGER NOT NULL,
                    file_path TEXT UNIQUE NOT NULL,
                    episode INTEGER,
                    season INTEGER DEFAULT 1,
                    sub_series_title TEXT,
                    last_watched TEXT,
                    is_watched INTEGER DEFAULT 0,
                    FOREIGN KEY (series_id) REFERENCES anime_series (id)
                )
            """)
            cursor.execute("""
                INSERT INTO anime_episodes_new (id, series_id, file_path, episode, season, sub_series_title, last_watched, is_watched)
                SELECT id, series_id, file_path, episode, season, sub_series_title, last_watched, is_watched FROM anime_episodes
            """)
            cursor.execute("DROP TABLE anime_episodes")
            cursor.execute("ALTER TABLE anime_episodes_new RENAME TO anime_episodes")
            self.conn.commit()
            print("Data migration completed.")

    def add_or_get_series(self, title, mal_id=None, anidb_id=None):
        """Adds a new anime series or retrieves it if it exists."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM anime_series WHERE title = ?", (title,))
        row = cursor.fetchone()
        if row:
            return row['id']
        else:
            cursor.execute("INSERT INTO anime_series (title, mal_id, anidb_id) VALUES (?, ?, ?)", (title, mal_id, anidb_id))
            self.conn.commit()
            return cursor.lastrowid

    def add_episode(self, series_id, file_path, episode=None, season=1, sub_series_title=None):
        """Adds a new anime episode."""
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO anime_episodes (series_id, file_path, episode, season, sub_series_title)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(file_path) DO UPDATE SET
                    episode = EXCLUDED.episode,
                    season = EXCLUDED.season,
                    sub_series_title = EXCLUDED.sub_series_title
            """, (series_id, file_path, episode, season, sub_series_title))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error adding/updating episode: {e}")
            return False

    def update_series_metadata(self, series_id, mal_id, anidb_id, cover_path, description, genres):
        """Updates the metadata for an anime series."""
        cursor = self.conn.cursor()
        try:
            genres_str = ", ".join(genres) if genres else ""
            cursor.execute("""
                UPDATE anime_series
                SET mal_id = ?, anidb_id = ?, cover_path = ?, description = ?, genres = ?
                WHERE id = ?
            """, (mal_id, anidb_id, cover_path, description, genres_str, series_id))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error updating series metadata: {e}")
            return False

    def get_all_episodes_with_series_info(self):
        """Retrieves all episodes with their series info."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT
                s.title,
                s.cover_path,
                s.description,
                s.genres,
                e.file_path,
                e.episode,
                e.season,
                e.sub_series_title
            FROM anime_episodes e
            JOIN anime_series s ON e.series_id = s.id
            ORDER BY s.title, e.sub_series_title, e.season, e.episode
        """)
        return [dict(row) for row in cursor.fetchall()]

    def get_series_by_title(self, title):
        """Retrieves a series by its title."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM anime_series WHERE title = ?", (title,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_cover_path_for_title(self, title):
        series = self.get_series_by_title(title)
        return series['cover_path'] if series else None
        
    def get_anime_metadata(self, title):
        series = self.get_series_by_title(title)
        if series:
            genres_str = series['genres']
            genres_list = [g.strip() for g in genres_str.split(',')] if genres_str else []
            return {
                "description": series['description'],
                "genres": genres_list
            }
        return None
        
    def search_episodes(self, query):
        """
        Searches for episodes with titles matching the query.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT
                s.title,
                e.file_path,
                e.episode
            FROM anime_episodes e
            JOIN anime_series s ON e.series_id = s.id
            WHERE s.title LIKE ?
            ORDER BY s.title, e.season, e.episode
        """, (f'%{query}%',))
        return [dict(row) for row in cursor.fetchall()]

    def get_series_without_metadata(self):
        """Gets all series that don't have metadata."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM anime_series WHERE description IS NULL OR cover_path IS NULL")
        return [dict(row) for row in cursor.fetchall()]

if __name__ == '__main__':
    # Example Usage and Migration Test
    DB_FILE = "test_aniplay.db"
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)

    # 1. Create Old Structure and add data
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS anime_episodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            episode INTEGER,
            cover_path TEXT,
            description TEXT,
            genres TEXT
        )
    """)
    cursor.execute("INSERT INTO anime_episodes (file_path, title, episode, cover_path, description, genres) VALUES (?, ?, ?, ?, ?, ?)",
                   ("/path/to/a1.mkv", "Series A", 1, "cover_a.jpg", "Desc A", "Action, Sci-Fi"))
    cursor.execute("INSERT INTO anime_episodes (file_path, title, episode) VALUES (?, ?, ?)",
                   ("/path/to/a2.mkv", "Series A", 2))
    cursor.execute("INSERT INTO anime_episodes (file_path, title, episode, cover_path, description, genres) VALUES (?, ?, ?, ?, ?, ?)",
                   ("/path/to/b1.mkv", "Series B", 1, "cover_b.jpg", "Desc B", "Comedy"))
    conn.commit()
    conn.close()

    print("--- OLD STRUCTURE DATA ---")
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM anime_episodes")
    for r in cursor.fetchall():
        print(dict(r))
    conn.close()


    # 2. Instantiate DatabaseManager to trigger migration
    print("\n--- MIGRATING ---")
    db_manager = DatabaseManager(DB_FILE)
    print("--- MIGRATION COMPLETE ---")


    # 3. Verify new structure and data
    print("\n--- NEW STRUCTURE DATA ---")
    print("\nSERIES TABLE:")
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM anime_series")
    for r in cursor.fetchall():
        print(dict(r))

    print("\nEPISODES TABLE:")
    cursor.execute("SELECT * FROM anime_episodes")
    for r in cursor.fetchall():
        print(dict(r))

    print("\nALL EPISODES WITH SERIES INFO:")
    for item in db_manager.get_all_episodes_with_series_info():
        print(item)

    # 4. Test new functionality
    print("\n--- TESTING NEW FUNCTIONS ---")
    series_c_id = db_manager.add_or_get_series("Series C")
    db_manager.add_episode(series_c_id, "/path/to/c1.mkv", 1)
    print("Added Series C")

    db_manager.update_series_metadata(series_c_id, 12345, 6789, "cover_c.jpg", "Desc C", ["Slice of Life"])
    print("Updated metadata for Series C")
    
    print("\nALL EPISODES WITH SERIES INFO (after adds):")
    for item in db_manager.get_all_episodes_with_series_info():
        print(item)

    db_manager.close()
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)

