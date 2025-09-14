import sys, os, subprocess
from functools import partial

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QListWidget, QListWidgetItem, QStackedWidget, QFrame, QSpacerItem,
    QSizePolicy, QMessageBox, QPushButton, QDialog, QComboBox, QCheckBox, QSlider,
    QStyle, QAbstractItemView
)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize, QTimer, pyqtSignal
import PyQt5.QtCore as QtCore

from cover_fetcher import precache_covers, ensure_episode_thumbnail
from settings import load_settings, save_settings

# -------------------------
# Paths
# -------------------------
LIBRARY_PATH = os.path.abspath("library")
COVERS_PATH = os.path.abspath("covers")
THUMBS_PATH = os.path.abspath(os.path.join(os.path.expanduser("~"), ".aniplay_thumbs"))

POSTER_SIZE = QSize(220, 310)   # series cover (portrait)
THUMB_SIZE  = QSize(320, 180)   # episode thumb (16:9)


# -------------------------
# UI Components
# -------------------------
class HeaderBar(QFrame):
    def __init__(self, title="AniPlay", parent=None):
        super().__init__(parent)
        self.setObjectName("HeaderBar")
        self.setFixedHeight(64)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 10, 18, 10)
        layout.setSpacing(16)

        self.title = QLabel(title)
        self.title.setObjectName("HeaderTitle")
        self.title.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        self.hint = QLabel("Arrows to navigate • Enter to open/play • Esc/Backspace to go back • F11 fullscreen")
        self.hint.setObjectName("HeaderHint")
        self.hint.setAlignment(Qt.AlignVCenter | Qt.AlignRight)

        # Buttons
        self.refresh_btn = QPushButton()
        self.refresh_btn.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        self.refresh_btn.setToolTip("Refresh Library")
        self.refresh_btn.setFixedSize(32, 32)

        self.settings_btn = QPushButton()
        self.settings_btn.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
        self.settings_btn.setToolTip("Settings")
        self.settings_btn.setFixedSize(32, 32)

        layout.addWidget(self.title, 0, Qt.AlignVCenter)
        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        layout.addWidget(self.refresh_btn, 0, Qt.AlignVCenter)
        layout.addWidget(self.settings_btn, 0, Qt.AlignVCenter)
        layout.addWidget(self.hint, 0, Qt.AlignVCenter)


class SeriesGrid(QListWidget):
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
        self.setGridSize(QSize(POSTER_SIZE.width() + 24, POSTER_SIZE.height() + 52))
        self.setSelectionMode(QListWidget.SingleSelection)
        self.setObjectName("SeriesGrid")
        self.setAlternatingRowColors(False)
        self.setVerticalScrollMode(QListWidget.ScrollPerPixel)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFocusPolicy(Qt.StrongFocus)


class EpisodeGrid(QListWidget):
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
        self.setGridSize(QSize(THUMB_SIZE.width() + 24, THUMB_SIZE.height() + 48))
        self.setSelectionMode(QListWidget.SingleSelection)
        self.setObjectName("EpisodeGrid")
        self.setAlternatingRowColors(False)
        self.setVerticalScrollMode(QListWidget.ScrollPerPixel)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFocusPolicy(Qt.StrongFocus)


class NetflixPage(QWidget):
    """Base page with header + body area."""
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.header = HeaderBar(title, parent)
        self.layout.addWidget(self.header)
        self.body = QWidget()
        self.body_layout = QVBoxLayout(self.body)
        self.body_layout.setContentsMargins(24, 18, 24, 24)
        self.body_layout.setSpacing(12)
        self.layout.addWidget(self.body)


