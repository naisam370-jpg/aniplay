# gui.py
import sys, os, subprocess
from functools import partial

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QListWidget, QListWidgetItem, QStackedWidget, QFrame, QSpacerItem,
    QSizePolicy, QMessageBox, QPushButton, QFileDialog, QDialog, QFormLayout,
    QLineEdit, QCheckBox, QSpinBox, QStyle
)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize, QTimer

from cover_cache import precache_covers, ensure_episode_thumbnail
import config  # expects the config.py you added earlier

# Paths & sizes
LIBRARY_PATH = os.path.abspath(config.get("library_path") or "library")
COVERS_PATH = os.path.abspath(config.get("covers_path") or "covers")
THUMBS_PATH = os.path.abspath(os.path.join(os.path.expanduser("~"), ".aniplay_thumbs"))

POSTER_SIZE = QSize(220, 310)   # series cover (portrait)
THUMB_SIZE  = QSize(320, 180)   # episode thumb (16:9)


# -----------------------
# Header with Settings button
# -----------------------
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

        layout.addWidget(self.title, 0, Qt.AlignVCenter)
        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # Settings (gear) button
        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setFixedSize(34, 34)
        self.settings_btn.setObjectName("SettingsBtn")
        layout.addWidget(self.settings_btn, 0, Qt.AlignVCenter)

        layout.addWidget(self.hint, 0, Qt.AlignVCenter)
        
        #refresh button
        self.refresh_btn = QPushButton("⟳")
        self.refresh_btn.setFixedSize(34, 34)
        self.refresh_btn.setObjectName("RefreshBtn")
        layout.addWidget(self.refresh_btn, 0, Qt.AlignVCenter)


# -----------------------
# Grids
# -----------------------
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


