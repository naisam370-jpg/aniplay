import sys, os, json, subprocess
from functools import partial

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QListWidget, QListWidgetItem, QStackedWidget, QFrame, QSpacerItem,
    QSizePolicy, QMessageBox, QPushButton, QDialog, QLineEdit,
    QStyle, QFileDialog, QCheckBox
)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize, QTimer

from cover_cache import precache_covers, ensure_episode_thumbnail


LIBRARY_PATH = os.path.abspath("library")
COVERS_PATH = os.path.abspath("covers")
THUMBS_PATH = os.path.abspath(os.path.join(os.path.expanduser("~"), ".aniplay_thumbs"))
CONFIG_PATH = os.path.abspath("config.json")

POSTER_SIZE = QSize(220, 310)   # series cover (portrait)
THUMB_SIZE  = QSize(320, 180)   # episode thumb (16:9)


# -----------------------
# Config Helpers
# -----------------------
def load_settings():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_settings(data):
    with open(CONFIG_PATH, "w") as f:
        json.dump(data, f, indent=2)


# -----------------------
# Settings Dialog
# -----------------------
class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(400, 250)

        layout = QVBoxLayout(self)

        # Library path setting
        self.library_label = QLabel("Library Folder:")
        self.library_path = QLineEdit()
        self.library_btn = QPushButton("Browse")
        self.library_btn.setIcon(self.style().standardIcon(QStyle.SP_DirOpenIcon))
        self.library_btn.clicked.connect(self._choose_library)

        library_layout = QHBoxLayout()
        library_layout.addWidget(self.library_path)
        library_layout.addWidget(self.library_btn)

        # Covers path setting
        self.covers_label = QLabel("Covers Folder:")
        self.covers_path = QLineEdit()
        self.covers_btn = QPushButton("Browse")
        self.covers_btn.setIcon(self.style().standardIcon(QStyle.SP_DirOpenIcon))
        self.covers_btn.clicked.connect(self._choose_covers)

        covers_layout = QHBoxLayout()
        covers_layout.addWidget(self.covers_path)
        covers_layout.addWidget(self.covers_btn)

        # Refresh button
        self.refresh_btn = QPushButton("Refresh Library")
        self.refresh_btn.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        self.refresh_btn.clicked.connect(self._refresh_library)

        # Save button
        self.save_btn = QPushButton("Save")
        self.save_btn.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
        self.save_btn.clicked.connect(self.accept)

        layout.addWidget(self.library_label)
        layout.addLayout(library_layout)
        layout.addWidget(self.covers_label)
        layout.addLayout(covers_layout)
        layout.addWidget(self.refresh_btn)
        layout.addWidget(self.save_btn)

        # Load saved settings if available
        self.load_settings()

    def _choose_library(self):
        path = QFileDialog.getExistingDirectory(self, "Select Library Folder")
        if path:
            self.library_path.setText(path)

    def _choose_covers(self):
        path = QFileDialog.getExistingDirectory(self, "Select Covers Folder")
        if path:
            self.covers_path.setText(path)

    def _refresh_library(self):
        # Save current settings first
        settings = self.save_settings()

        # Trigger library + cover refresh
        self.parent().populate_series()
        precache_covers(settings["library_path"], settings["covers_path"])

        QMessageBox.information(self, "AniPlay", "Library and covers refreshed.")

    def save_settings(self):
        settings = {
            "library_path": self.library_path.text(),
            "covers_path": self.covers_path.text(),
        }
        with open("settings.json", "w") as f:
            json.dump(settings, f, indent=4)
        return settings

    def load_settings(self):
        if os.path.exists("settings.json"):
            with open("settings.json", "r") as f:
                settings = json.load(f)
                self.library_path.setText(settings.get("library_path", ""))
                self.covers_path.setText(settings.get("covers_path", ""))


