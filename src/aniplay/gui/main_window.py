#!/usr/bin/env python3
"""
Enhanced AniPlay GUI with Database Integration
File: src/aniplay/gui/main_window.py
"""

import sys
import os
import subprocess
from functools import partial
from typing import List, Optional

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QListWidget, QListWidgetItem, QStackedWidget, QFrame, QSpacerItem,
    QSizePolicy, QMessageBox, QPushButton, QDialog, QComboBox, QCheckBox, QSlider,
    QStyle, QAbstractItemView, QLineEdit, QProgressBar, QMenu, QAction, QSplitter,
    QTextEdit, QGroupBox, QButtonGroup, QRadioButton
)
from PyQt5.QtGui import QIcon, QPixmap, QFont, QPainter, QPen
from PyQt5.QtCore import Qt, QSize, QTimer, pyqtSignal, QThread, QPropertyAnimation, QEasingCurve
import PyQt5.QtCore as QtCore

# Import our new modules
from ..core.database import DatabaseManager
from ..core.library_scanner import LibraryScanner
from ..models.anime import Anime
from ..models.episode import Episode
from ..utils.file_utils import format_duration, format_file_size, generate_video_thumbnail

# Constants
POSTER_SIZE = QSize(220, 310)
THUMB_SIZE = QSize(320, 180)
MINI_POSTER_SIZE = QSize(160, 225)

class SearchBar(QLineEdit):
    """Enhanced search bar with clear button and search suggestions"""
    search_requested = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("Search anime...")
        self.setObjectName("SearchBar")
        self.textChanged.connect(self._on_text_changed)
        self.returnPressed.connect(self._on_search_requested)
        
        # Add clear button
        self.clear_action = self.addAction(
            self.style().standardIcon(QStyle.SP_DialogCloseButton), 
            QLineEdit.TrailingPosition
        )
        self.clear_action.triggered.connect(self.clear)
        self.clear_action.setVisible(False)
    
    def _on_text_changed(self, text):
        self.clear_action.setVisible(bool(text))
        if len(text) >= 2:  # Start searching after 2 characters
            QTimer.singleShot(300, lambda: self.search_requested.emit(text))
        elif len(text) == 0:
            self.search_requested.emit("")  # Show all when cleared
    
    def _on_search_requested(self):
        self.search_requested.emit(self.text())

class SortFilterWidget(QWidget):
    """Widget for sorting and filtering options"""
    sort_changed = pyqtSignal(str, bool)  # sort_by, reverse
    filter_changed = pyqtSignal(str)      # filter_type
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Sort options
        sort_label = QLabel("Sort:")
        self.sort_combo = QComboBox()
        self.sort_combo.addItems([
            "Name", "Date Added", "Last Watched", "Rating", "Year"
        ])
        self.sort_combo.currentTextChanged.connect(self._on_sort_changed)
        
        self.reverse_check = QCheckBox("Reverse")
        self.reverse_check.toggled.connect(self._on_sort_changed)
        
        # Filter options
        filter_label = QLabel("Filter:")
        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            "All", "Favorites", "Recently Watched", "Completed", "Ongoing"
        ])
        self.filter_combo.currentTextChanged.connect(self._on_filter_changed)
        
        layout.addWidget(sort_label)
        layout.addWidget(self.sort_combo)
        layout.addWidget(self.reverse_check)
        layout.addWidget(QFrame())  # Separator
        layout.addWidget(filter_label)
        layout.addWidget(self.filter_combo)
        layout.addStretch()
    
    def _on_sort_changed(self):
        sort_by = self.sort_combo.currentText().lower().replace(" ", "_")
        self.sort_changed.emit(sort_by, self.reverse_check.isChecked())
    
    def _on_filter_changed(self):
        filter_type = self.filter_combo.currentText().lower().replace(" ", "_")
        self.filter_changed.emit(filter_type)

