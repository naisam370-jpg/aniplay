from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QScrollArea, QHBoxLayout
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QFont
from src.core.database_manager import DatabaseManager
import os

class EpisodeRowWidget(QWidget):
    """A custom widget for a single row in the episode list."""
    play_requested = Signal(dict)
    watched_status_changed = Signal(dict)

    def __init__(self, episode_data, parent=None):
        super().__init__(parent)
        self.episode_data = episode_data
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0) # Adjust margins for episode rows
        
        title = episode_data.get('title', 'Unknown Title')
        episode_num = episode_data.get('episode')
        season_num = episode_data.get('season')

        display_text = ""
        if season_num is not None and episode_num is not None:
            display_text = f"S{season_num:02d}E{episode_num:02d}"
        elif episode_num is not None:
            display_text = f"Episode {episode_num}"
        else:
            display_text = title # Fallback to title if no episode info

        self.play_button = QPushButton(display_text)
        self.play_button.setStyleSheet("text-align: left; padding: 8px;")
        self.play_button.clicked.connect(lambda: self.play_requested.emit(self.episode_data))
        
        self.watched_button = QPushButton("Mark Watched")
        self.watched_button.setFixedWidth(120)
        self.watched_button.clicked.connect(lambda: self.watched_status_changed.emit(self.episode_data))
        
        layout.addWidget(self.play_button)
        layout.addWidget(self.watched_button)
        
        self.update_style()

    def update_style(self):
        """Updates the widget's style based on the watched status."""
        if self.episode_data.get('is_watched'):
            self.play_button.setStyleSheet("text-align: left; padding: 8px; color: #888; background-color: #333;")
            self.watched_button.setText("Mark Unwatched")
        else:
            self.play_button.setStyleSheet("text-align: left; padding: 8px;")
            self.watched_button.setText("Mark Watched")

class EpisodeListWidget(QWidget):
    back_requested = Signal()
    video_playing = Signal(dict)

    def __init__(self, db_manager: DatabaseManager, mpv_player, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.mpv_player = mpv_player
        self.anime_data = None

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        header_container_layout = QHBoxLayout()
        
        self.btn_back = QPushButton("← Back to Library")
        self.btn_back.clicked.connect(self.back_requested.emit)
        self.btn_back.setFixedWidth(150)
        header_container_layout.addWidget(self.btn_back, alignment=Qt.AlignTop)

        self.cover_label = QLabel()
        self.cover_label.setFixedSize(100, 150)
        self.cover_label.setAlignment(Qt.AlignCenter)
        self.cover_label.setStyleSheet("border: 1px solid #555; background-color: #3a3a3a;")
        header_container_layout.addWidget(self.cover_label, alignment=Qt.AlignTop)

        title_layout = QVBoxLayout()
        self.title_label = QLabel("Anime Title")
        font = self.title_label.font()
        font.setPointSize(18)
        font.setBold(True)
        self.title_label.setFont(font)
        title_layout.addWidget(self.title_label)

        self.genres_label = QLabel("Genres: N/A")
        self.genres_label.setWordWrap(True)
        title_layout.addWidget(self.genres_label)
        
        title_layout.addStretch()
        header_container_layout.addLayout(title_layout)
        
        main_layout.addLayout(header_container_layout)

        self.description_label = QLabel("Description will be shown here.")
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("padding: 5px;")
        main_layout.addWidget(self.description_label)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        main_layout.addWidget(scroll_area)

        self.scroll_content = QWidget()
        self.episodes_layout = QVBoxLayout(self.scroll_content)
        self.episodes_layout.setAlignment(Qt.AlignTop)
        scroll_area.setWidget(self.scroll_content)

    def populate_episodes(self, anime_series_data):
        self.anime_data = anime_series_data
        title = anime_series_data.get('title', 'Unknown Title')
        self.title_label.setText(title)

        # Clear existing items
        while self.episodes_layout.count():
            item = self.episodes_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # Get metadata from the first episode of the first season for display
        first_episode_in_first_season = None
        if anime_series_data.get("seasons"):
            first_season_episodes = anime_series_data["seasons"][0].get("episodes")
            if first_season_episodes:
                first_episode_in_first_season = first_season_episodes[0]

        description = first_episode_in_first_season.get("description", "No description available.") if first_episode_in_first_season else "No description available."
        genres = first_episode_in_first_season.get("genres", "N/A") if first_episode_in_first_season else "N/A"

        self.description_label.setText(description.replace('<br>', '') if description else "No description available.")
        self.genres_label.setText(f"Genres: {genres}")

        cover_path = first_episode_in_first_season.get("cover_path") if first_episode_in_first_season else None

        pixmap = QPixmap()
        if cover_path and os.path.exists(cover_path):
            pixmap.load(cover_path)

        if not pixmap.isNull():
            self.cover_label.setPixmap(pixmap.scaled(self.cover_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.cover_label.setText("No Cover")

        # Populate episodes grouped by season
        for season_data in anime_series_data.get('seasons', []):
            season_num = season_data.get('season_num')
            episodes_in_season = season_data.get('episodes', [])

            if season_num is not None:
                season_label = QLabel(f"Season {season_num}")
                season_label.setFont(QFont("Arial", 12, QFont.Bold))
                season_label.setStyleSheet("margin-top: 10px; margin-bottom: 5px;")
                self.episodes_layout.addWidget(season_label)

            for episode in episodes_in_season:
                row_widget = EpisodeRowWidget(episode)
                row_widget.play_requested.connect(self.on_episode_clicked)
                row_widget.watched_status_changed.connect(self.on_watched_status_changed)
                self.episodes_layout.addWidget(row_widget)

    def on_episode_clicked(self, episode_data):
        file_path = episode_data.get("file_path")
        if file_path:
            self.mpv_player.play_video(file_path)
            self.video_playing.emit(episode_data)

    def on_watched_status_changed(self, episode_data):
        """Toggles the watched status of an episode."""
        current_status = episode_data.get('is_watched', 0)
        new_status = not current_status
        
        file_path = episode_data.get('file_path')
        if file_path:
            self.db_manager.update_watched_status(file_path, new_status)
            # Update the local data and refresh the UI for this row
            episode_data['is_watched'] = int(new_status)
            # Find the widget and update its style
            for i in range(self.episodes_layout.count()):
                widget = self.episodes_layout.itemAt(i).widget()
                # Check if the item is an EpisodeRowWidget before accessing its episode_data
                if isinstance(widget, EpisodeRowWidget) and widget.episode_data['file_path'] == file_path:
                    widget.update_style()
                    break