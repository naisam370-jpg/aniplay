from PySide6.QtCore import QThread, Signal
from src.core.anilist_api import AnilistAPI
from src.core.database_manager import DatabaseManager
import os
from collections import defaultdict # Import defaultdict

class MetadataFetcher(QThread):
    """
    A background thread to fetch metadata and covers from Anilist.
    """
    finished = Signal() # Signal emitted when all fetching is complete
    metadata_updated = Signal(str) # Signal emitted when a single anime's metadata is updated

    def __init__(self, db_path: str, series_titles: list, parent=None):
        super().__init__(parent)
        self.db_path = db_path
        self.series_titles = series_titles
        self.anilist_api = AnilistAPI()

    def run(self):
        """The main work of the thread."""
        db_manager = DatabaseManager(self.db_path)
        
        # Since series_titles are now cleaned, each title is its own base anime title for fetching
        base_anime_to_series_map = defaultdict(list)
        for series_title in self.series_titles:
            base_anime_to_series_map[series_title].append(series_title)

        fetched_base_anime_metadata = {} # Cache to avoid re-fetching for the same base anime

        print(f"Starting metadata fetch for {len(self.series_titles)} series titles...")
        for base_anime_title, derived_series_titles in base_anime_to_series_map.items(): # base_anime_title is now the cleaned series_title
            if base_anime_title in fetched_base_anime_metadata:
                metadata = fetched_base_anime_metadata[base_anime_title]
                print(f"Using cached metadata for '{base_anime_title}'.")
            else:
                print(f"Fetching metadata for base anime: '{base_anime_title}'...")
                metadata = self.anilist_api.fetch_anime_metadata(base_anime_title)
                print(f"Metadata for '{base_anime_title}': {'Found' if metadata else 'Not Found'}")
                fetched_base_anime_metadata[base_anime_title] = metadata

            if metadata and metadata.get('coverImage', {}).get('extraLarge'):
                cover_url = metadata['coverImage']['extraLarge']
                description = metadata.get('description', 'No description available.')
                genres = metadata.get('genres', [])
                print(f"Cover URL: {cover_url}, Description: {description[:50]}..., Genres: {genres}")
                
                # Apply this metadata to all derived series titles
                for series_title in derived_series_titles:
                    # Check if cover already exists for this specific series_title
                    existing_cover_in_db = db_manager.get_cover_path_for_title(series_title)
                    print(f"Checking existing cover for '{series_title}': {existing_cover_in_db}")
                    if existing_cover_in_db:
                        print(f"Cover path for '{series_title}' already in DB: {existing_cover_in_db}. Skipping download.")
                        # Still update metadata if description/genres might be missing
                        update_success = db_manager.update_series_metadata(series_title, existing_cover_in_db, description, genres)
                        print(f"Updated metadata for '{series_title}' in DB (existing cover): {update_success}")
                        self.metadata_updated.emit(series_title)
                        continue

                    cover_path = os.path.join("covers", f"{series_title}.jpg")
                    # Download the cover
                    download_success = self.anilist_api.download_cover(cover_url, cover_path)
                    print(f"Downloaded cover for '{series_title}' to '{cover_path}': {download_success}")
                    if download_success:
                        # Update the database with all the new metadata for this specific series_title
                        update_success = db_manager.update_series_metadata(series_title, cover_path, description, genres)
                        print(f"Updated metadata for '{series_title}' in DB (new cover): {update_success}")
                        self.metadata_updated.emit(series_title)
                    else:
                        print(f"Failed to download cover for '{series_title}'.")
            else:
                for series_title in derived_series_titles:
                    print(f"Could not fetch metadata for '{base_anime_title}' (for series '{series_title}'). No cover or metadata found.")
        
        print("Metadata fetch complete.")
        db_manager.close() # Close the database connection for this thread
        self.finished.emit()