class EnhancedSeriesGrid(QListWidget):
    """Enhanced series grid with progress indicators and context menu"""
    anime_selected = pyqtSignal(Anime)
    favorite_toggled = pyqtSignal(int, bool)
    
    def __init__(self):
        super().__init__()
        self.setViewMode(QListWidget.IconMode)
        self.setResizeMode(QListWidget.Adjust)
        self.setMovement(QListWidget.Static)
        self.setWrapping(True)
        self.setUniformItemSizes(True)
        self.setWordWrap(True)
        self.setSpacing(16)
        self.setIconSize(POSTER_SIZE)
        self.setGridSize(QSize(POSTER_SIZE.width() + 24, POSTER_SIZE.height() + 72))
        self.setSelectionMode(QListWidget.SingleSelection)
        self.setObjectName("SeriesGrid")
        self.setVerticalScrollMode(QListWidget.ScrollPerPixel)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        
        # Connect signals
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.itemActivated.connect(self._on_item_activated)
    
    def populate_anime_list(self, anime_list: List[Anime]):
        """Populate grid with anime list"""
        self.clear()
        
        for anime in anime_list:
            item = self._create_anime_item(anime)
            self.addItem(item)
        
        if self.count() > 0:
            self.setCurrentRow(0)
    
    def _create_anime_item(self, anime: Anime) -> QListWidgetItem:
        """Create a list widget item for an anime"""
        # Create display text with progress info
        watched_episodes = self._get_watched_episodes_count(anime)
        if anime.total_episodes > 0:
            progress_text = f"{watched_episodes}/{anime.total_episodes}"
            display_text = f"{anime.name}\n{progress_text} episodes"
        else:
            display_text = anime.name
        
        item = QListWidgetItem(display_text)
        item.setTextAlignment(Qt.AlignHCenter)
        item.setData(Qt.UserRole, anime)
        
        # Set icon
        if anime.cover_path and os.path.exists(anime.cover_path):
            pixmap = QPixmap(anime.cover_path)
            # Add favorite indicator if needed
            if anime.is_favorite:
                pixmap = self._add_favorite_indicator(pixmap)
            item.setIcon(QIcon(pixmap))
        else:
            item.setIcon(QIcon(self._get_placeholder_poster()))
        
        return item
    
    def _get_watched_episodes_count(self, anime: Anime) -> int:
        """Get count of watched episodes for an anime"""
        # This would need to query the database
        # For now, return 0 as placeholder
        return 0
    
    def _add_favorite_indicator(self, pixmap: QPixmap) -> QPixmap:
        """Add a favorite star indicator to the pixmap"""
        painter = QPainter(pixmap)
        painter.setPen(QPen(Qt.yellow, 2))
        painter.setBrush(Qt.yellow)
        
        # Draw star in top-right corner
        star_size = 20
        x = pixmap.width() - star_size - 5
        y = 5
        
        # Simple star drawing (you could use a better star shape)
        painter.drawEllipse(x, y, star_size, star_size)
        painter.end()
        
        return pixmap
    
    def _get_placeholder_poster(self) -> str:
        """Get placeholder poster path"""
        placeholder_path = "placeholder_poster.png"
        if not os.path.exists(placeholder_path):
            pixmap = QPixmap(POSTER_SIZE)
            pixmap.fill(Qt.darkGray)
            pixmap.save(placeholder_path)
        return placeholder_path
    
    def _on_item_activated(self, item):
        """Handle item activation"""
        anime = item.data(Qt.UserRole)
        if anime:
            self.anime_selected.emit(anime)
    
    def show_context_menu(self, position):
        """Show context menu for anime items"""
        item = self.itemAt(position)
        if not item:
            return
        
        anime = item.data(Qt.UserRole)
        menu = QMenu(self)
        
        # Favorite toggle
        if anime.is_favorite:
            favorite_action = menu.addAction("Remove from Favorites")
        else:
            favorite_action = menu.addAction("Add to Favorites")
        
        # Other actions
        info_action = menu.addAction("Show Info")
        rescan_action = menu.addAction("Rescan Episodes")
        
        # Execute menu
        action = menu.exec_(self.mapToGlobal(position))
        
        if action == favorite_action:
            self.favorite_toggled.emit(anime.id, not anime.is_favorite)
        elif action == info_action:
            self._show_anime_info(anime)
        elif action == rescan_action:
            self._rescan_anime(anime)
    
    def _show_anime_info(self, anime: Anime):
        """Show detailed anime information"""
        # This would open an info dialog
        QMessageBox.information(self, "Anime Info", 
                               f"Name: {anime.name}\n"
                               f"Episodes: {anime.total_episodes}\n"
                               f"Rating: {anime.rating}\n"
                               f"Status: {anime.status}")
    
    def _rescan_anime(self, anime: Anime):
        """Request rescan of anime episodes"""
        # This would trigger a rescan operation
        QMessageBox.information(self, "Rescan", f"Rescanning {anime.name}...")

