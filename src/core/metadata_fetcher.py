from PySide6.QtCore import QThread, Signal
from src.core.anilist_api import AnilistAPI
from src.core.database_manager import DatabaseManager
import os

class MetadataFetcher(QThread):
    """
    A background thread to fetch metadata and covers from Anilist.
    """
    finished = Signal() # Signal emitted when all fetching is complete
    metadata_updated = Signal(str) # Signal emitted when a single anime's metadata is updated

    def __init__(self, db_path: str, anime_titles: list, parent=None):
        super().__init__(parent)
        self.db_path = db_path
        self.anime_titles = anime_titles
        self.anilist_api = AnilistAPI()

    def run(self):
        """The main work of the thread."""
        # Create a new DatabaseManager instance for this thread
        db_manager = DatabaseManager(self.db_path)
        
        print(f"Starting metadata fetch for {len(self.anime_titles)} titles...")
        for title in self.anime_titles:
            # First, check if a cover path already exists in the database for this title
            existing_cover_in_db = db_manager.get_cover_path_for_title(title)
            if existing_cover_in_db:
                print(f"Cover path for '{title}' already in DB: {existing_cover_in_db}. Skipping fetch.")
                continue

            # If not in DB, then check if the file exists on disk (e.g., from a previous manual placement)
            cover_path = os.path.join("covers", f"{title}.jpg")
            if os.path.exists(cover_path):
                print(f"Cover file for '{title}' exists on disk. Updating DB with this path.")
                db_manager.update_cover_path(title, cover_path)
                self.metadata_updated.emit(title)
                continue

            print(f"Fetching metadata for '{title}'...")
            metadata = self.anilist_api.fetch_anime_metadata(title)

            if metadata and metadata.get('coverImage', {}).get('extraLarge'):
                cover_url = metadata['coverImage']['extraLarge']
                description = metadata.get('description', 'No description available.')
                genres = metadata.get('genres', [])
                
                # Download the cover
                if self.anilist_api.download_cover(cover_url, cover_path):
                    # Update the database with all the new metadata
                    db_manager.update_series_metadata(title, cover_path, description, genres)
                    self.metadata_updated.emit(title)
        
        print("Metadata fetch complete.")
        db_manager.close() # Close the database connection for this thread
        self.finished.emit()
