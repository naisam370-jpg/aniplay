from PySide6.QtWidgets import QWidget, QFileDialog, QMessageBox, QApplication, QCheckBox, QLineEdit
from PySide6.QtCore import Qt, Signal
from src.core.database_manager import DatabaseManager
from src.core.settings_manager import SettingsManager
import os
import shutil
from .ui_settings_widget import Ui_Form as Ui_SettingsWidget

class SettingsWidget(QWidget, Ui_SettingsWidget):
    scan_completed = Signal(list)
    scan_requested = Signal()

    def __init__(self, db_manager: DatabaseManager, settings_manager: SettingsManager, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        
        self.db_manager = db_manager
        self.settings_manager = settings_manager
        self.selected_path = self.settings_manager.get("library_path")

        # --- Connect Signals ---
        self.btn_select_folder.clicked.connect(self.select_folder)
        self.btn_scan.clicked.connect(self.scan_requested.emit)
        self.chk_auto_scan.stateChanged.connect(self.on_auto_scan_changed)
        self.btn_save_token.clicked.connect(self.on_save_token)
        self.btn_clear_covers.clicked.connect(self.on_clear_cover_cache)
        self.btn_clear_db.clicked.connect(self.on_clear_database)

        # --- Set Initial Values ---
        self.chk_auto_scan.setChecked(self.settings_manager.get("auto_scan", False))
        self.token_input.setText(self.settings_manager.get("anilist_token", ""))
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