class EnhancedEpisodeGrid(QListWidget):
    """Enhanced episode grid with progress indicators"""
    episode_selected = pyqtSignal(Episode)
    
    def __init__(self):
        super().__init__()
        self.setViewMode(QListWidget.IconMode)
        self.setResizeMode(QListWidget.Adjust)
        self.setMovement(QListWidget.Static)
        self.setWrapping(True)
        self.setUniformItemSizes(True)
        self.setWordWrap(True)
        self.setSpacing(16)
        self.setIconSize(THUMB_SIZE)
        self.setGridSize(QSize(THUMB_SIZE.width() + 24, THUMB_SIZE.height() + 68))
        self.setSelectionMode(QListWidget.SingleSelection)
        self.setObjectName("EpisodeGrid")
        self.setVerticalScrollMode(QListWidget.ScrollPerPixel)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFocusPolicy(Qt.StrongFocus)
        
        self.itemActivated.connect(self._on_item_activated)
    
    def populate_episodes(self, episodes: List[Episode]):
        """Populate grid with episodes"""
        self.clear()
        
        for episode in episodes:
            item = self._create_episode_item(episode)
            self.addItem(item)
        
        if self.count() > 0:
            self.setCurrentRow(0)
    
    def _create_episode_item(self, episode: Episode) -> QListWidgetItem:
        """Create episode item with progress info"""
        # Create display text
        duration_text = format_duration(episode.duration) if episode.duration > 0 else "Unknown"
        progress_text = ""
        
        if episode.is_watched:
            progress_text = "✓ Watched"
        elif episode.progress_seconds > 0:
            progress_percent = (episode.progress_seconds / episode.duration) * 100 if episode.duration > 0 else 0
            progress_text = f"{progress_percent:.0f}% watched"
        
        display_text = f"Episode {episode.episode_number}"
        if episode.title and episode.title != f"Episode {episode.episode_number}":
            display_text += f"\n{episode.title}"
        display_text += f"\n{duration_text}"
        if progress_text:
            display_text += f"\n{progress_text}"
        
        item = QListWidgetItem(display_text)
        item.setTextAlignment(Qt.AlignHCenter)
        item.setData(Qt.UserRole, episode)
        
        # Set thumbnail
        if episode.thumbnail_path and os.path.exists(episode.thumbnail_path):
            pixmap = QPixmap(episode.thumbnail_path)
            if episode.is_watched:
                pixmap = self._add_watched_indicator(pixmap)
            item.setIcon(QIcon(pixmap))
        else:
            item.setIcon(QIcon(self._get_placeholder_thumb()))
        
        return item
    
    def _add_watched_indicator(self, pixmap: QPixmap) -> QPixmap:
        """Add watched indicator to thumbnail"""
        painter = QPainter(pixmap)
        painter.setPen(QPen(Qt.green, 3))
        painter.setBrush(Qt.green)
        
        # Draw checkmark in corner
        check_size = 25
        x = pixmap.width() - check_size - 5
        y = 5
        painter.drawEllipse(x, y, check_size, check_size)
        
        # Draw checkmark
        painter.setPen(QPen(Qt.white, 3))
        painter.drawLine(x + 6, y + 12, x + 10, y + 16)
        painter.drawLine(x + 10, y + 16, x + 18, y + 8)
        painter.end()
        
        return pixmap
    
    def _get_placeholder_thumb(self) -> str:
        """Get placeholder thumbnail"""
        placeholder_path = "placeholder_thumb.png"
        if not os.path.exists(placeholder_path):
            pixmap = QPixmap(THUMB_SIZE)
            pixmap.fill(Qt.darkGray)
            pixmap.save(placeholder_path)
        return placeholder_path
    
    def _on_item_activated(self, item):
        """Handle episode activation"""
        episode = item.data(Qt.UserRole)
        if episode:
            self.episode_selected.emit(episode)

