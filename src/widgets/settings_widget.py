from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QTextEdit, QHBoxLayout, QApplication, QCheckBox, QLineEdit, QMessageBox
from PySide6.QtCore import Qt, Signal
from src.core.library_scanner import scan_library
from src.core.database_manager import DatabaseManager
from src.core.settings_manager import SettingsManager
import os
import shutil # Import shutil

class SettingsWidget(QWidget):
    scan_completed = Signal(list)
    scan_requested = Signal()

    def __init__(self, db_manager: DatabaseManager, settings_manager: SettingsManager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.settings_manager = settings_manager
        self.selected_path = self.settings_manager.get("library_path")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title_label = QLabel("Settings")
        font = title_label.font()
        font.setPointSize(18)
        font.setBold(True)
        title_label.setFont(font)
        layout.addWidget(title_label)

        # --- Library Path ---
        path_layout = QHBoxLayout()
        self.path_label = QLabel()
        self.btn_select_folder = QPushButton("Select Folder")
        self.btn_select_folder.clicked.connect(self.select_folder)
        path_layout.addWidget(self.path_label)
        path_layout.addStretch()
        path_layout.addWidget(self.btn_select_folder)
        layout.addLayout(path_layout)

        # --- Scan Button ---
        self.btn_scan = QPushButton("Scan Library Now")
        self.btn_scan.clicked.connect(self.scan_requested.emit)
        layout.addWidget(self.btn_scan)
        
        # --- Auto-scan Checkbox ---
        self.chk_auto_scan = QCheckBox("Automatically scan library on startup")
        self.chk_auto_scan.setChecked(self.settings_manager.get("auto_scan", False))
        self.chk_auto_scan.stateChanged.connect(self.on_auto_scan_changed)
        layout.addWidget(self.chk_auto_scan)

        # --- API Settings ---
        api_label = QLabel("API Settings")
        font.setPointSize(14)
        api_label.setFont(font)
        layout.addWidget(api_label)

        token_layout = QHBoxLayout()
        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText("Anilist Access Token")
        self.token_input.setEchoMode(QLineEdit.Password)
        self.token_input.setText(self.settings_manager.get("anilist_token", ""))
        
        self.btn_save_token = QPushButton("Save Token")
        self.btn_save_token.clicked.connect(self.on_save_token)
        
        token_layout.addWidget(self.token_input)
        token_layout.addWidget(self.btn_save_token)
        layout.addLayout(token_layout)

        # --- Data Management ---
        data_label = QLabel("Data Management")
        font.setPointSize(14)
        data_label.setFont(font)
        layout.addWidget(data_label)

        self.btn_clear_covers = QPushButton("Clear Cover Cache")
        self.btn_clear_covers.clicked.connect(self.on_clear_cover_cache)
        layout.addWidget(self.btn_clear_covers)

        self.btn_clear_db = QPushButton("Clear Library Database")
        self.btn_clear_db.clicked.connect(self.on_clear_database)
        layout.addWidget(self.btn_clear_db)

        layout.addStretch()

        self.update_path_label()

    def update_path_label(self):
        """Updates the path label and scan button based on the selected_path."""
        if self.selected_path:
            self.path_label.setText(f"Library Folder: {self.selected_path}")
            self.btn_scan.setEnabled(True)
        else:
            self.path_label.setText("No library folder selected.")
            self.btn_scan.setEnabled(False)

    def select_folder(self):
        """Opens a dialog to select a directory and saves it."""
        path = QFileDialog.getExistingDirectory(self, "Select Library Folder")
        if path:
            self.selected_path = path
            self.settings_manager.set("library_path", self.selected_path)
            self.update_path_label()

    def on_auto_scan_changed(self, state):
        """Saves the auto-scan setting when the checkbox is changed."""
        is_checked = state == Qt.Checked
        self.settings_manager.set("auto_scan", is_checked)

    def on_save_token(self):
        """Saves the Anilist access token to settings."""
        token = self.token_input.text()
        self.settings_manager.set("anilist_token", token)
        print("Anilist token saved.")

    def on_clear_cover_cache(self):
        """Clears all downloaded cover images and updates the database."""
        reply = QMessageBox.question(self, 'Clear Cover Cache',
                                     "Are you sure you want to delete all downloaded cover images? This action cannot be undone.",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            covers_dir = "covers"
            if os.path.exists(covers_dir):
                shutil.rmtree(covers_dir) # Use shutil.rmtree to delete directory and its contents
                os.makedirs(covers_dir) # Recreate empty directory
                print(f"Cleared all files from {covers_dir}")
            
            self.db_manager.clear_all_cover_paths() # Update database
            QMessageBox.information(self, 'Cover Cache Cleared', "All cover images have been cleared.")
            self.scan_completed.emit([]) # Trigger a reload of the library

    def on_clear_database(self):
        """Clears the entire library database and cover cache."""
        reply = QMessageBox.question(self, 'Clear Library Database',
                                     "Are you sure you want to delete the entire library database and all cover images? This action cannot be undone.",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # Delete database file
            db_path = self.db_manager.db_path
            if os.path.exists(db_path):
                os.remove(db_path)
                print(f"Deleted database file: {db_path}")
            
            # Clear cover cache
            covers_dir = "covers"
            if os.path.exists(covers_dir):
                shutil.rmtree(covers_dir)
                os.makedirs(covers_dir)
                print(f"Cleared all files from {covers_dir}")

            QMessageBox.information(self, 'Library Cleared', "The entire library database and cover cache have been cleared. The application will now restart.")
            QApplication.quit() # Restart the application
