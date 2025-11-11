from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel, QScrollArea, QPushButton
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QPixmap, QFont
import os
from src.widgets.episode_list_widget import EpisodeRowWidget # Import EpisodeRowWidget

class SubSeriesCard(QWidget):
    sub_series_selected = Signal(dict) # Signal to emit when a sub-series is selected

    def __init__(self, sub_series_data, parent=None):
        super().__init__(parent)
        self.sub_series_data = sub_series_data
        self.setFixedSize(160, 250)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        self.cover_label = QLabel()
        self.cover_label.setAlignment(Qt.AlignCenter)
        self.cover_label.setFixedSize(150, 200)
        self.cover_label.setStyleSheet("border: 1px solid #555; background-color: #3a3a3a;")
        
        # Attempt to load cover image from the first available episode in this sub-series
        cover_path = None
        total_episodes = 0
        watched_count = 0

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

        title = sub_series_data.get("title", "Unknown Sub-series")
        
        display_text = f"{title}\n({watched_count}/{total_episodes} Watched)"

        self.title_label = QLabel(display_text)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setWordWrap(True)
        self.title_label.setFont(QFont("Arial", 10))

        layout.addWidget(self.cover_label)
        layout.addWidget(self.title_label)

    def mousePressEvent(self, event):
        """Handles click events on the sub-series card."""
        if event.button() == Qt.LeftButton:
            self.sub_series_selected.emit(self.sub_series_data)
        super().mousePressEvent(event)

class AnimeDetailView(QScrollArea): # Renamed class
    sub_series_or_episode_selected = Signal(dict) # Renamed signal
    back_to_anime_grid = Signal() # Signal to go back to main anime grid

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

        # Layout for direct episodes
        self.direct_episodes_layout = QVBoxLayout()
        self.direct_episodes_label = QLabel("Direct Episodes:")
        self.direct_episodes_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.direct_episodes_label.hide() # Hide by default
        self.main_layout.addWidget(self.direct_episodes_label)
        self.main_layout.addLayout(self.direct_episodes_layout)

        # Layout for sub-series grid
        self.sub_series_label = QLabel("Sub-series:")
        self.sub_series_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.sub_series_label.hide() # Hide by default
        self.main_layout.addWidget(self.sub_series_label)
        
        self.sub_series_grid_layout = QGridLayout()
        self.sub_series_grid_layout.setContentsMargins(0, 0, 0, 0)
        self.sub_series_grid_layout.setSpacing(10)
        self.sub_series_grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.main_layout.addLayout(self.sub_series_grid_layout)
        self.main_layout.addStretch() # Push content to top

    def update_view(self, anime_data): # Renamed method
        """
        Clears and repopulates the view with direct episodes and sub-series cards.
        """
        # Clear existing items in direct episodes layout
        for i in reversed(range(self.direct_episodes_layout.count())):
            widget = self.direct_episodes_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
            self.direct_episodes_layout.removeItem(self.direct_episodes_layout.itemAt(i))

        # Clear existing items in sub-series grid layout
        for i in reversed(range(self.sub_series_grid_layout.count())):
            item = self.sub_series_grid_layout.itemAt(i)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            self.sub_series_grid_layout.removeItem(item)

        direct_episodes = anime_data.get("episodes", [])
        sub_series_list = anime_data.get("sub_series", [])

        # Populate direct episodes
        if direct_episodes:
            self.direct_episodes_label.show()
            for episode in sorted(direct_episodes, key=lambda e: e.get('episode', 0) or 0):
                row_widget = EpisodeRowWidget(episode)
                row_widget.play_requested.connect(self.sub_series_or_episode_selected.emit) # Emit episode data
                self.direct_episodes_layout.addWidget(row_widget)
        else:
            self.direct_episodes_label.hide()

        # Populate sub-series
        if sub_series_list:
            self.sub_series_label.show()
            col = 0
            row = 0
            max_cols = 5

            for sub_series_data in sub_series_list:
                card = SubSeriesCard(sub_series_data)
                card.sub_series_selected.connect(self.sub_series_or_episode_selected.emit) # Emit sub-series data
                self.sub_series_grid_layout.addWidget(card, row, col)
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
        else:
            self.sub_series_label.hide()

        if not direct_episodes and not sub_series_list:
            empty_label = QLabel("No content found for this anime.")
            empty_label.setAlignment(Qt.AlignCenter)
            self.main_layout.addWidget(empty_label) # Add to main_layout if nothing else is shown