# -----------------------
# Page container
# -----------------------
class NetflixPage(QWidget):
    """Base page with header + body area."""
    def __init__(self, title, parent=None):
        super().__init__(parent)
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
# Settings Dialog
# -----------------------
class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(600, 420)

        self.cfg = config.load_config()
        self._build_ui()
        # inside HeaderBar.__init__
        self.settings_btn = QPushButton()
        self.settings_btn.setFixedSize(34, 34)
        self.settings_btn.setObjectName("SettingsBtn")

        # use a system gear icon if available
        self.settings_btn.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
        self.settings_btn.setIconSize(QSize(20, 20))


    def _build_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        layout.addLayout(form)

        # Library path
        self.lib_edit = QLineEdit(self.cfg.get("library_path"))
        btn_lib = QPushButton("Browse")
        btn_lib.clicked.connect(self._browse_lib)
        h1 = QHBoxLayout()
        h1.addWidget(self.lib_edit)
        h1.addWidget(btn_lib)
        form.addRow("Library folder:", h1)

        # Covers path
        self.cov_edit = QLineEdit(self.cfg.get("covers_path"))
        btn_cov = QPushButton("Browse")
        btn_cov.clicked.connect(self._browse_cov)
        h2 = QHBoxLayout()
        h2.addWidget(self.cov_edit)
        h2.addWidget(btn_cov)
        form.addRow("Covers folder:", h2)

        # Auto-fetch covers
        self.autofetch_cb = QCheckBox()
        self.autofetch_cb.setChecked(bool(self.cfg.get("auto_fetch_covers", True)))
        form.addRow("Auto-fetch covers:", self.autofetch_cb)

        # Player executable
        self.player_exec = QLineEdit(self.cfg.get("player.executable") or self.cfg.get("player", {}).get("executable", "mpv"))
        form.addRow("Player executable:", self.player_exec)

        # Subtitle font size
        self.sub_font = QSpinBox()
        self.sub_font.setRange(10, 72)
        self.sub_font.setValue(int(self.cfg.get("subtitles.font_size", 24)))
        form.addRow("Subtitle font size:", self.sub_font)

        # Thumbnail size
        self.thumb_size = QSpinBox()
        self.thumb_size.setRange(160, 800)
        self.thumb_size.setValue(int(self.cfg.get("ui.thumbnail_size", 320)))
        form.addRow("Thumbnail width (px):", self.thumb_size)

        # Buttons
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.reset_btn = QPushButton("Reset to Defaults")
        self.clear_btn = QPushButton("Clear thumbnail cache")
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.reset_btn)
        btn_layout.addWidget(self.clear_btn)
        layout.addLayout(btn_layout)

        # Connect
        self.save_btn.clicked.connect(self._save)
        self.reset_btn.clicked.connect(self._reset)
        self.clear_btn.clicked.connect(self._clear_cache)

    def _browse_lib(self):
        p = QFileDialog.getExistingDirectory(self, "Select Library folder", self.lib_edit.text() or os.getcwd())
        if p:
            self.lib_edit.setText(p)

    def _browse_cov(self):
        p = QFileDialog.getExistingDirectory(self, "Select Covers folder", self.cov_edit.text() or os.getcwd())
        if p:
            self.cov_edit.setText(p)

    def _save(self):
        # write into config and save
        config.set("library_path", self.lib_edit.text())
        config.set("covers_path", self.cov_edit.text())
        config.set("auto_fetch_covers", bool(self.autofetch_cb.isChecked()))
        # player.executable path
        config.set("player.executable", self.player_exec.text())
        config.set("subtitles.font_size", int(self.sub_font.value()))
        config.set("ui.thumbnail_size", int(self.thumb_size.value()))
        config.save_config()
        config.ensure_paths_exist(config.load_config())
        QMessageBox.information(self, "Settings", "Saved.")
        self.accept()

    def _reset(self):
        if QMessageBox.question(self, "Reset", "Reset to defaults?") == QMessageBox.Yes:
            config.reset_defaults()
            self.cfg = config.load_config()
            # refresh UI fields
            self.lib_edit.setText(self.cfg.get("library_path"))
            self.cov_edit.setText(self.cfg.get("covers_path"))
            self.autofetch_cb.setChecked(bool(self.cfg.get("auto_fetch_covers", True)))
            self.player_exec.setText(self.cfg.get("player", {}).get("executable", "mpv"))
            self.sub_font.setValue(int(self.cfg.get("subtitles.font_size", 24)))
            self.thumb_size.setValue(int(self.cfg.get("ui.thumbnail_size", 320)))
            QMessageBox.information(self, "Settings", "Reset to defaults.")

    def _clear_cache(self):
        # clear thumbnail cache (THUMBS_PATH)
        try:
            for fn in os.listdir(THUMBS_PATH):
                try:
                    os.remove(os.path.join(THUMBS_PATH, fn))
                except Exception:
                    pass
            QMessageBox.information(self, "Settings", "Thumbnail cache cleared.")
        except Exception as e:
            QMessageBox.warning(self, "Settings", f"Failed to clear cache: {e}")