class HeaderBar(QFrame):
    """Enhanced header with search and controls"""
    def __init__(self, title="AniPlay", parent=None):
        super().__init__(parent)
        self.setObjectName("HeaderBar")
        self.setFixedHeight(80)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(18, 8, 18, 8)
        main_layout.setSpacing(8)
        
        # Top row - title and buttons
        top_layout = QHBoxLayout()
        
        self.title = QLabel(title)
        self.title.setObjectName("HeaderTitle")
        self.title.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        
        # Buttons
        self.refresh_btn = QPushButton()
        self.refresh_btn.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        self.refresh_btn.setToolTip("Refresh Library")
        self.refresh_btn.setFixedSize(32, 32)
        
        self.settings_btn = QPushButton()
        self.settings_btn.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
        self.settings_btn.setToolTip("Settings")
        self.settings_btn.setFixedSize(32, 32)
        
        self.library_btn = QPushButton()
        self.library_btn.setIcon(self.style().standardIcon(QStyle.SP_DirIcon))
        self.library_btn.setToolTip("Library Management")
        self.library_btn.setFixedSize(32, 32)
        
        top_layout.addWidget(self.title, 0, Qt.AlignVCenter)
        top_layout.addStretch()
        top_layout.addWidget(self.refresh_btn)
        top_layout.addWidget(self.library_btn)
        top_layout.addWidget(self.settings_btn)
        
        # Bottom row - search and filters
        bottom_layout = QHBoxLayout()
        
        self.search_bar = SearchBar()
        self.search_bar.setMaximumWidth(300)
        
        self.sort_filter_widget = SortFilterWidget()
        
        bottom_layout.addWidget(self.search_bar)
        bottom_layout.addWidget(self.sort_filter_widget)
        
        main_layout.addLayout(top_layout)
        main_layout.addLayout(bottom_layout)

class LibraryScanThread(QThread):
    """Background thread for library scanning"""
    progress_update = pyqtSignal(str, int, int)  # message, current, total
    scan_complete = pyqtSignal(dict)  # statistics
    error_occurred = pyqtSignal(str)
    
    def __init__(self, scanner: LibraryScanner, library_path: str):
        super().__init__()
        self.scanner = scanner
        self.library_path = library_path
    
    def run(self):
        try:
            self.progress_update.emit("Starting library scan...", 0, 100)
            stats = self.scanner.scan_library(self.library_path, update_existing=True)
            self.scan_complete.emit(stats)
        except Exception as e:
            self.error_occurred.emit(str(e))