# -------------------------
# Settings Dialog
# -------------------------
class SettingsDialog(QDialog):
    settings_changed = QtCore.pyqtSignal(dict)  # emit settings back to MainWindow

    def __init__(self, parent=None, settings=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.settings = settings or {}

        layout = QVBoxLayout()

        # --- Theme selection ---
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Theme:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        self.theme_combo.setCurrentText(self.settings.get("theme", "Light"))
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        layout.addLayout(theme_layout)

        # --- Scroll speed ---
        scroll_layout = QHBoxLayout()
        scroll_label = QLabel("Scroll Speed:")
        self.scroll_slider = QSlider(Qt.Horizontal)
        self.scroll_slider.setRange(1, 20)
        self.scroll_slider.setValue(self.settings.get("scroll_speed", 5))
        scroll_layout.addWidget(scroll_label)
        scroll_layout.addWidget(self.scroll_slider)
        layout.addLayout(scroll_layout)

        # --- Auto-fetch covers ---
        self.cover_check = QCheckBox("Automatically fetch anime covers")
        self.cover_check.setChecked(self.settings.get("auto_fetch_covers", True))
        layout.addWidget(self.cover_check)

        # --- Buttons ---
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Cancel")
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def accept(self):
        """Collect settings and emit to parent before closing"""
        new_settings = {
            "theme": self.theme_combo.currentText(),
            "scroll_speed": self.scroll_slider.value(),
            "auto_fetch_covers": self.cover_check.isChecked()
        }
        self.settings_changed.emit(new_settings)  # notify MainWindow
        super().accept()


# -------------------------
# Main Window
# -------------------------
class AniPlayWindow(QMainWindow):
    def __init__(self, library_path=LIBRARY_PATH, covers_path=COVERS_PATH):
        super().__init__()
        self.setWindowTitle("AniPlay")
        self.setMinimumSize(1200, 720)

        self.library_path = library_path
        self.covers_path = covers_path
        os.makedirs(self.library_path, exist_ok=True)
        os.makedirs(self.covers_path, exist_ok=True)
        os.makedirs(THUMBS_PATH, exist_ok=True)

        # Load settings
        self.settings = load_settings()

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Pages
        self.seriesPage = NetflixPage("AniPlay", self)
        self.episodesPage = NetflixPage("AniPlay", self)
        self.stack.addWidget(self.seriesPage)
        self.stack.addWidget(self.episodesPage)

        # SERIES GRID
        self.seriesGrid = SeriesGrid()
        self.seriesPage.body_layout.addWidget(self.seriesGrid)
        self.seriesGrid.itemActivated.connect(self._open_series_from_item)

        # EPISODE GRID
        self.episodeTitle = QLabel("Episodes")
        self.episodeTitle.setObjectName("SectionTitle")
        self.episodesPage.body_layout.addWidget(self.episodeTitle)
        self.episodeGrid = EpisodeGrid()
        self.episodesPage.body_layout.addWidget(self.episodeGrid)
        self.episodeGrid.itemActivated.connect(self._play_episode_from_item)

        # Header buttons
        self.seriesPage.header.refresh_btn.clicked.connect(self.populate_library)
        self.seriesPage.header.settings_btn.clicked.connect(self.open_settings)

        # Styling
        self._apply_styles(dark=(self.settings.get("theme", "Light") == "Dark"))

        # Populate series after a tick (UI first)
        QTimer.singleShot(0, self.populate_library)

        # Fullscreen toggle via F11
        self._fullscreen = False

    # -----------------------
    # Settings
    # -----------------------
    def open_settings(self):
        dlg = SettingsDialog(self, self.settings)
        dlg.settings_changed.connect(self.apply_settings)  # listen for updates
        dlg.exec_()

    def apply_settings(self, new_settings):
        self.settings.update(new_settings)
        save_settings(self.settings)  # write to JSON

        # Apply theme
        self._apply_styles(dark=(self.settings.get("theme", "Light") == "Dark"))

        # Apply scroll speed
        self.seriesGrid.verticalScrollBar().setSingleStep(self.settings.get("scroll_speed", 5))
        self.episodeGrid.verticalScrollBar().setSingleStep(self.settings.get("scroll_speed", 5))

    # -----------------------
    # Data / Population
    # -----------------------
    def populate_library(self):
        self.seriesGrid.clear()
        if not os.path.isdir(self.library_path):
            QMessageBox.warning(self, "AniPlay", f"Library not found:\n{self.library_path}")
            return

        # Pre-cache covers
        precache_covers(self.library_path, self.covers_path)

        series_folders = [
            d for d in sorted(os.listdir(self.library_path))
            if os.path.isdir(os.path.join(self.library_path, d))
        ]

        for name in series_folders:
            cover_path = os.path.join(self.covers_path, f"{name}.jpg")
            item = QListWidgetItem(name)
            item.setTextAlignment(Qt.AlignHCenter)
            if os.path.exists(cover_path):
                item.setIcon(QIcon(cover_path))
            else:
                placeholder = self._placeholder_poster()
                item.setIcon(QIcon(placeholder))
            item.setData(Qt.UserRole, os.path.join(self.library_path, name))
            self.seriesGrid.addItem(item)

        if self.seriesGrid.count() > 0:
            self.seriesGrid.setCurrentRow(0)
            self.seriesGrid.setFocus()

    def populate_episodes(self, series_name, series_path):
        self.episodeTitle.setText(series_name)
        self.episodeGrid.clear()

        exts = (".mp4", ".mkv", ".avi", ".mov", ".webm")
        files = [
            f for f in sorted(os.listdir(series_path))
            if os.path.isfile(os.path.join(series_path, f)) and f.lower().endswith(exts)
        ]

        for fname in files:
            fpath = os.path.join(series_path, fname)
            thumb = ensure_episode_thumbnail(fpath, THUMBS_PATH, width=THUMB_SIZE.width())
            item = QListWidgetItem(QIcon(thumb) if thumb else QIcon(self._placeholder_thumb()), fname)
            item.setTextAlignment(Qt.AlignHCenter)
            item.setData(Qt.UserRole, fpath)
            self.episodeGrid.addItem(item)

        if self.episodeGrid.count() > 0:
            self.episodeGrid.setCurrentRow(0)
            self.episodeGrid.setFocus()

    # -----------------------
    # Event handlers
    # -----------------------
    def _open_series_from_item(self, item: QListWidgetItem):
        series_path = item.data(Qt.UserRole)
        series_name = os.path.basename(series_path)
        self.populate_episodes(series_name, series_path)
        self.stack.setCurrentWidget(self.episodesPage)

    def _play_episode_from_item(self, item: QListWidgetItem):
        path = item.data(Qt.UserRole)
        if not path or not os.path.exists(path):
            return
        subprocess.Popen(["mpv", "--force-window=yes", path])

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_F11:
            self._fullscreen = not self._fullscreen
            if self._fullscreen:
                self.showFullScreen()
            else:
                self.showNormal()
            return

        if key in (Qt.Key_Escape, Qt.Key_Backspace):
            if self.stack.currentWidget() is self.episodesPage:
                self.stack.setCurrentWidget(self.seriesPage)
                self.seriesGrid.setFocus()
                return

        super().keyPressEvent(event)

    # -----------------------
    # Helpers / Styling
    # -----------------------
    def _placeholder_poster(self):
        p = os.path.join(os.path.dirname(__file__), "placeholder_poster.png")
        if not os.path.exists(p):
            pix = QPixmap(POSTER_SIZE)
            pix.fill(Qt.darkGray)
            pix.save(p)
        return p

    def _placeholder_thumb(self):
        p = os.path.join(os.path.dirname(__file__), "placeholder_thumb.png")
        if not os.path.exists(p):
            pix = QPixmap(THUMB_SIZE)
            pix.fill(Qt.darkGray)
            pix.save(p)
        return p

    def _apply_styles(self, dark=True):
        if dark:
            ttext = "#ffffff"
            bg = "#0f0f10"
            card = "#17181c"
            text = "#E35FFD"
            hint = "#b9b9bd"
            sel = "#2491ff"
        else:
            ttext = "#000000"
            bg = "#f2f2f2"
            card = "#ffffff"
            text = "#B62CF7"
            hint = "#555555"
            sel = "#0078d7"

        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {bg}; }}

            #HeaderBar {{
                background-color: {card};
                border-bottom: 1px solid #232326;
            }}
            #HeaderTitle {{
                color: {ttext};
                font-size: 20px;
                font-weight: 700;
            }}
            #HeaderHint {{
                color: {hint};
                font-size: 12px;
            }}
            #SectionTitle {{
                color: {ttext};
                font-size: 18px;
                font-weight: 600;
                margin: 6px 2px 6px 2px;
            }}

            QListWidget#SeriesGrid, QListWidget#EpisodeGrid {{
                background-color: {bg};
                border: none;
                color: {text};
                font-size: 13px;
            }}
            QListWidget::item {{
                margin: 6px;
                padding: 6px 4px 10px 4px;
                border-radius: 12px;
            }}
            QListWidget::item:selected {{
                background-color: {card};
                border: 2px solid {sel};
            }}
            QListWidget::item:hover {{
                background-color: {card};
                border: 1px solid {sel};
            }}
        """)


# -------------------------
# Main
# -------------------------
def main():
    app = QApplication(sys.argv)
    app.setApplicationName("AniPlay")

    win = AniPlayWindow(LIBRARY_PATH, COVERS_PATH)
    win.showMaximized()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
