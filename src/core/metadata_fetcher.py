import re
from PySide6.QtCore import QThread, Signal
from src.core.jikan_api import search_anime, get_anime_details
from src.core.database_manager import DatabaseManager
import os
import requests

def download_cover(url, save_path):
    """Downloads a cover image from a URL."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error downloading cover from {url}: {e}")
        return False

class MetadataFetcher(QThread):
    """
    A background thread to fetch metadata and covers from Jikan API.
    """
    finished = Signal()
    metadata_updated = Signal(str)

    def __init__(self, db_path: str, parent=None):
        super().__init__(parent)
        self.db_path = db_path

    def run(self):
        """The main work of the thread."""
        db_manager = DatabaseManager(self.db_path)
        series_to_fetch = db_manager.get_series_without_metadata()

        print(f"Starting metadata fetch for {len(series_to_fetch)} series.")
        for series in series_to_fetch:
            title = series['title']
            print(f"Fetching metadata for: '{title}'...")

            search_result = search_anime(title)
            if not search_result:
                print(f"No search results for '{title}' on Jikan.")
                continue

            mal_id = search_result['mal_id']
            details = get_anime_details(mal_id)

            if details:
                anidb_url_match = next((item['url'] for item in details.get('external', []) if item['name'] == 'AniDB' and 'url' in item), None)
                anidb_id = None
                if anidb_url_match:
                    match = re.search(r'aid=(\d+)', anidb_url_match)
                    if match:
                        anidb_id = int(match.group(1))
                description = details.get('synopsis', 'No description available.')
                genres = [genre['name'] for genre in details.get('genres', [])]
                cover_url = details.get('images', {}).get('jpg', {}).get('large_image_url')

                cover_path = None
                if cover_url:
                    sanitized_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    cover_path = os.path.join("covers", f"{sanitized_title}.jpg")
                    if not os.path.exists(cover_path):
                        print(f"Downloading cover for '{title}' to '{cover_path}'")
                        download_success = download_cover(cover_url, cover_path)
                        if not download_success:
                            cover_path = None # Don't save path if download failed
                    else:
                        print(f"Cover for '{title}' already exists at '{cover_path}'.")

                db_manager.update_series_metadata(
                    series_id=series['id'],
                    mal_id=mal_id,
                    anidb_id=anidb_id,
                    cover_path=cover_path,
                    description=description,
                    genres=genres
                )
                print(f"Successfully updated metadata for '{title}'.")
                self.metadata_updated.emit(title)
            else:
                print(f"Could not fetch details for '{title}' (MAL ID: {mal_id}).")

        print("Metadata fetch complete.")
        db_manager.close()
        self.finished.emit()
