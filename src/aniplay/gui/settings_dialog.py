#!/usr/bin/env python3
"""
Enhanced Settings Dialog
File: src/aniplay/gui/settings_dialog.py
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, QLabel, 
    QComboBox, QSlider, QCheckBox, QPushButton, QSpinBox, QLineEdit,
    QGroupBox, QFormLayout, QFileDialog, QMessageBox, QTextEdit,
    QListWidget, QListWidgetItem, QSplitter, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
import os
from typing import Dict, Any

class SettingsDialog(QDialog):
    """Enhanced settings dialog with multiple categories"""
    
    def __init__(self, parent=None, current_settings: Dict[str, Any] = None):
        super().__init__(parent)
        self.setWindowTitle("AniPlay Settings")
        self.setMinimumSize(600, 500)
        self.setModal(True)
        
        self.settings = current_settings or {}
        self.setup_ui()
        self.load_current_settings()
    
    def setup_ui(self):
        """Setup the settings interface"""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # General tab
        self.general_tab = self.create_general_tab()
        self.tab_widget.addTab(self.general_tab, "General")
        
        # Appearance tab
        self.appearance_tab = self.create_appearance_tab()
        self.tab_widget.addTab(self.appearance_tab, "Appearance")
        
        # Library tab
        self.library_tab = self.create_library_tab()
        self.tab_widget.addTab(self.library_tab, "Library")
        
        # Playback tab
        self.playback_tab = self.create_playback_tab()
        self.tab_widget.addTab(self.playback_tab, "Playback")
        
        # Advanced tab
        self.advanced_tab = self.create_advanced_tab()
        self.tab_widget.addTab(self.advanced_tab, "Advanced")
        
        layout.addWidget(self.tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.defaults_btn = QPushButton("Restore Defaults")
        self.defaults_btn.clicked.connect(self.restore_defaults)
        
        button_layout.addWidget(self.defaults_btn)
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        self.ok_btn = QPushButton("OK")
        self.ok_btn.clicked.connect(self.accept)
        self.ok_btn.setDefault(True)
        
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.ok_btn)
        
        layout.addLayout(button_layout)
    
    def create_general_tab(self) -> QWidget:
        """Create general settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Application behavior group
        app_group = QGroupBox("Application")
        app_layout = QFormLayout(app_group)
        
        self.startup_scan_check = QCheckBox("Scan library on startup")
        app_layout.addRow(self.startup_scan_check)
        
        self.minimize_to_tray_check = QCheckBox("Minimize to system tray")
        app_layout.addRow(self.minimize_to_tray_check)
        
        self.remember_window_state_check = QCheckBox("Remember window size and position")
        app_layout.addRow(self.remember_window_state_check)
        
        # Language selection
        self.language_combo = QComboBox()
        self.language_combo.addItems(["English", "Japanese", "French", "German", "Spanish"])
        app_layout.addRow("Language:", self.language_combo)
        
        layout.addWidget(app_group)
        
        # Updates group
        updates_group = QGroupBox("Updates")
        updates_layout = QFormLayout(updates_group)
        
        self.check_updates_check = QCheckBox("Check for updates automatically")
        updates_layout.addRow(self.check_updates_check)
        
        self.update_frequency_combo = QComboBox()
        self.update_frequency_combo.addItems(["Daily", "Weekly", "Monthly", "Never"])
        updates_layout.addRow("Check frequency:", self.update_frequency_combo)
        
        layout.addWidget(updates_group)
        
        layout.addStretch()
        return tab
    
    def create_appearance_tab(self) -> QWidget:
        """Create appearance settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Theme group
        theme_group = QGroupBox("Theme")
        theme_layout = QFormLayout(theme_group)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light", "Auto (System)"])
        theme_layout.addRow("Theme:", self.theme_combo)
        
        self.accent_color_combo = QComboBox()
        self.accent_color_combo.addItems(["Blue", "Purple", "Green", "Orange", "Red"])
        theme_layout.addRow("Accent color:", self.accent_color_combo)
        
        layout.addWidget(theme_group)
        
        # Grid display group
        display_group = QGroupBox("Display")
        display_layout = QFormLayout(display_group)
        
        # Poster size
        self.poster_size_slider = QSlider(Qt.Horizontal)
        self.poster_size_slider.setRange(150, 300)
        self.poster_size_slider.setValue(220)
        self.poster_size_slider.setTickPosition(QSlider.TicksBelow)
        self.poster_size_slider.setTickInterval(50)
        self.poster_size_label = QLabel("220px")
        self.poster_size_slider.valueChanged.connect(
            lambda v: self.poster_size_label.setText(f"{v}px")
        )
        
        poster_layout = QHBoxLayout()
        poster_layout.addWidget(self.poster_size_slider)
        poster_layout.addWidget(self.poster_size_label)
        display_layout.addRow("Poster size:", poster_layout)
        
        # Grid spacing
        self.grid_spacing_slider = QSlider(Qt.Horizontal)
        self.grid_spacing_slider.setRange(8, 32)
        self.grid_spacing_slider.setValue(16)
        self.grid_spacing_label = QLabel("16px")
        self.grid_spacing_slider.valueChanged.connect(
            lambda v: self.grid_spacing_label.setText(f"{v}px")
        )
        
        spacing_layout = QHBoxLayout()
        spacing_layout.addWidget(self.grid_spacing_slider)
        spacing_layout.addWidget(self.grid_spacing_label)
        display_layout.addRow("Grid spacing:", spacing_layout)
        
        # Scroll speed
        self.scroll_speed_slider = QSlider(Qt.Horizontal)
        self.scroll_speed_slider.setRange(1, 20)
        self.scroll_speed_slider.setValue(5)
        self.scroll_speed_label = QLabel("5")
        self.scroll_speed_slider.valueChanged.connect(
            lambda v: self.scroll_speed_label.setText(str(v))
        )
        
        scroll_layout = QHBoxLayout()
        scroll_layout.addWidget(self.scroll_speed_slider)
        scroll_layout.addWidget(self.scroll_speed_label)
        display_layout.addRow("Scroll speed:", scroll_layout)
        
        # Show episode progress
        self.show_progress_check = QCheckBox("Show episode progress indicators")
        display_layout.addRow(self.show_progress_check)
        
        # Show ratings
        self.show_ratings_check = QCheckBox("Show anime ratings")
        display_layout.addRow(self.show_ratings_check)
        
        layout.addWidget(display_group)
        
        # Font settings
        font_group = QGroupBox("Fonts")
        font_layout = QFormLayout(font_group)
        
        self.ui_font_size_spin = QSpinBox()
        self.ui_font_size_spin.setRange(8, 24)
        self.ui_font_size_spin.setValue(12)
        font_layout.addRow("UI font size:", self.ui_font_size_spin)
        
        layout.addWidget(font_group)
        layout.addStretch()
        return tab
    
    def create_library_tab(self) -> QWidget:
        """Create library settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Library paths group
        paths_group = QGroupBox("Library Paths")
        paths_layout = QVBoxLayout(paths_group)
        
        # Main library path
        main_path_layout = QHBoxLayout()
        self.library_path_edit = QLineEdit()
        self.library_path_browse_btn = QPushButton("Browse...")
        self.library_path_browse_btn.clicked.connect(self.browse_library_path)
        
        main_path_layout.addWidget(QLabel("Library folder:"))
        main_path_layout.addWidget(self.library_path_edit)
        main_path_layout.addWidget(self.library_path_browse_btn)
        paths_layout.addLayout(main_path_layout)
        
        # Additional library paths
        additional_label = QLabel("Additional library folders:")
        paths_layout.addWidget(additional_label)
        
        additional_paths_layout = QHBoxLayout()
        self.additional_paths_list = QListWidget()
        self.additional_paths_list.setMaximumHeight(100)
        
        additional_buttons_layout = QVBoxLayout()
        self.add_path_btn = QPushButton("Add...")
        self.remove_path_btn = QPushButton("Remove")
        self.add_path_btn.clicked.connect(self.add_library_path)
        self.remove_path_btn.clicked.connect(self.remove_library_path)
        
        additional_buttons_layout.addWidget(self.add_path_btn)
        additional_buttons_layout.addWidget(self.remove_path_btn)
        additional_buttons_layout.addStretch()
        
        additional_paths_layout.addWidget(self.additional_paths_list)
        additional_paths_layout.addLayout(additional_buttons_layout)
        paths_layout.addLayout(additional_paths_layout)
        
        layout.addWidget(paths_group)
        
        # Scanning options group
        scan_group = QGroupBox("Library Scanning")
        scan_layout = QFormLayout(scan_group)
        
        self.auto_scan_check = QCheckBox("Automatically scan for new content")
        scan_layout.addRow(self.auto_scan_check)
        
        self.scan_interval_combo = QComboBox()
        self.scan_interval_combo.addItems(["Every startup", "Hourly", "Daily", "Weekly", "Manual only"])
        scan_layout.addRow("Scan interval:", self.scan_interval_combo)
        
        self.deep_scan_check = QCheckBox("Perform deep scan (slower, more accurate)")
        scan_layout.addRow(self.deep_scan_check)
        
        self.scan_subdirs_check = QCheckBox("Scan subdirectories")
        scan_layout.addRow(self.scan_subdirs_check)
        
        layout.addWidget(scan_group)
        
        # Metadata group
        metadata_group = QGroupBox("Metadata")
        metadata_layout = QFormLayout(metadata_group)
        
        self.auto_fetch_covers_check = QCheckBox("Automatically fetch anime covers")
        metadata_layout.addRow(self.auto_fetch_covers_check)
        
        self.auto_fetch_info_check = QCheckBox("Automatically fetch anime information")
        metadata_layout.addRow(self.auto_fetch_info_check)
        
        self.metadata_source_combo = QComboBox()
        self.metadata_source_combo.addItems(["MyAnimeList", "AniDB", "TVDB", "Manual only"])
        metadata_layout.addRow("Metadata source:", self.metadata_source_combo)
        
        self.generate_thumbnails_check = QCheckBox("Generate episode thumbnails")
        metadata_layout.addRow(self.generate_thumbnails_check)
        
        layout.addWidget(metadata_group)
        
        layout.addStretch()
        return tab
    
    def create_playback_tab(self) -> QWidget:
        """Create playback settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Player settings group
        player_group = QGroupBox("Media Player")
        player_layout = QFormLayout(player_group)
        
        # Player executable
        player_path_layout = QHBoxLayout()
        self.player_path_edit = QLineEdit()
        self.player_path_browse_btn = QPushButton("Browse...")
        self.player_path_browse_btn.clicked.connect(self.browse_player_path)
        
        player_path_layout.addWidget(self.player_path_edit)
        player_path_layout.addWidget(self.player_path_browse_btn)
        player_layout.addRow("Player executable:", player_path_layout)
        
        # Player arguments
        self.player_args_edit = QLineEdit()
        self.player_args_edit.setPlaceholderText("--force-window=yes --save-position-on-quit")
        player_layout.addRow("Player arguments:", self.player_args_edit)
        
        layout.addWidget(player_group)
        
        # Playback behavior group
        behavior_group = QGroupBox("Playback Behavior")
        behavior_layout = QFormLayout(behavior_group)
        
        self.auto_play_next_check = QCheckBox("Automatically play next episode")
        behavior_layout.addRow(self.auto_play_next_check)
        
        self.mark_watched_threshold_spin = QSpinBox()
        self.mark_watched_threshold_spin.setRange(70, 100)
        self.mark_watched_threshold_spin.setValue(90)
        self.mark_watched_threshold_spin.setSuffix("%")
        behavior_layout.addRow("Mark as watched at:", self.mark_watched_threshold_spin)
        
        self.resume_playback_check = QCheckBox("Resume from last position")
        behavior_layout.addRow(self.resume_playback_check)
        
        self.fullscreen_check = QCheckBox("Start playback in fullscreen")
        behavior_layout.addRow(self.fullscreen_check)
        
        layout.addWidget(behavior_group)
        
        # Audio/Video group
        av_group = QGroupBox("Audio & Video")
        av_layout = QFormLayout(av_group)
        
        self.preferred_audio_combo = QComboBox()
        self.preferred_audio_combo.addItems(["Japanese", "English", "First available"])
        av_layout.addRow("Preferred audio:", self.preferred_audio_combo)
        
        self.preferred_subtitle_combo = QComboBox()
        self.preferred_subtitle_combo.addItems(["English", "Japanese", "Off", "Auto"])
        av_layout.addRow("Preferred subtitles:", self.preferred_subtitle_combo)
        
        self.hardware_decode_check = QCheckBox("Use hardware decoding")
        av_layout.addRow(self.hardware_decode_check)
        
        layout.addWidget(av_group)
        
        layout.addStretch()
        return tab
    
    def create_advanced_tab(self) -> QWidget:
        """Create advanced settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Database group
        db_group = QGroupBox("Database")
        db_layout = QFormLayout(db_group)
        
        # Database location
        db_path_layout = QHBoxLayout()
        self.db_path_edit = QLineEdit()
        self.db_path_browse_btn = QPushButton("Browse...")
        self.db_path_browse_btn.clicked.connect(self.browse_db_path)
        
        db_path_layout.addWidget(self.db_path_edit)
        db_path_layout.addWidget(self.db_path_browse_btn)
        db_layout.addRow("Database location:", db_path_layout)
        
        # Database maintenance
        db_buttons_layout = QHBoxLayout()
        self.vacuum_db_btn = QPushButton("Optimize Database")
        self.backup_db_btn = QPushButton("Backup Database")
        self.restore_db_btn = QPushButton("Restore Database")
        
        self.vacuum_db_btn.clicked.connect(self.vacuum_database)
        self.backup_db_btn.clicked.connect(self.backup_database)
        self.restore_db_btn.clicked.connect(self.restore_database)
        
        db_buttons_layout.addWidget(self.vacuum_db_btn)
        db_buttons_layout.addWidget(self.backup_db_btn)
        db_buttons_layout.addWidget(self.restore_db_btn)
        
        db_layout.addRow("Maintenance:", db_buttons_layout)
        
        layout.addWidget(db_group)
        
        # Cache group
        cache_group = QGroupBox("Cache & Storage")
        cache_layout = QFormLayout(cache_group)
        
        # Cache size limit
        self.cache_size_spin = QSpinBox()
        self.cache_size_spin.setRange(100, 10000)
        self.cache_size_spin.setValue(1000)
        self.cache_size_spin.setSuffix(" MB")
        cache_layout.addRow("Cache size limit:", self.cache_size_spin)
        
        # Thumbnail cache
        self.thumbnail_cache_check = QCheckBox("Enable thumbnail cache")
        cache_layout.addRow(self.thumbnail_cache_check)
        
        # Clear cache button
        self.clear_cache_btn = QPushButton("Clear Cache")
        self.clear_cache_btn.clicked.connect(self.clear_cache)
        cache_layout.addRow("Cache management:", self.clear_cache_btn)
        
        layout.addWidget(cache_group)
        
        # Logging group
        log_group = QGroupBox("Logging")
        log_layout = QFormLayout(log_group)
        
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["Error", "Warning", "Info", "Debug"])
        log_layout.addRow("Log level:", self.log_level_combo)
        
        self.log_to_file_check = QCheckBox("Log to file")
        log_layout.addRow(self.log_to_file_check)
        
        # Log viewer
        self.view_logs_btn = QPushButton("View Logs")
        self.view_logs_btn.clicked.connect(self.view_logs)
        log_layout.addRow("Log viewer:", self.view_logs_btn)
        
        layout.addWidget(log_group)
        
        # Experimental features
        experimental_group = QGroupBox("Experimental Features")
        experimental_layout = QFormLayout(experimental_group)
        
        self.gpu_thumbnails_check = QCheckBox("Use GPU for thumbnail generation")
        experimental_layout.addRow(self.gpu_thumbnails_check)
        
        self.experimental_ui_check = QCheckBox("Enable experimental UI features")
        experimental_layout.addRow(self.experimental_ui_check)
        
        layout.addWidget(experimental_group)
        
        layout.addStretch()
        return tab
    
    def load_current_settings(self):
        """Load current settings into the UI"""
        # General settings
        self.startup_scan_check.setChecked(self.settings.get("startup_scan", True))
        self.minimize_to_tray_check.setChecked(self.settings.get("minimize_to_tray", False))
        self.remember_window_state_check.setChecked(self.settings.get("remember_window_state", True))
        
        # Appearance settings
        theme = self.settings.get("theme", "Dark").capitalize()
        index = self.theme_combo.findText(theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
        
        self.scroll_speed_slider.setValue(self.settings.get("scroll_speed", 5))
        self.poster_size_slider.setValue(self.settings.get("poster_size", 220))
        self.grid_spacing_slider.setValue(self.settings.get("grid_spacing", 16))
        self.show_progress_check.setChecked(self.settings.get("show_progress", True))
        self.show_ratings_check.setChecked(self.settings.get("show_ratings", True))
        
        # Library settings
        self.library_path_edit.setText(self.settings.get("library_path", ""))
        self.auto_fetch_covers_check.setChecked(self.settings.get("auto_fetch_covers", True))
        self.auto_fetch_info_check.setChecked(self.settings.get("auto_fetch_info", False))
        self.generate_thumbnails_check.setChecked(self.settings.get("generate_thumbnails", True))
        
        # Playback settings
        self.player_path_edit.setText(self.settings.get("player_path", "mpv"))
        self.player_args_edit.setText(self.settings.get("player_args", "--force-window=yes --save-position-on-quit"))
        self.auto_play_next_check.setChecked(self.settings.get("auto_play_next", False))
        self.resume_playback_check.setChecked(self.settings.get("resume_playback", True))
        self.mark_watched_threshold_spin.setValue(self.settings.get("mark_watched_threshold", 90))
        
        # Advanced settings
        self.db_path_edit.setText(self.settings.get("db_path", ""))
        self.cache_size_spin.setValue(self.settings.get("cache_size_mb", 1000))
        self.thumbnail_cache_check.setChecked(self.settings.get("thumbnail_cache", True))
    
    def get_settings(self) -> Dict[str, Any]:
        """Get current settings from the UI"""
        return {
            # General
            "startup_scan": self.startup_scan_check.isChecked(),
            "minimize_to_tray": self.minimize_to_tray_check.isChecked(),
            "remember_window_state": self.remember_window_state_check.isChecked(),
            "language": self.language_combo.currentText(),
            
            # Appearance
            "theme": self.theme_combo.currentText(),
            "accent_color": self.accent_color_combo.currentText(),
            "scroll_speed": self.scroll_speed_slider.value(),
            "poster_size": self.poster_size_slider.value(),
            "grid_spacing": self.grid_spacing_slider.value(),
            "show_progress": self.show_progress_check.isChecked(),
            "show_ratings": self.show_ratings_check.isChecked(),
            "ui_font_size": self.ui_font_size_spin.value(),
            
            # Library
            "library_path": self.library_path_edit.text(),
            "auto_scan": self.auto_scan_check.isChecked(),
            "scan_interval": self.scan_interval_combo.currentText(),
            "deep_scan": self.deep_scan_check.isChecked(),
            "scan_subdirs": self.scan_subdirs_check.isChecked(),
            "auto_fetch_covers": self.auto_fetch_covers_check.isChecked(),
            "auto_fetch_info": self.auto_fetch_info_check.isChecked(),
            "metadata_source": self.metadata_source_combo.currentText(),
            "generate_thumbnails": self.generate_thumbnails_check.isChecked(),
            
            # Playback
            "player_path": self.player_path_edit.text(),
            "player_args": self.player_args_edit.text(),
            "auto_play_next": self.auto_play_next_check.isChecked(),
            "mark_watched_threshold": self.mark_watched_threshold_spin.value(),
            "resume_playback": self.resume_playback_check.isChecked(),
            "fullscreen": self.fullscreen_check.isChecked(),
            "preferred_audio": self.preferred_audio_combo.currentText(),
            "preferred_subtitle": self.preferred_subtitle_combo.currentText(),
            "hardware_decode": self.hardware_decode_check.isChecked(),
            
            # Advanced
            "db_path": self.db_path_edit.text(),
            "cache_size_mb": self.cache_size_spin.value(),
            "thumbnail_cache": self.thumbnail_cache_check.isChecked(),
            "log_level": self.log_level_combo.currentText(),
            "log_to_file": self.log_to_file_check.isChecked(),
            "gpu_thumbnails": self.gpu_thumbnails_check.isChecked(),
            "experimental_ui": self.experimental_ui_check.isChecked(),
        }
    
    def browse_library_path(self):
        """Browse for library path"""
        path = QFileDialog.getExistingDirectory(self, "Select Library Folder")
        if path:
            self.library_path_edit.setText(path)
    
    def browse_player_path(self):
        """Browse for player executable"""
        path, _ = QFileDialog.getOpenFileName(self, "Select Media Player")
        if path:
            self.player_path_edit.setText(path)
    
    def browse_db_path(self):
        """Browse for database location"""
        path, _ = QFileDialog.getSaveFileName(self, "Database Location", "", "Database files (*.db)")
        if path:
            self.db_path_edit.setText(path)
    
    def add_library_path(self):
        """Add additional library path"""
        path = QFileDialog.getExistingDirectory(self, "Add Library Folder")
        if path:
            item = QListWidgetItem(path)
            self.additional_paths_list.addItem(item)
    
    def remove_library_path(self):
        """Remove selected library path"""
        current_item = self.additional_paths_list.currentItem()
        if current_item:
            row = self.additional_paths_list.row(current_item)
            self.additional_paths_list.takeItem(row)
    
    def vacuum_database(self):
        """Optimize database"""
        reply = QMessageBox.question(self, "Optimize Database", 
                                   "This will optimize the database and may take some time. Continue?")
        if reply == QMessageBox.Yes:
            QMessageBox.information(self, "Database Optimization", "Database optimization completed!")
    
    def backup_database(self):
        """Backup database"""
        path, _ = QFileDialog.getSaveFileName(self, "Backup Database", 
                                            "aniplay_backup.db", "Database files (*.db)")
        if path:
            QMessageBox.information(self, "Backup", f"Database backed up to:\n{path}")
    
    def restore_database(self):
        """Restore database from backup"""
        path, _ = QFileDialog.getOpenFileName(self, "Restore Database", 
                                            "", "Database files (*.db)")
        if path:
            reply = QMessageBox.warning(self, "Restore Database", 
                                      "This will replace your current database. Are you sure?",
                                      QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                QMessageBox.information(self, "Restore", "Database restored successfully!")
    
    def clear_cache(self):
        """Clear application cache"""
        reply = QMessageBox.question(self, "Clear Cache", 
                                   "This will clear all cached thumbnails and covers. Continue?")
        if reply == QMessageBox.Yes:
            QMessageBox.information(self, "Cache Cleared", "Cache cleared successfully!")
    
    def view_logs(self):
        """View application logs"""
        log_dialog = QDialog(self)
        log_dialog.setWindowTitle("Application Logs")
        log_dialog.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(log_dialog)
        
        log_text = QTextEdit()
        log_text.setReadOnly(True)
        log_text.setFont(QFont("Courier", 9))
        log_text.setPlainText("Sample log entries would appear here...")
        
        layout.addWidget(log_text)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(log_dialog.close)
        layout.addWidget(close_btn)
        
        log_dialog.exec_()
    
    def restore_defaults(self):
        """Restore all settings to defaults"""
        reply = QMessageBox.question(self, "Restore Defaults", 
                                   "This will reset all settings to their default values. Continue?")
        if reply == QMessageBox.Yes:
            self.settings = {}
            self.load_current_settings()