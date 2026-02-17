import sys
import os
from pathlib import Path
from PySide6.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QPushButton
from PySide6.QtCore import QThreadPool, Qt
from PySide6.QtGui import QPixmap

ROOT_DIR = Path(__file__).parent.parent.parent.absolute()
if str(ROOT_DIR / "src") not in sys.path:
    sys.path.insert(0, str(ROOT_DIR / "src"))

from .ui_mainwindow import Ui_MainWindow
from core.scanner import ScannerWorker
from ui.episode_item import EpisodeItem


class MainWindow(QMainWindow):
    def __init__(self, launcher):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.core = launcher
        self.threadpool = QThreadPool()

        # Navigation
        self.ui.btn_home.clicked.connect(lambda: self.ui.stacked_widget.setCurrentIndex(0))
        self.ui.btn_library.clicked.connect(lambda: self.ui.stacked_widget.setCurrentIndex(0))
        self.ui.btn_settings.clicked.connect(lambda: self.ui.stacked_widget.setCurrentIndex(3))

        # Settings
        self.ui.btn_browse_path.clicked.connect(self.browse_folder)
        self.ui.btn_start_scan.clicked.connect(self.run_library_scan)

        if hasattr(self.ui, 'btn_back_to_library'):
            self.ui.btn_back_to_library.clicked.connect(lambda: self.ui.stacked_widget.setCurrentIndex(0))

        self.display_library()
        self.ui.stacked_widget.setCurrentIndex(0)

    def browse_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select Anime Library")
        if path: self.ui.edit_library_path.setText(path)

    def run_library_scan(self):
        path = self.ui.edit_library_path.text()
        if not os.path.exists(path):
            QMessageBox.warning(self, "Path Error", "Please select a valid folder.")
            return

        self.ui.btn_start_scan.setEnabled(False)
        worker = ScannerWorker(path, self.core.db)
        worker.signals.progress.connect(self.ui.lbl_scan_status.setText)
        worker.signals.finished.connect(self.on_scan_finished)
        self.threadpool.start(worker)

    def on_scan_finished(self, count):
        self.ui.btn_start_scan.setEnabled(True)
        self.ui.lbl_scan_status.setText(f"Done! Found {count} episodes.")
        self.display_library()

    def display_library(self):
        if not hasattr(self.ui, 'library_grid'): return
        while self.ui.library_grid.count():
            child = self.ui.library_grid.takeAt(0)
            if child.widget(): child.widget().deleteLater()

        anime_list = self.core.db.get_library()
        row, col = 0, 0
        for anime in anime_list:
            anime_id, title, poster, rating = anime
            btn = QPushButton()
            btn.setFixedSize(160, 240)
            btn.setCursor(Qt.PointingHandCursor)

            if poster and os.path.exists(poster):
                btn.setStyleSheet(f"border-image: url({poster.replace('\\', '/')}); border-radius: 5px;")
            else:
                btn.setText(title)
                btn.setStyleSheet("background-color: #222; color: white; border-radius: 5px;")

            btn.clicked.connect(lambda checked=False, a_id=anime_id: self.open_anime_details(a_id))
            self.ui.library_grid.addWidget(btn, row, col)
            col += 1
            if col > 4:
                col = 0
                row += 1

    def open_anime_details(self, anime_id):
        # 1. Fetch Metadata [cite: 15]
        # Data index: 0:id, 1:title, 2:folder, 3:poster, 4:mal_id, 5:rating, 6:synopsis
        anime_data = self.core.db.get_anime_details(anime_id)

        if anime_data:
            # Map database results to UI widgets found in mainwindow.ui
            self.ui.lbl_title.setText(str(anime_data[1]))
            self.ui.lbl_rating.setText(f"⭐ {anime_data[5] if anime_data[5] else 'N/A'}")
            self.ui.lbl_synopsis.setText(str(anime_data[6]) if anime_data[6] else "No synopsis.")

            # Handle the Poster Image
            poster_path = anime_data[3]
            if poster_path and os.path.exists(poster_path):
                pixmap = QPixmap(poster_path)  # QPixmap is now properly defined
                self.ui.lbl_big_poster.setPixmap(pixmap.scaled(
                    self.ui.lbl_big_poster.width(),
                    self.ui.lbl_big_poster.height(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                ))

        # 2. Setup Episode Layout [cite: 17]
        container = self.ui.episode_list_layout
        layout = container if hasattr(container, 'count') else container.layout()
        if layout is None: return

        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Switch to Details Page (Page Index 1)

        self.ui.stacked_widget.setCurrentIndex(1)

        try:
            episodes = self.core.db.get_episodes(anime_id)
            for index, ep in enumerate(episodes):
                # Unpack all 5 columns
                ep_id, file_path, thumb_path, db_title, db_ep_num = ep

                # Logic: Use Number if exists, otherwise Index. Use Title if exists, otherwise "Episode X"
                num = db_ep_num if db_ep_num else index + 1
                title = db_title if db_title else f"Episode {num}"

                item = EpisodeItem(title=title, ep_number=num, thumb_path=thumb_path, file_path=file_path)
                item.clicked.connect(self.play_video)
                layout.addWidget(item)
            layout.addStretch()
        except Exception as e:
            print(f"❌ Error: {e}")

    def play_video(self, file_path):
        print(f"🎬 Playing: {file_path}")