class AniPlayMainWindow(QMainWindow):
    """Enhanced main window with database integration"""
    
    def __init__(self, library_path: str, covers_path: str, thumbs_path: str, db_path: str):
        super().__init__()
        self.setWindowTitle("AniPlay")
        self.setMinimumSize(1200, 720)
        
        # Initialize paths
        self.library_path = library_path
        self.covers_path = covers_path
        self.thumbs_path = thumbs_path
        
        # Initialize database and scanner
        self.db = DatabaseManager(db_path)
        self.scanner = LibraryScanner(self.db, covers_path, thumbs_path)
        
        # Current data
        self.current_anime_list: List[Anime] = []
        self.current_anime: Optional[Anime] = None
        self.current_search_query = ""
        self.current_sort = ("name", False)
        self.current_filter = "all"
        
        self.setup_ui()
        self.connect_signals()
        self.load_settings()
        
        # Load initial data
        QTimer.singleShot(100, self.refresh_library_display)
    
    def setup_ui(self):
        """Setup the user interface"""
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        # Main library page
        self.library_page = QWidget()
        library_layout = QVBoxLayout(self.library_page)
        library_layout.setContentsMargins(0, 0, 0, 0)
        
        self.header = HeaderBar("AniPlay")
        library_layout.addWidget(self.header)
        
        # Recently watched section (optional)
        self.recently_watched_section = self.create_recently_watched_section()
        library_layout.addWidget(self.recently_watched_section)
        
        # Main series grid
        self.series_grid = EnhancedSeriesGrid()
        library_layout.addWidget(self.series_grid)
        
        # Episodes page
        self.episodes_page = QWidget()
        episodes_layout = QVBoxLayout(self.episodes_page)
        episodes_layout.setContentsMargins(0, 0, 0, 0)
        
        self.episodes_header = HeaderBar("Episodes")
        episodes_layout.addWidget(self.episodes_header)
        
        # Episode info section
        episode_info_layout = QHBoxLayout()
        
        self.anime_info_widget = self.create_anime_info_widget()
        episode_info_layout.addWidget(self.anime_info_widget)
        
        episodes_layout.addLayout(episode_info_layout)
        
        # Episodes grid
        self.episode_grid = EnhancedEpisodeGrid()
        episodes_layout.addWidget(self.episode_grid)
        
        # Add pages to stack
        self.stack.addWidget(self.library_page)
        self.stack.addWidget(self.episodes_page)
        
        # Progress bar for scanning
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.statusBar().addPermanentWidget(self.progress_bar)
        
        # Apply initial styling
        self.apply_theme("dark")
    
    def create_recently_watched_section(self) -> QWidget:
        """Create recently watched section"""
        section = QWidget()
        section.setMaximumHeight(280)
        layout = QVBoxLayout(section)
        
        title = QLabel("Recently Watched")
        title.setObjectName("SectionTitle")
        layout.addWidget(title)
        
        # Horizontal scroll area for recently watched
        self.recent_list = QListWidget()
        self.recent_list.setViewMode(QListWidget.IconMode)
        self.recent_list.setFlow(QListWidget.LeftToRight)
        self.recent_list.setWrapping(False)
        self.recent_list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.recent_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.recent_list.setFixedHeight(250)
        self.recent_list.setIconSize(MINI_POSTER_SIZE)
        self.recent_list.setGridSize(QSize(MINI_POSTER_SIZE.width() + 20, MINI_POSTER_SIZE.height() + 40))
        self.recent_list.setObjectName("RecentList")
        
        layout.addWidget(self.recent_list)
        return section
    
    def create_anime_info_widget(self) -> QWidget:
        """Create anime information display widget"""
        widget = QWidget()
        widget.setMaximumHeight(120)
        layout = QHBoxLayout(widget)
        
        # Anime cover (small)
        self.anime_cover_label = QLabel()
        self.anime_cover_label.setFixedSize(80, 110)
        self.anime_cover_label.setScaledContents(True)
        self.anime_cover_label.setStyleSheet("border: 1px solid #444; border-radius: 4px;")
        
        # Anime details
        details_layout = QVBoxLayout()
        
        self.anime_title_label = QLabel()
        self.anime_title_label.setObjectName("AnimeTitle")
        
        self.anime_stats_label = QLabel()
        self.anime_stats_label.setObjectName("AnimeStats")
        
        # Progress info
        self.progress_info_label = QLabel()
        self.progress_info_label.setObjectName("ProgressInfo")
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        self.favorite_btn = QPushButton("★ Favorite")
        self.favorite_btn.setCheckable(True)
        self.favorite_btn.setObjectName("FavoriteButton")
        
        self.mark_watched_btn = QPushButton("Mark All Watched")
        
        buttons_layout.addWidget(self.favorite_btn)
        buttons_layout.addWidget(self.mark_watched_btn)
        buttons_layout.addStretch()
        
        details_layout.addWidget(self.anime_title_label)
        details_layout.addWidget(self.anime_stats_label)
        details_layout.addWidget(self.progress_info_label)
        details_layout.addLayout(buttons_layout)
        details_layout.addStretch()
        
        layout.addWidget(self.anime_cover_label)
        layout.addLayout(details_layout)
        layout.addStretch()
        
        return widget
    
    def connect_signals(self):
        """Connect all signal handlers"""
        # Header signals
        self.header.refresh_btn.clicked.connect(self.scan_library)
        self.header.settings_btn.clicked.connect(self.open_settings)
        self.header.library_btn.clicked.connect(self.open_library_management)
        self.header.search_bar.search_requested.connect(self.search_anime)
        self.header.sort_filter_widget.sort_changed.connect(self.sort_anime)
        self.header.sort_filter_widget.filter_changed.connect(self.filter_anime)
        
        # Series grid signals
        self.series_grid.anime_selected.connect(self.open_anime_episodes)
        self.series_grid.favorite_toggled.connect(self.toggle_favorite)
        
        # Episode grid signals
        self.episode_grid.episode_selected.connect(self.play_episode)
        
        # Recently watched signals
        self.recent_list.itemActivated.connect(self.open_recent_anime)
        
        # Anime info signals
        self.favorite_btn.toggled.connect(self.on_favorite_toggled)
        self.mark_watched_btn.clicked.connect(self.mark_all_watched)
    
    def load_settings(self):
        """Load user settings from database"""
        self.theme = self.db.get_setting("theme", "dark")
        self.scroll_speed = self.db.get_setting("scroll_speed", 5)
        self.auto_fetch_covers = self.db.get_setting("auto_fetch_covers", True)
        
        # Apply settings
        self.apply_theme(self.theme)
        self.series_grid.verticalScrollBar().setSingleStep(self.scroll_speed)
        self.episode_grid.verticalScrollBar().setSingleStep(self.scroll_speed)
    
    def scan_library(self):
        """Start background library scan"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        # Start scan thread
        self.scan_thread = LibraryScanThread(self.scanner, self.library_path)
        self.scan_thread.progress_update.connect(self.on_scan_progress)
        self.scan_thread.scan_complete.connect(self.on_scan_complete)
        self.scan_thread.error_occurred.connect(self.on_scan_error)
        self.scan_thread.start()
    
    def on_scan_progress(self, message: str, current: int, total: int):
        """Handle scan progress updates"""
        self.statusBar().showMessage(message)
        if total > 0:
            self.progress_bar.setRange(0, total)
            self.progress_bar.setValue(current)
    
    def on_scan_complete(self, stats: dict):
        """Handle scan completion"""
        self.progress_bar.setVisible(False)
        self.statusBar().showMessage(
            f"Scan complete: {stats['anime_added']} added, {stats['episodes_added']} episodes", 
            5000
        )
        self.refresh_library_display()
    
    def on_scan_error(self, error: str):
        """Handle scan errors"""
        self.progress_bar.setVisible(False)
        self.statusBar().showMessage("Scan failed", 5000)
        QMessageBox.critical(self, "Scan Error", f"Library scan failed:\n{error}")
    
    def refresh_library_display(self):
        """Refresh the anime display"""
        self.apply_filters_and_sort()
        self.load_recently_watched()
    
    def apply_filters_and_sort(self):
        """Apply current search, filter, and sort to anime list"""
        # Get base anime list
        if self.current_filter == "all":
            anime_list = self.db.get_all_anime()
        elif self.current_filter == "favorites":
            anime_list = self.db.get_favorites()
        elif self.current_filter == "recently_watched":
            anime_list = self.db.get_recently_watched(50)
        else:
            anime_list = self.db.get_all_anime()
        
        # Apply search filter
        if self.current_search_query:
            anime_list = [anime for anime in anime_list 
                         if self.current_search_query.lower() in anime.name.lower()]
        
        # Apply sorting
        sort_key, reverse = self.current_sort
        if sort_key == "name":
            anime_list.sort(key=lambda x: x.name.lower(), reverse=reverse)
        elif sort_key == "date_added":
            anime_list.sort(key=lambda x: x.date_added or "", reverse=reverse)
        elif sort_key == "last_watched":
            anime_list.sort(key=lambda x: x.last_watched or "", reverse=reverse)
        elif sort_key == "rating":
            anime_list.sort(key=lambda x: x.rating, reverse=reverse)
        elif sort_key == "year":
            anime_list.sort(key=lambda x: x.year or 0, reverse=reverse)
        
        self.current_anime_list = anime_list
        self.series_grid.populate_anime_list(anime_list)
    
    def load_recently_watched(self):
        """Load recently watched anime"""
        recent_anime = self.db.get_recently_watched(10)
        self.recent_list.clear()
        
        for anime in recent_anime:
            item = QListWidgetItem(anime.name)
            item.setData(Qt.UserRole, anime)
            
            if anime.cover_path and os.path.exists(anime.cover_path):
                item.setIcon(QIcon(anime.cover_path))
            else:
                item.setIcon(QIcon(self._get_placeholder_mini()))
            
            self.recent_list.addItem(item)
    
    def search_anime(self, query: str):
        """Handle search requests"""
        self.current_search_query = query
        self.apply_filters_and_sort()
    
    def sort_anime(self, sort_by: str, reverse: bool):
        """Handle sort changes"""
        self.current_sort = (sort_by, reverse)
        self.apply_filters_and_sort()
    
    def filter_anime(self, filter_type: str):
        """Handle filter changes"""
        self.current_filter = filter_type
        self.apply_filters_and_sort()
    
    def open_anime_episodes(self, anime: Anime):
        """Open episodes view for an anime"""
        self.current_anime = anime
        
        # Update anime info display
        self.update_anime_info_display(anime)
        
        # Load episodes
        episodes = self.db.get_episodes(anime.id)
        self.episode_grid.populate_episodes(episodes)
        
        # Switch to episodes page
        self.stack.setCurrentWidget(self.episodes_page)
        self.episode_grid.setFocus()
    
    def update_anime_info_display(self, anime: Anime):
        """Update the anime info display"""
        # Set cover
        if anime.cover_path and os.path.exists(anime.cover_path):
            self.anime_cover_label.setPixmap(QPixmap(anime.cover_path))
        else:
            self.anime_cover_label.clear()
        
        # Set title
        self.anime_title_label.setText(anime.name)
        
        # Set stats
        stats_text = f"Episodes: {anime.total_episodes}"
        if anime.rating > 0:
            stats_text += f" • Rating: {anime.rating:.1f}"
        if anime.year:
            stats_text += f" • Year: {anime.year}"
        self.anime_stats_label.setText(stats_text)
        
        # Set progress info
        episodes = self.db.get_episodes(anime.id)
        watched_count = sum(1 for ep in episodes if ep.is_watched)
        progress_text = f"Watched: {watched_count}/{len(episodes)} episodes"
        if watched_count > 0 and len(episodes) > 0:
            progress_percent = (watched_count / len(episodes)) * 100
            progress_text += f" ({progress_percent:.0f}%)"
        self.progress_info_label.setText(progress_text)
        
        # Update favorite button
        self.favorite_btn.setChecked(anime.is_favorite)
    
    def play_episode(self, episode: Episode):
        """Play an episode"""
        if not os.path.exists(episode.file_path):
            QMessageBox.warning(self, "File Not Found", 
                               f"Episode file not found:\n{episode.file_path}")
            return
        
        try:
            # Launch mpv player
            subprocess.Popen([
                "mpv", 
                "--force-window=yes",
                f"--save-position-on-quit",
                episode.file_path
            ])
            
            # Update last watched time for anime
            self.db.update_progress(episode.id, episode.progress_seconds, episode.is_watched)
            
            # Refresh displays
            self.refresh_library_display()
            if self.current_anime:
                self.update_anime_info_display(self.current_anime)
            
        except Exception as e:
            QMessageBox.critical(self, "Playback Error", 
                                f"Failed to start playback:\n{str(e)}")
    
    def toggle_favorite(self, anime_id: int, is_favorite: bool):
        """Toggle favorite status of an anime"""
        # Update database
        with self.db.get_connection() as conn:
            conn.execute("UPDATE anime SET is_favorite = ? WHERE id = ?", 
                        (is_favorite, anime_id))
        
        # Refresh display
        self.refresh_library_display()
        
        # Update current anime if it's the one being toggled
        if self.current_anime and self.current_anime.id == anime_id:
            self.current_anime.is_favorite = is_favorite
            self.update_anime_info_display(self.current_anime)
    
    def on_favorite_toggled(self, checked: bool):
        """Handle favorite button toggle"""
        if self.current_anime:
            self.toggle_favorite(self.current_anime.id, checked)
    
    def mark_all_watched(self):
        """Mark all episodes of current anime as watched"""
        if not self.current_anime:
            return
        
        reply = QMessageBox.question(self, "Mark All Watched",
                                   f"Mark all episodes of '{self.current_anime.name}' as watched?")
        
        if reply == QMessageBox.Yes:
            episodes = self.db.get_episodes(self.current_anime.id)
            for episode in episodes:
                self.db.update_progress(episode.id, episode.duration, True)
            
            # Refresh display
            self.open_anime_episodes(self.current_anime)
    
    def open_recent_anime(self, item):
        """Open anime from recently watched list"""
        anime = item.data(Qt.UserRole)
        if anime:
            self.open_anime_episodes(anime)
    
    def open_settings(self):
        """Open settings dialog"""
        from .settings_dialog import SettingsDialog
        
        dialog = SettingsDialog(self, {
            "theme": self.theme,
            "scroll_speed": self.scroll_speed,
            "auto_fetch_covers": self.auto_fetch_covers
        })
        
        if dialog.exec_() == QDialog.Accepted:
            settings = dialog.get_settings()
            self.apply_settings(settings)
    
    def open_library_management(self):
        """Open library management dialog"""
        QMessageBox.information(self, "Library Management", 
                               "Library management features coming soon!")
    
    def apply_settings(self, settings: dict):
        """Apply new settings"""
        # Save to database
        for key, value in settings.items():
            self.db.set_setting(key, value)
        
        # Apply locally
        if "theme" in settings:
            self.theme = settings["theme"]
            self.apply_theme(self.theme)
        
        if "scroll_speed" in settings:
            self.scroll_speed = settings["scroll_speed"]
            self.series_grid.verticalScrollBar().setSingleStep(self.scroll_speed)
            self.episode_grid.verticalScrollBar().setSingleStep(self.scroll_speed)
        
        if "auto_fetch_covers" in settings:
            self.auto_fetch_covers = settings["auto_fetch_covers"]
    
    def apply_theme(self, theme: str):
        """Apply theme styling"""
        if theme == "dark":
            self.setStyleSheet(self._get_dark_theme_css())
        else:
            self.setStyleSheet(self._get_light_theme_css())
    
    def _get_dark_theme_css(self) -> str:
        """Get dark theme stylesheet"""
        return """
        QMainWindow { background-color: #0f0f10; }
        
        #HeaderBar {
            background-color: #17181c;
            border-bottom: 1px solid #232326;
        }
        
        #HeaderTitle {
            color: #ffffff;
            font-size: 20px;
            font-weight: 700;
        }
        
        #SectionTitle {
            color: #ffffff;
            font-size: 18px;
            font-weight: 600;
            margin: 6px 2px 6px 2px;
        }
        
        #AnimeTitle {
            color: #ffffff;
            font-size: 16px;
            font-weight: 600;
        }
        
        #AnimeStats, #ProgressInfo {
            color: #b9b9bd;
            font-size: 12px;
        }
        
        QListWidget#SeriesGrid, QListWidget#EpisodeGrid, QListWidget#RecentList {
            background-color: #0f0f10;
            border: none;
            color: #E35FFD;
            font-size: 13px;
        }
        
        QListWidget::item {
            margin: 6px;
            padding: 6px 4px 10px 4px;
            border-radius: 12px;
        }
        
        QListWidget::item:selected {
            background-color: #17181c;
            border: 2px solid #2491ff;
        }
        
        QListWidget::item:hover {
            background-color: #17181c;
            border: 1px solid #2491ff;
        }
        
        #SearchBar {
            padding: 8px 12px;
            border: 1px solid #444;
            border-radius: 6px;
            background-color: #17181c;
            color: #ffffff;
            font-size: 14px;
        }
        
        #SearchBar:focus {
            border-color: #2491ff;
        }
        
        QComboBox {
            padding: 6px 12px;
            border: 1px solid #444;
            border-radius: 4px;
            background-color: #17181c;
            color: #ffffff;
        }
        
        QPushButton {
            padding: 6px 12px;
            border: 1px solid #444;
            border-radius: 4px;
            background-color: #17181c;
            color: #ffffff;
        }
        
        QPushButton:hover {
            background-color: #232326;
            border-color: #2491ff;
        }
        
        QPushButton:pressed {
            background-color: #2491ff;
        }
        
        #FavoriteButton:checked {
            background-color: #ff6b35;
            border-color: #ff6b35;
            color: #ffffff;
        }
        
        QProgressBar {
            border: 1px solid #444;
            border-radius: 4px;
            background-color: #17181c;
        }
        
        QProgressBar::chunk {
            background-color: #2491ff;
            border-radius: 3px;
        }
        """
    
    def _get_light_theme_css(self) -> str:
        """Get light theme stylesheet"""
        return """
        QMainWindow { background-color: #f2f2f2; }
        
        #HeaderBar {
            background-color: #ffffff;
            border-bottom: 1px solid #e0e0e0;
        }
        
        #HeaderTitle {
            color: #000000;
            font-size: 20px;
            font-weight: 700;
        }
        
        #SectionTitle {
            color: #000000;
            font-size: 18px;
            font-weight: 600;
            margin: 6px 2px 6px 2px;
        }
        
        QListWidget#SeriesGrid, QListWidget#EpisodeGrid, QListWidget#RecentList {
            background-color: #f2f2f2;
            border: none;
            color: #B62CF7;
            font-size: 13px;
        }
        
        QListWidget::item {
            margin: 6px;
            padding: 6px 4px 10px 4px;
            border-radius: 12px;
        }
        
        QListWidget::item:selected {
            background-color: #ffffff;
            border: 2px solid #0078d7;
        }
        
        QListWidget::item:hover {
            background-color: #ffffff;
            border: 1px solid #0078d7;
        }
        """
    
    def _get_placeholder_mini(self) -> str:
        """Get mini placeholder poster"""
        placeholder_path = "placeholder_mini.png"
        if not os.path.exists(placeholder_path):
            pixmap = QPixmap(MINI_POSTER_SIZE)
            pixmap.fill(Qt.lightGray)
            pixmap.save(placeholder_path)
        return placeholder_path
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        key = event.key()
        
        if key == Qt.Key_F11:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
            return
        
        if key in (Qt.Key_Escape, Qt.Key_Backspace):
            if self.stack.currentWidget() == self.episodes_page:
                self.stack.setCurrentWidget(self.library_page)
                self.series_grid.setFocus()
                return
        
        if key == Qt.Key_F5:
            self.scan_library()
            return
        
        if event.modifiers() & Qt.ControlModifier:
            if key == Qt.Key_F:
                self.header.search_bar.setFocus()
                self.header.search_bar.selectAll()
                return
        
        super().keyPressEvent(event)