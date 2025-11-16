import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel, QScrollArea
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QPixmap, QFont
from .ui_anime_grid_widget import Ui_AnimeGridWidget

class AnimeCard(QWidget):
    series_selected = Signal(dict) # Signal to emit when a series is selected

    def __init__(self, anime_series_data, parent=None):
        super().__init__(parent)
        self.anime_series_data = anime_series_data
        self.setFixedSize(160, 250)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        self.cover_label = QLabel()
        self.cover_label.setAlignment(Qt.AlignCenter)
        self.cover_label.setFixedSize(150, 200)
        self.cover_label.setStyleSheet("border: 1px solid #555; background-color: #3a3a3a;")
        
        cover_path = None
        total_episodes = 0
        watched_count = 0

        # Collect episodes from direct list
        for episode in anime_series_data.get("episodes", []):
            total_episodes += 1
            if episode.get('is_watched'):
                watched_count += 1
            if not cover_path and episode.get("cover_path"):
                cover_path = episode.get("cover_path")

        # Collect episodes from sub-series
        for sub_series_data in anime_series_data.get("sub_series", []):
            for episode in sub_series_data.get("episodes", []):
                total_episodes += 1
                if episode.get('is_watched'):
                    watched_count += 1
                if not cover_path and episode.get("cover_path"):
                    cover_path = episode.get("cover_path")
                    
        pixmap = QPixmap()
        if cover_path and os.path.exists(cover_path):
            pixmap.load(cover_path)

        if not pixmap.isNull():
            self.cover_label.setPixmap(pixmap.scaled(self.cover_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.cover_label.setText("No Cover")

        title = anime_series_data.get("title", "Unknown Title")
        
        display_text = f"{title}\n({watched_count}/{total_episodes} Watched)"

        self.title_label = QLabel(display_text)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setWordWrap(True)
        self.title_label.setFont(QFont("Arial", 10))

        layout.addWidget(self.cover_label)
        layout.addWidget(self.title_label)

    def mousePressEvent(self, event):
        """Handles click events on the anime card."""
        if event.button() == Qt.LeftButton:
            self.series_selected.emit(self.anime_series_data)
        super().mousePressEvent(event)

class AnimeGridWidget(QScrollArea, Ui_AnimeGridWidget):
    series_selected = Signal(dict) # Signal to bubble up from AnimeCard

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.update_grid([]) # Initially empty

    def update_grid(self, anime_series_list):
        """
        Clears and repopulates the grid with new anime cards based on a list of anime series.
        """
        # Clear existing items
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if not anime_series_list:
            empty_label = QLabel("Your library is empty. Scan a folder in Settings to add anime.")
            empty_label.setAlignment(Qt.AlignCenter)
            self.grid_layout.addWidget(empty_label, 0, 0, 1, -1)
            return

        col = 0
        row = 0
        max_cols = 5

        for anime_series_data in anime_series_list:
            card = AnimeCard(anime_series_data)
            card.series_selected.connect(self.series_selected.emit) # Bubble up the signal
            self.grid_layout.addWidget(card, row, col)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
