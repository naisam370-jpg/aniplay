import sys
from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout, QHBoxLayout, QStackedWidget

from src.widgets.player_control_widget import PlayerControlWidget
from src.widgets.episode_list_widget import EpisodeListWidget
from src.widgets.sidebar_widget import SidebarWidget
from src.widgets.anime_grid_widget import AnimeGridWidget
from src.widgets.search_widget import SearchWidget
from src.widgets.settings_widget import SettingsWidget
from src.widgets.anime_detail_view import AnimeDetailView # Import new widget
from src.core.database_manager import DatabaseManager
from src.core.library_scanner import load_library_from_db, group_episodes_by_anime, scan_library
from src.core.mpv_player import MpvPlayer
from src.core.metadata_fetcher import MetadataFetcher
from src.core.settings_manager import SettingsManager

class AniPlayWindow(QMainWindow):
    def __init__(self, db_manager, mpv_player, settings_manager):
        super().__init__()
        self.db_manager = db_manager
        self.mpv_player = mpv_player
        self.settings_manager = settings_manager
        self.metadata_fetcher = None
        self.setWindowTitle("AniPlay")
        self.setGeometry(100, 100, 1200, 700)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)

        self.sidebar = SidebarWidget()
        content_layout.addWidget(self.sidebar)

        self.stacked_widget = QStackedWidget()
        content_layout.addWidget(self.stacked_widget)

        # --- Create Views ---
        self.anime_grid = AnimeGridWidget()
        self.anime_detail_view = AnimeDetailView() # Instantiate new widget
        self.search_view = SearchWidget(self.db_manager, self.mpv_player)
        self.settings_view = SettingsWidget(self.db_manager, self.settings_manager)
        self.episode_list_view = EpisodeListWidget(self.db_manager, self.mpv_player)

        # --- Add Views to Stacked Widget ---
        self.stacked_widget.addWidget(self.anime_grid)
        self.stacked_widget.addWidget(self.anime_detail_view) # Add new widget
        self.stacked_widget.addWidget(self.episode_list_view)
        self.stacked_widget.addWidget(self.search_view)
        self.stacked_widget.addWidget(self.settings_view)

        main_layout.addLayout(content_layout)

        self.player_controls = PlayerControlWidget(self.mpv_player)
        self.player_controls.hide()
        main_layout.addWidget(self.player_controls)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # --- Connect Signals ---
        self.sidebar.btn_library.clicked.connect(self.show_anime_grid)
        self.sidebar.btn_search.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.search_view))
        self.sidebar.btn_settings.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.settings_view))

        self.settings_view.scan_requested.connect(self.trigger_scan)
        self.anime_grid.series_selected.connect(self.show_anime_detail) # Connect to new method
        self.anime_detail_view.sub_series_or_episode_selected.connect(self.handle_anime_detail_selection) # New connection
        self.anime_detail_view.back_to_anime_grid.connect(self.show_anime_grid) # New connection
        self.episode_list_view.back_requested.connect(self.show_anime_grid) # Default back to anime grid
        self.episode_list_view.video_playing.connect(self.on_video_playing)
        self.search_view.video_playing.connect(self.on_video_playing)

        # --- Initial Load ---
        self.load_and_display_library()
        
        if self.settings_manager.get("auto_scan", False):
            self.trigger_scan()

    def trigger_scan(self):
        library_path = self.settings_manager.get("library_path")
        if library_path:
            print(f"Starting scan of '{library_path}'...")
            video_files = scan_library(library_path, self.db_manager)
            self.on_scan_completed(video_files)
        else:
            print("Scan triggered, but no library path is set.")

    def load_and_display_library(self):
        all_episodes = load_library_from_db(self.db_manager)
        grouped_anime = group_episodes_by_anime(all_episodes)
        self.anime_grid.update_grid(grouped_anime)

    def on_scan_completed(self, video_files):
        self.load_and_display_library()
        self.search_view.refresh_cache()
        
        # Collect unique main anime titles for metadata fetching
        unique_main_anime_titles = {item['title'] for item in video_files}
        
        if unique_main_anime_titles:
            self.metadata_fetcher = MetadataFetcher(self.db_manager.db_path, list(unique_main_anime_titles))
            self.metadata_fetcher.metadata_updated.connect(self.on_metadata_updated)
            self.metadata_fetcher.finished.connect(self._metadata_fetcher_finished) # Connect finished signal
            self.metadata_fetcher.start()

    def _metadata_fetcher_finished(self):
        """Slot to handle cleanup when metadata fetcher thread finishes."""
        print("Metadata fetcher thread finished.")
        if self.metadata_fetcher:
            self.metadata_fetcher.deleteLater()
            self.metadata_fetcher = None # Clear reference


    def on_metadata_updated(self, title):
        print(f"UI: Metadata updated for {title}, reloading library.")
        self.load_and_display_library()

    def show_anime_grid(self):
        self.load_and_display_library()
        self.stacked_widget.setCurrentWidget(self.anime_grid)

    def show_anime_detail(self, anime_data):
        """
        Shows the AnimeDetailView for a selected main anime.
        """
        self.current_main_anime_data = anime_data # Store for back button context
        main_anime_cover_path = self.db_manager.get_cover_path_for_title(anime_data["title"])
        anime_metadata = self.db_manager.get_anime_metadata(anime_data["title"])
        description = anime_metadata["description"] if anime_metadata else "No description available."
        genres = ", ".join(anime_metadata["genres"]) if anime_metadata and anime_metadata["genres"] else "N/A"
        self.anime_detail_view.update_view(anime_data, main_anime_cover_path, description, genres)
        self.stacked_widget.setCurrentWidget(self.anime_detail_view)
        # Ensure back button for episode_list_view goes to anime_detail_view
        self.episode_list_view.back_requested.disconnect()
        self.episode_list_view.back_requested.connect(lambda: self.stacked_widget.setCurrentWidget(self.anime_detail_view))

    def handle_anime_detail_selection(self, selected_data):
        """
        Handles selection from AnimeDetailView (either a sub-series or a direct episode).
        """
        if "episodes" in selected_data: # It's a sub-series or a main anime's direct episodes
            self.episode_list_view.populate_episodes(selected_data)
            self.stacked_widget.setCurrentWidget(self.episode_list_view)
        elif "file_path" in selected_data: # It's a direct episode from AnimeDetailView
            self.mpv_player.play_video(selected_data["file_path"]) # Initiate playback
            self.on_video_playing(selected_data)


    def on_video_playing(self, anime_data):
        """Shows the player controls when a video starts playing."""
        self.player_controls.update_info(anime_data)
        self.player_controls.show()

    def closeEvent(self, event):
        """Ensures background threads are terminated before the application exits."""
        if self.metadata_fetcher and self.metadata_fetcher.isRunning():
            print("Terminating metadata fetcher thread...")
            self.metadata_fetcher.quit()
            self.metadata_fetcher.wait() # Wait for the thread to finish
        super().closeEvent(event)

def main():
    """Main function to run the application."""
    app = QApplication(sys.argv)
    
    db_path = "aniplay.db"
    settings_path = "settings.json"
    
    db_manager = DatabaseManager(db_path)
    settings_manager = SettingsManager(settings_path)
    
    mpv_player = MpvPlayer()
    
    main_win = AniPlayWindow(db_manager, mpv_player, settings_manager)
    
    # Load and apply stylesheet
    try:
        with open("src/styles/dark_theme.qss", "r") as f:
            main_win.setStyleSheet(f.read())
    except FileNotFoundError:
        print("Stylesheet not found, using default style.")

    main_win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()


