import os
import xxhash
from pathlib import Path
from PySide6.QtCore import QRunnable, QObject, Signal, Slot

from .parser import EpisodeParser
from .thumbnails import ThumbnailManager
from .api import JikanAPI  # Import the API


class ScannerSignals(QObject):
    progress = Signal(str)
    found_anime = Signal(str)
    finished = Signal(int)


class ScannerWorker(QRunnable):
    def __init__(self, root_path, db_manager):
        super().__init__()
        self.root_path = Path(root_path)
        self.db = db_manager
        self.signals = ScannerSignals()
        self.parser = EpisodeParser()
        self.thumb_manager = ThumbnailManager()
        self.api = JikanAPI()  # Initialize API
        self.video_extensions = ('.mkv', '.mp4', '.avi', '.mov')

    def generate_hash(self, file_path):
        try:
            with open(file_path, "rb") as f:
                return xxhash.xxh64(f.read(1024 * 1024)).hexdigest()
        except Exception:
            return None

    def find_cover(self, folder_path):
        folder = Path(folder_path)
        for name in ['cover.jpg', 'poster.jpg', 'folder.jpg', 'cover.png']:
            potential_path = folder / name
            if potential_path.exists():
                return str(potential_path)
        return None

    @Slot()
    def run(self):
        total_indexed = 0

        for root, dirs, files in os.walk(self.root_path):
            if 'extras' in root.lower():
                continue

            relative_path = Path(root).relative_to(self.root_path)
            if str(relative_path) == ".":
                continue

            anime_title = relative_path.parts[0]
            anime_root_folder = str(self.root_path / anime_title)

            # Check for cover.jpg
            cover_path = None
            if len(relative_path.parts) == 1:
                cover_path = self.find_cover(root)

            # 1. Ensure Anime exists in DB
            anime_id = self.db.get_or_create_anime(
                title=anime_title,
                path=anime_root_folder,
                poster=cover_path
            )
            self.signals.found_anime.emit(anime_title)

            # 2. Fetch Metadata if it doesn't exist yet
            existing_data = self.db.get_anime_details(anime_id)
            if existing_data and existing_data[4] is None:  # mal_id is at index 4
                self.signals.progress.emit(f"Fetching metadata for: {anime_title}")
                metadata = self.api.search_anime(anime_title)
                if metadata:
                    self.db.update_anime_metadata(
                        anime_id,
                        metadata['mal_id'],
                        metadata['rating'],
                        metadata['synopsis'],
                        metadata['genres']
                    )

            # 3. Process Episodes
            for file in files:
                if file.lower().endswith(self.video_extensions):
                    full_path = os.path.join(root, file)
                    self.signals.progress.emit(f"Processing: {file}")

                    season, episode = self.parser.parse_path(full_path)
                    file_hash = self.generate_hash(full_path)
                    thumb_path = self.thumb_manager.generate_for_episode(full_path, file_hash)

                    self.db.add_episode(
                        anime_id=anime_id,
                        file_path=full_path,
                        season=season,
                        episode=episode,
                        file_hash=file_hash,
                        thumbnail_path=thumb_path
                    )
                    total_indexed += 1

        self.signals.finished.emit(total_indexed)