# -----------------------
# Main Window
# -----------------------
class AniPlayWindow(QMainWindow):
    def __init__(self, library_path=LIBRARY_PATH, covers_path=COVERS_PATH):
        super().__init__()
        self.setWindowTitle("AniPlay")
        self.setMinimumSize(1200, 720)

        # Update paths from config (again) to ensure any saved change reflects
        self.library_path = library_path
        self.covers_path = covers_path
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

        # Wire header settings button
        self.seriesPage.header.settings_btn.clicked.connect(self.open_settings)
        self.episodesPage.header.settings_btn.clicked.connect(self.open_settings)

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

        # Styling
        self._apply_styles()

        # Populate series after a tick (UI first)
        QTimer.singleShot(0, self.populate_series)

        # Fullscreen toggle via F11
        self._fullscreen = False

    # -----------------------
    # Data / Population
    # -----------------------
    def populate_series(self):
        self.seriesGrid.clear()
        cfg = config.load_config()
        self.library_path = cfg.get("library_path") or self.library_path
        self.covers_path = cfg.get("covers_path") or self.covers_path

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
                # fallback placeholder
                placeholder = self._placeholder_poster()
                item.setIcon(QIcon(placeholder))
            # carry series path in data
            item.setData(Qt.UserRole, os.path.join(self.library_path, name))
            self.seriesGrid.addItem(item)

        if self.seriesGrid.count() > 0:
            self.seriesGrid.setCurrentRow(0)
            self.seriesGrid.setFocus()

    def populate_episodes(self, series_name, series_path):
        self.episodeTitle.setText(series_name)
        self.episodeGrid.clear()

        # Episodes = common video extensions
        exts = (".mp4", ".mkv", ".avi", ".mov", ".webm")
        files = [
            f for f in sorted(os.listdir(series_path))
            if os.path.isfile(os.path.join(series_path, f)) and f.lower().endswith(exts)
        ]

        # get thumbnail width from config
        thumb_w = int(config.get("ui.thumbnail_size", THUMB_SIZE.width()))

        for fname in files:
            fpath = os.path.join(series_path, fname)
            thumb = ensure_episode_thumbnail(fpath, THUMBS_PATH, seek="00:00:05", width=thumb_w)
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
    
    # open series on item activation (double-click or Enter)
    def _open_series_from_item(self, item: QListWidgetItem):
        series_path = item.data(Qt.UserRole)
        series_name = os.path.basename(series_path)
        self.populate_episodes(series_name, series_path)
        self.stack.setCurrentWidget(self.episodesPage)

    # play episode on item activation (double-click or Enter)
    def _play_episode_from_item(self, item: QListWidgetItem):
        path = item.data(Qt.UserRole)
        if not path or not os.path.exists(path):
            return
        # Use system mpv for now (backend integration can replace this)
        player_exec = config.get("player.executable", "mpv")
        subprocess.Popen([player_exec, "--force-window=yes", path])
    # open settings dialog
    def open_settings(self):
        dlg = SettingsDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            # settings possibly changed — reload relevant things
            # ensure paths exist, re-run precache if auto-fetch is on
            cfg = config.load_config()
            ensure_pf = config.get("auto_fetch_covers", True)
            config.ensure_paths_exist(cfg)
            if ensure_pf:
                QTimer.singleShot(10, lambda: precache_covers(cfg.get("library_path"), cfg.get("covers_path")))
            # refresh UI
            QTimer.singleShot(50, self.populate_series)
    # global key events
    def keyPressEvent(self, event):
        key = event.key()

        # global
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
        # return path to a generated or bundled placeholder (simple)
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

            #HeaderBar {
                background-color: #141416;
                border-bottom: 1px solid #232326;
            }
            #HeaderTitle {
                color: #ffffff;
                font-size: 20px;
                font-weight: 700;
            }
            #HeaderHint {
                color: #b9b9bd;
                font-size: 12px;
            }
            #SectionTitle {
                color: #ffffff;
                font-size: 18px;
                font-weight: 600;
                margin: 6px 2px 6px 2px;
            }

            QListWidget#SeriesGrid, QListWidget#EpisodeGrid {
                background-color: #0f0f10;
                border: none;
                color: #e7e7ea;
                font-size: 13px;
            }
            QListWidget::item {
                margin: 6px;
                padding: 6px 4px 10px 4px;
                border-radius: 10px;
            }
            QListWidget::item:selected {
                background-color: #1f2a36;
                border: 2px solid #2491ff;
            }
            QListWidget::item:hover {
                background-color: #17181c;
            }
            QPushButton#SettingsBtn {
                border: none;
                border-radius: 6px;
                background: #1f1f22;
                color: #ffffff;
                font-size: 24px;
            }
            QPushButton#SettingsBtn:hover {
                background: #2c2c30;
            }
            QPushButton#RefreshBtn {
                border: none;
                border-radius: 6px;
                background: #1f1f22;
                color: #ffffff;
                font-size: 24px;
            }
            QPushButton#RefreshBtn:hover {
                background: #2c2c30;
            }

        """)


def main():
    # Pre-cache covers (AniList) before launching the UI — use config paths
    cfg = config.load_config()
    libp = cfg.get("library_path") or LIBRARY_PATH
    covp = cfg.get("covers_path") or COVERS_PATH
    os.makedirs(libp, exist_ok=True)
    os.makedirs(covp, exist_ok=True)
    os.makedirs(THUMBS_PATH, exist_ok=True)

    if config.get("auto_fetch_covers", True):
        precache_covers(libp, covp)

    app = QApplication(sys.argv)
    app.setApplicationName("AniPlay")

    win = AniPlayWindow(libp, covp)
    win.showMaximized()  # toggle with F11

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
