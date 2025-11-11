from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QScrollArea, QGridLayout
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from src.core.database_manager import DatabaseManager
from src.core.mpv_player import MpvPlayer
from rapidfuzz import process, fuzz
import os

class SearchWidget(QWidget):
    video_playing = Signal(dict)

    def __init__(self, db_manager: DatabaseManager, mpv_player: MpvPlayer, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.mpv_player = mpv_player
        self.all_episodes = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search your library (e.g., 'spy family')...")
        self.search_input.textChanged.connect(self.on_search_query_changed)
        layout.addWidget(self.search_input)

        self.results_scroll_area = QScrollArea()
        self.results_scroll_area.setWidgetResizable(True)
        self.results_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        layout.addWidget(self.results_scroll_area)

        self.scroll_content = QWidget()
        self.results_grid_layout = QGridLayout(self.scroll_content)
        self.results_grid_layout.setContentsMargins(10, 10, 10, 10)
        self.results_grid_layout.setSpacing(10)
        self.results_grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.results_scroll_area.setWidget(self.scroll_content)
        
        self.refresh_cache() # Initial cache load

    def refresh_cache(self):
        """Reloads the episode cache from the database."""
        print("Refreshing search cache...")
        self.all_episodes = self.db_manager.get_all_episodes()
        # Create a list of titles for rapidfuzz to search against
        self.episode_titles = [ep['title'] for ep in self.all_episodes]
        print(f"Cache refreshed with {len(self.all_episodes)} episodes.")

    def on_search_query_changed(self, query):
        """Triggers when the search input text changes."""
        if len(query) > 2:
            # Use rapidfuzz to find best matches
            matches = process.extract(query, self.episode_titles, scorer=fuzz.WRatio, limit=50, score_cutoff=50)
            
            # Get the full episode data for each match using the index
            results = [self.all_episodes[index] for (title, score, index) in matches]
            self.update_results(results)
        else:
            self.update_results([]) # Clear results if query is too short

    def update_results(self, results):
        """Clears and repopulates the results grid."""
        while self.results_grid_layout.count():
            item = self.results_grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if not results:
            return

        col = 0
        row = 0
        max_cols = 5

        for episode_data in results:
            card = self.create_result_card(episode_data)
            self.results_grid_layout.addWidget(card, row, col)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    def create_result_card(self, episode_data):
        """Creates a clickable card widget for a single search result."""
        card = QWidget()
        card.setFixedSize(160, 250) # Set a fixed size for the card
        card_layout = QVBoxLayout(card)
        
        cover_label = QLabel()
        cover_label.setStyleSheet("border: 1px solid #555; background-color: #3a3a3a;")
        cover_label.setFixedSize(150, 200)
        cover_label.setAlignment(Qt.AlignCenter)
        
        cover_path = episode_data.get("cover_path")

        pixmap = QPixmap()
        if cover_path and os.path.exists(cover_path):
            pixmap.load(cover_path)

        if not pixmap.isNull():
            cover_label.setPixmap(pixmap.scaled(cover_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            cover_label.setText("No Cover")
            
        title_text = episode_data.get("title", "Unknown")
        ep_num = episode_data.get("episode")
        if ep_num:
            title_text += f"\nEp {ep_num}"
            
        title_label = QLabel(title_text)
        title_label.setWordWrap(True)
        title_label.setAlignment(Qt.AlignCenter)
        
        card_layout.addWidget(cover_label)
        card_layout.addWidget(title_label)
        
        card.mousePressEvent = lambda event: self.on_card_clicked(event, episode_data)
        
        return card

    def on_card_clicked(self, event, episode_data):
        if event.button() == Qt.LeftButton:
            file_path = episode_data.get("file_path")
            if file_path:
                self.mpv_player.play(file_path)
                self.video_playing.emit(episode_data)
