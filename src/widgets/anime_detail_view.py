from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel, QScrollArea, QPushButton
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QPixmap, QFont
import os

class ContentCard(QWidget):
    clicked = Signal(dict) # Signal to emit when the card is clicked

    def __init__(self, item_data, main_anime_cover_path=None, parent=None):
        super().__init__(parent)
        self.item_data = item_data
        self.main_anime_cover_path = main_anime_cover_path
        self.setFixedSize(160, 250)
        self.setCursor(Qt.PointingHandCursor) # Indicate clickable

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        self.cover_label = QLabel()
        self.cover_label.setAlignment(Qt.AlignCenter)
        self.cover_label.setFixedSize(150, 200)
        self.cover_label.setStyleSheet("border: 1px solid #555; background-color: #3a3a3a;")
        
        display_title = "Unknown"
        display_text_extra = ""
        cover_to_load = None

        if "file_path" in item_data: # This is an episode
            episode_num = item_data.get("episode")
            display_title = f"Episode {episode_num}" if episode_num is not None else os.path.basename(item_data["file_path"])
            if item_data.get("is_watched"):
                display_text_extra = "(Watched)"
            cover_to_load = item_data.get("cover_path") or self.main_anime_cover_path
        elif "episodes" in item_data: # This is a sub-series
            display_title = item_data.get("title", "Unknown Sub-series")
            total_episodes = len(item_data["episodes"])
            watched_count = sum(1 for ep in item_data["episodes"] if ep.get('is_watched'))
            display_text_extra = f"({watched_count}/{total_episodes} Watched)"
            # For sub-series, use the cover of the first episode if available, otherwise main anime cover
            for ep in item_data["episodes"]:
                if ep.get("cover_path"):
                    cover_to_load = ep.get("cover_path")
                    break
            if not cover_to_load:
                cover_to_load = self.main_anime_cover_path
        
        pixmap = QPixmap()
        if cover_to_load and os.path.exists(cover_to_load):
            pixmap.load(cover_to_load)

        if not pixmap.isNull():
            self.cover_label.setPixmap(pixmap.scaled(self.cover_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.cover_label.setText("No Cover")

        self.title_label = QLabel(f"{display_title}\n{display_text_extra}".strip())
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setWordWrap(True)
        self.title_label.setFont(QFont("Arial", 10))

        layout.addWidget(self.cover_label)
        layout.addWidget(self.title_label)

    def mousePressEvent(self, event):
        """Handles click events on the card."""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.item_data)
        super().mousePressEvent(event)

class AnimeDetailView(QScrollArea):
    sub_series_or_episode_selected = Signal(dict)
    back_to_anime_grid = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.content_widget = QWidget()
        self.setWidget(self.content_widget)

        self.main_layout = QVBoxLayout(self.content_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
        self.main_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.btn_back = QPushButton("← Back to Anime List")
        self.btn_back.clicked.connect(self.back_to_anime_grid.emit)
        self.btn_back.setFixedWidth(150)
        self.main_layout.addWidget(self.btn_back, alignment=Qt.AlignTop | Qt.AlignLeft)

        # Labels for description and genres
        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        self.description_label.setFont(QFont("Arial", 10))
        self.main_layout.addWidget(self.description_label)

        self.genres_label = QLabel()
        self.genres_label.setFont(QFont("Arial", 10, italic=True))
        self.main_layout.addWidget(self.genres_label)

        self.content_grid_layout = QGridLayout()
        self.content_grid_layout.setContentsMargins(0, 0, 0, 0)
        self.content_grid_layout.setSpacing(10)
        self.content_grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.main_layout.addLayout(self.content_grid_layout)
        self.main_layout.addStretch()

    def update_view(self, anime_data, main_anime_cover_path, description, genres):
        """
        Clears and repopulates the view with ContentCards for direct episodes and sub-series,
        and displays the anime's description and genres.
        """
        # Update description and genres
        self.description_label.setText(description)
        self.genres_label.setText(f"Genres: {genres}")

        # Clear existing items in the grid layout
        for i in reversed(range(self.content_grid_layout.count())):
            item = self.content_grid_layout.itemAt(i)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            self.content_grid_layout.removeItem(item)

        direct_episodes = anime_data.get("episodes", [])
        sub_series_list = anime_data.get("sub_series", [])

        all_items_to_display = []
        # Add direct episodes
        for episode in sorted(direct_episodes, key=lambda e: e.get('episode', 0) or 0):
            all_items_to_display.append(episode)
        
        # Add sub-series
        for sub_series_data in sub_series_list:
            all_items_to_display.append(sub_series_data)

        col = 0
        row = 0
        max_cols = 5

        if not all_items_to_display:
            empty_label = QLabel("No content found for this anime.")
            empty_label.setAlignment(Qt.AlignCenter)
            self.main_layout.addWidget(empty_label)
            return

        for item_data in all_items_to_display:
            card = ContentCard(item_data, main_anime_cover_path)
            card.clicked.connect(self.sub_series_or_episode_selected.emit)
            self.content_grid_layout.addWidget(card, row, col)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
