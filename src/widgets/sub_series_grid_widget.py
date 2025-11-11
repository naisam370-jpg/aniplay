from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel, QScrollArea, QPushButton
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QPixmap, QFont
import os

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

class SubSeriesGridWidget(QScrollArea):
    sub_series_selected = Signal(dict) # Signal to bubble up from SubSeriesCard
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

        self.grid_layout = QGridLayout()
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(10)
        self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.main_layout.addLayout(self.grid_layout)
        self.main_layout.addStretch() # Push content to top

        self.update_grid([]) # Initially empty

    def update_grid(self, sub_series_list):
        """
        Clears and repopulates the grid with new sub-series cards.
        """
        # Clear existing items in the grid layout (excluding the back button)
        for i in reversed(range(self.grid_layout.count())):
            item = self.grid_layout.itemAt(i)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            self.grid_layout.removeItem(item)

        if not sub_series_list:
            empty_label = QLabel("No sub-series found for this anime.")
            empty_label.setAlignment(Qt.AlignCenter)
            self.grid_layout.addWidget(empty_label, 0, 0, 1, -1)
            return

        col = 0
        row = 0
        max_cols = 5

        for sub_series_data in sub_series_list:
            card = SubSeriesCard(sub_series_data)
            card.sub_series_selected.connect(self.sub_series_selected.emit) # Bubble up the signal
            self.grid_layout.addWidget(card, row, col)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
