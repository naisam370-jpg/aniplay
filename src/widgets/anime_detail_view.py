from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel, QScrollArea, QPushButton, QStackedWidget, QHBoxLayout
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QPixmap, QFont
import os

class EpisodeListItem(QWidget):
    clicked = Signal(dict)

    def __init__(self, item_data, parent=None):
        super().__init__(parent)
        self.item_data = item_data
        self.setObjectName("EpisodeListItem")
        self.setCursor(Qt.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)

        episode_num = item_data.get("episode")
        title = f"Episode {episode_num}" if episode_num is not None else os.path.basename(item_data["file_path"])
        
        self.title_label = QLabel(title)
        self.title_label.setFont(QFont("Arial", 11))
        
        layout.addWidget(self.title_label)
        layout.addStretch()

        if item_data.get("is_watched"):
            self.watched_label = QLabel("Watched")
            self.watched_label.setFont(QFont("Arial", 10, italic=True))
            self.watched_label.setStyleSheet("color: #888;")
            layout.addWidget(self.watched_label)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.item_data)
        super().mousePressEvent(event)

class ContentCard(QWidget):
    clicked = Signal(dict) # Signal to emit when the card is clicked

    def __init__(self, item_data, main_anime_cover_path=None, parent=None):
        super().__init__(parent)
        self.item_data = item_data
        self.main_anime_cover_path = main_anime_cover_path
        self.setObjectName("ContentCard")
        self.setFixedSize(160, 250)
        self.setCursor(Qt.PointingHandCursor) # Indicate clickable

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        self.cover_label = QLabel()
        self.cover_label.setObjectName("CoverLabel")
        self.cover_label.setAlignment(Qt.AlignCenter)
        self.cover_label.setFixedSize(150, 200)
        
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

    def __init__(self, settings_manager, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.current_items = []
        self.main_anime_cover_path = None
        self.is_episode_view = False
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.content_widget = QWidget()
        self.setWidget(self.content_widget)

        self.main_layout = QVBoxLayout(self.content_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
        self.main_layout.setAlignment(Qt.AlignTop)

        # --- Top Controls ---
        top_controls_layout = QHBoxLayout()
        self.btn_back = QPushButton("← Back")
        self.btn_back.clicked.connect(self.back_to_anime_grid.emit)
        self.btn_back.setFixedWidth(100)
        top_controls_layout.addWidget(self.btn_back)

        top_controls_layout.addStretch()

        self.btn_toggle_view = QPushButton("List View")
        self.btn_toggle_view.setCheckable(True)
        self.btn_toggle_view.clicked.connect(self._toggle_view)
        self.btn_toggle_view.setFixedWidth(100)
        top_controls_layout.addWidget(self.btn_toggle_view)
        self.main_layout.addLayout(top_controls_layout)

        # --- Description and Genres ---
        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        self.description_label.setFont(QFont("Arial", 10))
        self.main_layout.addWidget(self.description_label)

        self.genres_label = QLabel()
        self.genres_label.setFont(QFont("Arial", 10, italic=True))
        self.main_layout.addWidget(self.genres_label)

        # --- Content Views (Grid and List) ---
        self.view_stack = QStackedWidget()
        self.main_layout.addWidget(self.view_stack)

        # Grid View
        grid_container = QWidget()
        self.content_grid_layout = QGridLayout(grid_container)
        self.content_grid_layout.setContentsMargins(0, 0, 0, 0)
        self.content_grid_layout.setSpacing(10)
        self.content_grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.view_stack.addWidget(grid_container)

        # List View
        list_container = QWidget()
        self.content_list_layout = QVBoxLayout(list_container)
        self.content_list_layout.setContentsMargins(0, 0, 0, 0)
        self.content_list_layout.setSpacing(5)
        self.content_list_layout.setAlignment(Qt.AlignTop)
        self.content_list_layout.addStretch(1)
        self.view_stack.addWidget(list_container)
        
        self.main_layout.addStretch()

        # Load initial view mode
        initial_view_mode = self.settings_manager.get("episode_view_mode", "grid")
        if initial_view_mode == "list":
            self.btn_toggle_view.setChecked(True)
            self.btn_toggle_view.setText("Grid View")
            self.view_stack.setCurrentIndex(1)
        else:
            self.btn_toggle_view.setText("List View")
            self.view_stack.setCurrentIndex(0)

    def _toggle_view(self):
        if self.btn_toggle_view.isChecked():
            self.view_stack.setCurrentIndex(1) # List view
            self.btn_toggle_view.setText("Grid View")
            self.settings_manager.set("episode_view_mode", "list")
        else:
            self.view_stack.setCurrentIndex(0) # Grid view
            self.btn_toggle_view.setText("List View")
            self.settings_manager.set("episode_view_mode", "grid")
        self._update_current_view()

    def _clear_layout(self, layout):
        """Removes all widgets from a layout."""
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def update_view(self, anime_data, main_anime_cover_path, description, genres):
        """
        Clears and repopulates the view with content cards or list items.
        """
        self.description_label.setText(description)
        self.genres_label.setText(f"Genres: {genres}")

        direct_episodes = anime_data.get("episodes", [])
        sub_series_list = anime_data.get("sub_series", [])

        self.current_items = []
        self.is_episode_view = False
        self.main_anime_cover_path = main_anime_cover_path

        if sub_series_list:
            self.current_items.extend(sub_series_list)
            self.btn_toggle_view.hide()
        elif direct_episodes:
            self.current_items.extend(sorted(direct_episodes, key=lambda e: e.get('episode', 0) or 0))
            self.is_episode_view = True
            self.btn_toggle_view.show()

        self._update_current_view()

    def _update_current_view(self):
        self._clear_layout(self.content_grid_layout)
        self._clear_layout(self.content_list_layout)

        if not self.current_items:
            self.content_grid_layout.addWidget(QLabel("No content found for this anime."), 0, 0)
            self.content_list_layout.addWidget(QLabel("No content found for this anime."))
            return

        if self.view_stack.currentIndex() == 0: # Grid view
            self._populate_grid_view()
        else: # List view
            self._populate_list_view()

    def _populate_grid_view(self):
        col, row, max_cols = 0, 0, 5
        for item_data in self.current_items:
            card = ContentCard(item_data, self.main_anime_cover_path)
            card.clicked.connect(self.sub_series_or_episode_selected.emit)
            self.content_grid_layout.addWidget(card, row, col)
            col += 1
            if col >= max_cols:
                col, row = 0, row + 1
    
    def _populate_list_view(self):
        if self.is_episode_view:
            for item_data in self.current_items:
                list_item = EpisodeListItem(item_data)
                list_item.clicked.connect(self.sub_series_or_episode_selected.emit)
                self.content_list_layout.addWidget(list_item)