# -----------------------
# UI Components
# -----------------------
class HeaderBar(QFrame):
    def __init__(self, title="AniPlay"):
        super().__init__()
        self.setObjectName("HeaderBar")
        self.setFixedHeight(64)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 10, 18, 10)
        layout.setSpacing(16)

        self.title = QLabel(title)
        self.title.setObjectName("HeaderTitle")
        self.title.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        self.hint = QLabel("Arrows • Enter • Esc/Backspace • F11 fullscreen")
        self.hint.setObjectName("HeaderHint")
        self.hint.setAlignment(Qt.AlignVCenter | Qt.AlignRight)

        self.settings_btn = QPushButton()
        self.settings_btn.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
        self.settings_btn.setFlat(True)
        self.settings_btn.setFixedSize(32, 32)

        layout.addWidget(self.title, 0, Qt.AlignVCenter)
        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        layout.addWidget(self.hint, 0, Qt.AlignVCenter)
        layout.addWidget(self.settings_btn, 0, Qt.AlignVCenter)


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
    def __init__(self, title):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.header = HeaderBar(title)
        self.layout.addWidget(self.header)
        self.body = QWidget()
        self.body_layout = QVBoxLayout(self.body)
        self.body_layout.setContentsMargins(24, 18, 24, 24)
        self.body_layout.setSpacing(12)
        self.layout.addWidget(self.body)


# -----------------------
# Main Window
# -----------------------
class AniPlayWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AniPlay")
        self.setMinimumSize(1200, 720)

        cfg = load_settings()
        self.library_path = cfg.get("library_path", LIBRARY_PATH)
        self.covers_path = cfg.get("covers_path", COVERS_PATH)
        self.start_fullscreen = cfg.get("start_fullscreen", False)

        os.makedirs(self.library_path, exist_ok=True)
        os.makedirs(self.covers_path, exist_ok=True)
        os.makedirs(THUMBS_PATH, exist_ok=True)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Pages
        self.seriesPage = NetflixPage("AniPlay")
        self.episodesPage = NetflixPage("AniPlay")
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

        # Settings button
        self.seriesPage.header.settings_btn.clicked.connect(self.open_settings)

        # Styling
        self._apply_styles()

        # Populate series after a tick
        QTimer.singleShot(0, self.populate_series)

        # Fullscreen toggle via F11
        self._fullscreen = False
        if self.start_fullscreen:
            self.showFullScreen()
            self._fullscreen = True
        else:
            self.showMaximized()

    # -----------------------
    # Data / Population
    # -----------------------
    def populate_series(self):
        self.seriesGrid.clear()
        if not os.path.isdir(self.library_path):
            QMessageBox.warning(self, "AniPlay", f"Library not found:\n{self.library_path}")
            return

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
            thumb = ensure_episode_thumbnail(fpath, THUMBS_PATH, seek="00:00:15", width=THUMB_SIZE.width())
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

    def open_settings(self):
        dlg = SettingsDialog(self)
        if dlg.exec_():
            cfg = dlg.save_settings()
            self.library_path = cfg.get("library_path", LIBRARY_PATH)
            self.covers_path = cfg.get("covers_path", COVERS_PATH)
            self.start_fullscreen = cfg.get("start_fullscreen", False)
            self.populate_series()

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

    def _apply_styles(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #0f0f10; }
            #HeaderBar { background-color: #141416; border-bottom: 1px solid #232326; }
            #HeaderTitle { color: #ffffff; font-size: 20px; font-weight: 700; }
            #HeaderHint { color: #b9b9bd; font-size: 12px; }
            #SectionTitle { color: #ffffff; font-size: 18px; font-weight: 600; margin: 6px 2px 6px 2px; }
            QListWidget#SeriesGrid, QListWidget#EpisodeGrid {
                background-color: #0f0f10;
                border: none;
                color: #e7e7ea;
                font-size: 13px;
            }
            QListWidget::item { margin: 6px; padding: 6px 4px 10px 4px; border-radius: 10px; }
            QListWidget::item:selected { background-color: #1f2a36; border: 2px solid #2491ff; }
            QListWidget::item:hover { background-color: #17181c; }
        """)


# -----------------------
# Entry Point
# -----------------------
def main():
    precache_covers(LIBRARY_PATH, COVERS_PATH)

    app = QApplication(sys.argv)
    app.setApplicationName("AniPlay")

    win = AniPlayWindow()
    win.show()  # fullscreen handled inside init
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
