import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel, QScrollArea
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QPixmap, QFont, QFontMetrics
from src.core.settings_manager import SettingsManager
from .ui_anime_grid_widget import Ui_AnimeGridWidget

class AnimeCard(QWidget):
    series_selected = Signal(dict) # Signal to emit when a series is selected

    def __init__(self, anime_series_data, settings_manager: SettingsManager, parent=None):
        super().__init__(parent)
        self.anime_series_data = anime_series_data
        self.settings_manager = settings_manager
        self.setFixedSize(160, 240)
        self.original_style = "background-color: #3a3a3a; border-radius: 5px;"
        self.setProperty("class", "AnimeCard")
        self.setStyleSheet(f".AnimeCard {{ {self.original_style} }} .AnimeCard:hover {{ background-color: #4a4a4a; }}")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        self.cover_label = QLabel()
        self.cover_label.setAlignment(Qt.AlignCenter)
        self.cover_label.setFixedSize(150, 205)
        self.cover_label.setStyleSheet("border: 1px solid #555; background-color: #3a3a3a;")
        
        cover_path = None
        total_episodes = 0
        watched_count = 0

        # Collect episodes
        for episode in anime_series_data.get("episodes", []):
            total_episodes += 1
            if episode.get('is_watched'):
                watched_count += 1
            if not cover_path and episode.get("cover_path"):
                cover_path = episode.get("cover_path")

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

        if total_episodes > 0:
            self.watched_count_label = QLabel(f"{watched_count}/{total_episodes}", self.cover_label)
            self.watched_count_label.setStyleSheet(
                "background-color: rgba(0, 0, 0, 0.7);"
                "color: white;"
                "padding: 2px 5px;"
                "border-radius: 5px;"
            )
            self.watched_count_label.adjustSize()
            self.watched_count_label.move(
                self.cover_label.width() - self.watched_count_label.width() - 5,
                5
            )

        title = anime_series_data.get("title", "Unknown Title")
        display_text = title

        self.title_label = QLabel()
        font_metrics = QFontMetrics(self.title_label.font())
        elide_mode_str = self.settings_manager.get("elide_mode", "Right")
        elide_mode_map = {"Right": Qt.ElideRight, "Left": Qt.ElideLeft, "Middle": Qt.ElideMiddle}
        elide_mode = elide_mode_map.get(elide_mode_str, Qt.ElideRight)
        elided_text = font_metrics.elidedText(display_text, elide_mode, self.cover_label.width())
        self.title_label.setText(elided_text)
        self.title_label.setToolTip(display_text)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(QFont("Arial", 10))
        self.title_label.setFixedHeight(20)

        layout.addWidget(self.cover_label)
        layout.addWidget(self.title_label)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setStyleSheet(".AnimeCard { background-color: #5a5a5a; border: 1px solid #777; border-radius: 5px; }")
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setStyleSheet(f".AnimeCard {{ {self.original_style} }} .AnimeCard:hover {{ background-color: #4a4a4a; }}")
            self.series_selected.emit(self.anime_series_data)
        super().mouseReleaseEvent(event)

class AnimeGridWidget(QScrollArea, Ui_AnimeGridWidget):
    series_selected = Signal(dict) # Signal to bubble up from AnimeCard

    def __init__(self, settings_manager: SettingsManager, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.settings_manager = settings_manager
        self.anime_series_list = []
        self.current_cols = 0
        self.update_grid([]) # Initially empty

    def update_grid(self, anime_series_list):
        """
        Stores the list of anime series and triggers a relayout.
        """
        self.anime_series_list = anime_series_list
        self._relayout_grid()

    def _relayout_grid(self):
        """
        Recalculates column count and lays out the grid if necessary.
        """
        card_width = 160 + self.grid_layout.spacing()
        width = self.width()
        
        if width < card_width:
            cols = 1
        else:
            cols = max(1, int(width / card_width))

        if cols == self.current_cols and self.grid_layout.count() > 0:
            return # No change needed

        self.current_cols = cols
        
        # Clear existing items
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if not self.anime_series_list:
            empty_label = QLabel("Your library is empty. Scan a folder in Settings to add anime.")
            empty_label.setAlignment(Qt.AlignCenter)
            self.grid_layout.addWidget(empty_label, 0, 0, 1, -1)
            return

        row = 0
        col = 0
        for anime_series_data in self.anime_series_list:
            card = AnimeCard(anime_series_data, self.settings_manager)
            card.series_selected.connect(self.series_selected.emit)
            self.grid_layout.addWidget(card, row, col)
            col += 1
            if col >= self.current_cols:
                col = 0
                row += 1

    def resizeEvent(self, event):
        """Handle resize events to relayout the grid."""
        super().resizeEvent(event)
        self._relayout_grid()
