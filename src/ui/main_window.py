import sys
import os
from pathlib import Path

from PySide6.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QPushButton
from PySide6.QtCore import QThreadPool, Qt
from PySide6.QtGui import QPixmap

# Ensure the app can find the generated UI and core modules
# ROOT_DIR is /aniplay
ROOT_DIR = Path(__file__).parent.parent.parent.absolute()
if str(ROOT_DIR / "src") not in sys.path:
    sys.path.insert(0, str(ROOT_DIR / "src"))

from .ui_mainwindow import Ui_MainWindow
from core.scanner import ScannerWorker


class MainWindow(QMainWindow):
    def __init__(self, launcher):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.core = launcher  # Access to DatabaseManager
        self.threadpool = QThreadPool()

        # 1. Sidebar Navigation Connections
        self.ui.btn_home.clicked.connect(lambda: self.ui.stacked_widget.setCurrentIndex(0))
        self.ui.btn_library.clicked.connect(lambda: self.ui.stacked_widget.setCurrentIndex(1))
        self.ui.btn_settings.clicked.connect(lambda: self.ui.stacked_widget.setCurrentIndex(4))

        # 2. Settings Page Connections
        self.ui.btn_browse_path.clicked.connect(self.browse_folder)
        self.ui.btn_start_scan.clicked.connect(self.run_library_scan)

        # Start on the Library page
        self.display_library()

    def browse_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select Anime Library")
        if path:
            self.ui.edit_library_path.setText(path)

    def run_library_scan(self):
        path = self.ui.edit_library_path.text()
        if not os.path.exists(path):
            QMessageBox.warning(self, "Path Error", "Please select a valid folder.")
            return

        self.ui.btn_start_scan.setEnabled(False)

        # Create Worker (passing target path and DB instance)
        worker = ScannerWorker(path, self.core.db)
        worker.signals.progress.connect(self.ui.lbl_scan_status.setText)
        worker.signals.finished.connect(self.on_scan_finished)

        self.threadpool.start(worker)

    def on_scan_finished(self, count):
        self.ui.btn_start_scan.setEnabled(True)
        self.ui.lbl_scan_status.setText(f"Done! Found {count} episodes.")
        self.display_library()

    def display_library(self):
        """Clears and re-fills the grid with anime posters."""
        # Clear existing widgets in the grid
        while self.ui.library_grid.count():
            item = self.ui.library_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Fetch from DB
        anime_list = self.core.db.get_library()

        row, col = 0, 0
        for anime_id, title, poster_path, rating in anime_list:
            btn = QPushButton()
            btn.setFixedSize(160, 240)

            # If poster exists, show it; otherwise, show text
            if poster_path and os.path.exists(poster_path):
                btn.setStyleSheet(f"border-image: url({poster_path.replace('\\', '/')}); border-radius: 5px;")
            else:
                btn.setText(title)

            btn.clicked.connect(lambda ch=False, a_id=anime_id: self.show_anime_details(a_id))
            self.ui.library_grid.addWidget(btn, row, col)

            col += 1
            if col > 4:  # 5 posters per row
                col = 0
                row += 1

        self.ui.stacked_widget.setCurrentIndex(1)

    def show_anime_details(self, anime_id):
        """Switches to Page 2 and fills in metadata."""
        # This is where we will fetch specific season/episode data
        self.ui.stacked_widget.setCurrentIndex(2)
        print(f"Loading Anime ID: {anime_id}")
