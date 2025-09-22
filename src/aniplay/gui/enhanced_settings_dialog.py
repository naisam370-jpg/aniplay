"""
Integrated Settings Dialog with Database Support
File: src/aniplay/gui/enhanced_settings_dialog.py
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, QLabel, 
    QComboBox, QSlider, QCheckBox, QPushButton, QSpinBox, QLineEdit,
    QGroupBox, QFormLayout, QFileDialog, QMessageBox, QTextEdit,
    QListWidget, QListWidgetItem, QSplitter, QFrame, QProgressBar,
    QButtonGroup, QRadioButton, QColorDialog, QFontComboBox, QScrollArea
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QThread
from PyQt5.QtGui import QFont, QIcon, QColor, QPalette
import os
from pathlib import Path
from typing import Dict, Any, Optional

# Import our settings system
try:
    from ..core.settings_manager import SettingsManager, get_settings
    from ..core.database import DatabaseManager
except ImportError:
    SettingsManager = None
    get_settings = None
    DatabaseManager = None

class SettingsValidationThread(QThread):
    """Background thread for settings validation"""
    validation_complete = pyqtSignal(list)  # List of validation issues
    
    def __init__(self, settings_manager: "SettingsManager"):
        super().__init__()
        self.settings_manager = settings_manager
    
    def run(self):
        """Run validation in background"""
        issues = self.settings_manager.validate_settings()
        self.validation_complete.emit(issues)

class EnhancedSettingsDialog(QDialog):
    """Enhanced settings dialog with full database integration"""
    
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None, settings_manager: Optional[SettingsManager] = None):
        super().__init__(parent)
        self.setWindowTitle("AniPlay Settings")
        self.setMinimumSize(800, 600)
        self.setModal(True)
        
        # Settings manager
        if settings_manager:
            self.settings = settings_manager
        elif get_settings:
            self.settings = get_settings()
        else:
            QMessageBox.critical(self, "Error", "Settings system not available")
            self.reject()
            return
        
        # Track changes
        self.changes_made = False
        self.original_settings = {}
        
        # UI Components
        self.validation_issues = []
        self.validation_thread = None
        
        self.setup_ui()
        self.load_current_settings()
        self.start_validation()
    
    def setup_ui(self):
        """Setup the settings interface"""
        layout = QVBoxLayout(self)
        
        # Create main splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - category list
        self.category_list = QListWidget()
        self.category_list.setMaximumWidth(200)
        self.category_list.setObjectName("CategoryList")
        
        categories = [
            ("General", "🏠"),
            ("Appearance", "🎨"), 
            ("Library", "📚"),
            ("Playback", "▶️"),
            ("Advanced", "⚙️"),
            ("Database", "🗄️"),
            ("About", "ℹ️")
        ]
        
        for name, icon in categories:
            item = QListWidgetItem(f"{icon} {name}")
            item.setData(Qt.UserRole, name.lower())
            self.category_list.addItem(item)
        
        # Right panel - settings content
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        
        # Settings stack
        self.settings_stack = QTabWidget()
        self.settings_stack.setTabPosition(QTabWidget.North)
        self.settings_stack.tabBar().hide()  # We'll use the left panel for navigation
        
        # Create all settings tabs
        self.general_tab = self.create_general_tab()
        self.appearance_tab = self.create_appearance_tab()
        self.library_tab = self.create_library_tab()
        self.playback_tab = self.create_playback_tab()
        self.advanced_tab = self.create_advanced_tab()
        self.database_tab = self.create_database_tab()
        self.about_tab = self.create_about_tab()
        
        self.settings_stack.addTab(self.general_tab, "General")
        self.settings_stack.addTab(self.appearance_tab, "Appearance")
        self.settings_stack.addTab(self.library_tab, "Library")
        self.settings_stack.addTab(self.playback_tab, "Playback")
        self.settings_stack.addTab(self.advanced_tab, "Advanced")
        self.settings_stack.addTab(self.database_tab, "Database")
        self.settings_stack.addTab(self.about_tab, "About")
        
        self.content_layout.addWidget(self.settings_stack)
        
        # Validation status
        self.validation_frame = QFrame()
        self.validation_layout = QHBoxLayout(self.validation_frame)
        self.validation_label = QLabel("✅ Settings validation in progress...")
        self.validation_layout.addWidget(self.validation_label)
        self.content_layout.addWidget(self.validation_frame)
        
        # Add to splitter
        splitter.addWidget(self.category_list)
        splitter.addWidget(self.content_widget)
        splitter.setSizes([200, 600])
        
        layout.addWidget(splitter)
        
        # Button bar
        button_layout = QHBoxLayout()
        
        # Left side buttons
        self.export_btn = QPushButton("Export Settings")
        self.import_btn = QPushButton("Import Settings")
        self.reset_btn = QPushButton("Reset to Defaults")
        
        self.export_btn.clicked.connect(self.export_settings)
        self.import_btn.clicked.connect(self.import_settings)
        self.reset_btn.clicked.connect(self.reset_settings)
        
        button_layout.addWidget(self.export_btn)
        button_layout.addWidget(self.import_btn)
        button_layout.addWidget(self.reset_btn)
        button_layout.addStretch()
        
        # Right side buttons
        self.apply_btn = QPushButton("Apply")
        self.cancel_btn = QPushButton("Cancel")
        self.ok_btn = QPushButton("OK")
        
        self.apply_btn.clicked.connect(self.apply_settings)
        self.cancel_btn.clicked.connect(self.reject)
        self.ok_btn.clicked.connect(self.accept_settings)
        self.ok_btn.setDefault(True)
        
        button_layout.addWidget(self.apply_btn)
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.ok_btn)
        
        layout.addLayout(button_layout)
        
        # Connect navigation
        self.category_list.currentItemChanged.connect(self.on_category_changed)
        self.category_list.setCurrentRow(0)
        
        # Apply styling
        self.apply_styles()
    
    def create_general_tab(self) -> QWidget:
        """Create general settings tab"""
        tab = QScrollArea()
        content = QWidget()
        layout = QVBoxLayout(content)
        
        # Application behavior
        app_group = QGroupBox("Application Behavior")
        app_layout = QFormLayout(app_group)
        
        self.language_combo = QComboBox()
        self.language_combo.addItems(["English", "Japanese", "French", "German", "Spanish"])
        app_layout.addRow("Language:", self.language_combo)
        
        self.startup_scan_check = QCheckBox("Scan library on startup")
        app_layout.addRow(self.startup_scan_check)
        
        self.minimize_to_tray_check = QCheckBox("Minimize to system tray")
        app_layout.addRow(self.minimize_to_tray_check)
        
        self.remember_window_state_check = QCheckBox("Remember window size and position")
        app_layout.addRow(self.remember_window_state_check)
        
        self.max_recent_items_spin = QSpinBox()
        self.max_recent_items_spin.setRange(5, 100)
        app_layout.addRow("Max recent items:", self.max_recent_items_spin)
        
        layout.addWidget(app_group)
        
        # Updates and notifications
        updates_group = QGroupBox("Updates & Notifications")
        updates_layout = QFormLayout(updates_group)
        
        self.check_updates_check = QCheckBox("Check for updates automatically")
        updates_layout.addRow(self.check_updates_check)
        
        self.update_frequency_combo = QComboBox()
        self.update_frequency_combo.addItems(["Daily", "Weekly", "Monthly", "Never"])
        updates_layout.addRow("Update frequency:", self.update_frequency_combo)
        
        self.send_analytics_check = QCheckBox("Send anonymous usage analytics")
        updates_layout.addRow(self.send_analytics_check)
        
        layout.addWidget(updates_group)
        
        layout.addStretch()
        tab.setWidget(content)
        return tab
    
    def create_appearance_tab(self) -> QWidget:
        """Create appearance settings tab"""
        tab = QScrollArea()
        content = QWidget()
        layout = QVBoxLayout(content)
        
        # Theme settings
        theme_group = QGroupBox("Theme & Colors")
        theme_layout = QFormLayout(theme_group)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light", "Auto (System)"])
        self.theme_combo.currentTextChanged.connect(self.on_setting_changed)
        theme_layout.addRow("Theme:", self.theme_combo)
        
        self.accent_color_combo = QComboBox()
        self.accent_color_combo.addItems(["Blue", "Purple", "Green", "Orange", "Red"])
        self.accent_color_combo.currentTextChanged.connect(self.on_setting_changed)
        theme_layout.addRow("Accent color:", self.accent_color_combo)
        
        # Custom color button
        self.custom_color_btn = QPushButton("Choose Custom Color")
        self.custom_color_btn.clicked.connect(self.choose_custom_color)
        theme_layout.addRow("Custom accent:", self.custom_color_btn)
        
        layout.addWidget(theme_group)
        
        # Display settings
        display_group = QGroupBox("Display Options")
        display_layout = QFormLayout(display_group)
        
        # Poster size
        poster_layout = QHBoxLayout()
        self.poster_size_slider = QSlider(Qt.Horizontal)
        self.poster_size_slider.setRange(150, 350)
        self.poster_size_slider.setTickPosition(QSlider.TicksBelow)
        self.poster_size_slider.setTickInterval(50)
        self.poster_size_label = QLabel("220px")
        self.poster_size_slider.valueChanged.connect(
            lambda v: self.poster_size_label.setText(f"{v}px")
        )
        self.poster_size_slider.valueChanged.connect(self.on_setting_changed)
        
        poster_layout.addWidget(self.poster_size_slider)
        poster_layout.addWidget(self.poster_size_label)
        display_layout.addRow("Poster size:", poster_layout)
        
        # Grid spacing
        spacing_layout = QHBoxLayout()
        self.grid_spacing_slider = QSlider(Qt.Horizontal)
        self.grid_spacing_slider.setRange(8, 40)
        self.grid_spacing_label = QLabel("16px")
        self.grid_spacing_slider.valueChanged.connect(
            lambda v: self.grid_spacing_label.setText(f"{v}px")
        )
        self.grid_spacing_slider.valueChanged.connect(self.on_setting_changed)
        
        spacing_layout.addWidget(self.grid_spacing_slider)
        spacing_layout.addWidget(self.grid_spacing_label)
        display_layout.addRow("Grid spacing:", spacing_layout)
        
        # UI options
        self.show_progress_check = QCheckBox("Show episode progress indicators")
        self.show_progress_check.toggled.connect(self.on_setting_changed)
        display_layout.addRow(self.show_progress_check)
        
        self.show_ratings_check = QCheckBox("Show anime ratings")
        self.show_ratings_check.toggled.connect(self.on_setting_changed)
        display_layout.addRow(self.show_ratings_check)
        
        self.show_thumbnails_check = QCheckBox("Show episode thumbnails")
        self.show_thumbnails_check.toggled.connect(self.on_setting_changed)
        display_layout.addRow(self.show_thumbnails_check)
        
        layout.addWidget(display_group)
        
        # Font settings
        font_group = QGroupBox("Fonts")
        font_layout = QFormLayout(font_group)
        
        self.ui_font_combo = QFontComboBox()
        self.ui_font_combo.currentFontChanged.connect(self.on_setting_changed)
        font_layout.addRow("UI font:", self.ui_font_combo)
        
        self.ui_font_size_spin = QSpinBox()
        self.ui_font_size_spin.setRange(8, 24)
        self.ui_font_size_spin.valueChanged.connect(self.on_setting_changed)
        font_layout.addRow("Font size:", self.ui_font_size_spin)
        
        layout.addWidget(font_group)
        layout.addStretch()
        tab.setWidget(content)
        return tab
    
    def create_library_tab(self) -> QWidget:
        """Create library settings tab"""
        tab = QScrollArea()
        content = QWidget()
        layout = QVBoxLayout(content)
        
        # Library paths
        paths_group = QGroupBox("Library Paths")
        paths_layout = QVBoxLayout(paths_group)
        
        # Main library path
        main_path_layout = QHBoxLayout()
        self.library_path_edit = QLineEdit()
        self.library_path_edit.textChanged.connect(self.on_setting_changed)
        self.library_path_browse_btn = QPushButton("Browse...")
        self.library_path_browse_btn.clicked.connect(self.browse_library_path)
        
        main_path_layout.addWidget(QLabel("Main library:"))
        main_path_layout.addWidget(self.library_path_edit)
        main_path_layout.addWidget(self.library_path_browse_btn)
        paths_layout.addLayout(main_path_layout)
        
        # Additional paths
        additional_label = QLabel("Additional library paths:")
        paths_layout.addWidget(additional_label)
        
        additional_layout = QHBoxLayout()
        self.additional_paths_list = QListWidget()
        self.additional_paths_list.setMaximumHeight(100)
        
        buttons_layout = QVBoxLayout()
        self.add_path_btn = QPushButton("Add...")
        self.remove_path_btn = QPushButton("Remove")
        self.add_path_btn.clicked.connect(self.add_library_path)
        self.remove_path_btn.clicked.connect(self.remove_library_path)
        
        buttons_layout.addWidget(self.add_path_btn)
        buttons_layout.addWidget(self.remove_path_btn)
        buttons_layout.addStretch()
        
        additional_layout.addWidget(self.additional_paths_list)
        additional_layout.addLayout(buttons_layout)
        paths_layout.addLayout(additional_layout)
        
        layout.addWidget(paths_group)
        
        # Scanning options
        scan_group = QGroupBox("Library Scanning")
        scan_layout = QFormLayout(scan_group)
        
        self.auto_scan_check = QCheckBox("Automatically scan for changes")
        self.auto_scan_check.toggled.connect(self.on_setting_changed)
        scan_layout.addRow(self.auto_scan_check)
        
        self.scan_interval_combo = QComboBox()
        self.scan_interval_combo.addItems(["Startup Only", "Hourly", "Daily", "Weekly", "Manual"])
        self.scan_interval_combo.currentTextChanged.connect(self.on_setting_changed)
        scan_layout.addRow("Scan interval:", self.scan_interval_combo)
        
        self.deep_scan_check = QCheckBox("Deep scan (slower, more thorough)")
        self.deep_scan_check.toggled.connect(self.on_setting_changed)
        scan_layout.addRow(self.deep_scan_check)
        
        self.scan_subdirs_check = QCheckBox("Scan subdirectories")
        self.scan_subdirs_check.toggled.connect(self.on_setting_changed)
        scan_layout.addRow(self.scan_subdirs_check)
        
        self.min_file_size_spin = QSpinBox()
        self.min_file_size_spin.setRange(1, 1000)
        self.min_file_size_spin.setSuffix(" MB")
        self.min_file_size_spin.valueChanged.connect(self.on_setting_changed)
        scan_layout.addRow("Min file size:", self.min_file_size_spin)
        
        layout.addWidget(scan_group)
        
        # Metadata options
        metadata_group = QGroupBox("Metadata & Thumbnails")
        metadata_layout = QFormLayout(metadata_group)
        
        self.auto_fetch_covers_check = QCheckBox("Automatically fetch anime covers")
        self.auto_fetch_covers_check.toggled.connect(self.on_setting_changed)
        metadata_layout.addRow(self.auto_fetch_covers_check)
        
        self.auto_fetch_info_check = QCheckBox("Automatically fetch anime information")
        self.auto_fetch_info_check.toggled.connect(self.on_setting_changed)
        metadata_layout.addRow(self.auto_fetch_info_check)
        
        self.metadata_source_combo = QComboBox()
        self.metadata_source_combo.addItems(["MyAnimeList", "AniDB", "TVDB", "Manual Only"])
        self.metadata_source_combo.currentTextChanged.connect(self.on_setting_changed)
        metadata_layout.addRow("Metadata source:", self.metadata_source_combo)
        
        self.generate_thumbnails_check = QCheckBox("Generate episode thumbnails")
        self.generate_thumbnails_check.toggled.connect(self.on_setting_changed)
        metadata_layout.addRow(self.generate_thumbnails_check)
        
        layout.addWidget(metadata_group)
        layout.addStretch()
        tab.setWidget(content)
        return tab
    
    def create_playback_tab(self) -> QWidget:
        """Create playback settings tab"""
        tab = QScrollArea()
        content = QWidget()
        layout = QVBoxLayout(content)
        
        # Player settings
        player_group = QGroupBox("Media Player")
        player_layout = QFormLayout(player_group)
        
        # Player path
        player_path_layout = QHBoxLayout()
        self.player_path_edit = QLineEdit()
        self.player_path_edit.textChanged.connect(self.on_setting_changed)
        self.player_path_browse_btn = QPushButton("Browse...")
        self.player_path_browse_btn.clicked.connect(self.browse_player_path)
        
        player_path_layout.addWidget(self.player_path_edit)
        player_path_layout.addWidget(self.player_path_browse_btn)
        player_layout.addRow("Player executable:", player_path_layout)
        
        # Player arguments
        self.player_args_edit = QLineEdit()
        self.player_args_edit.setPlaceholderText("--force-window=yes --save-position-on-quit")
        self.player_args_edit.textChanged.connect(self.on_setting_changed)
        player_layout.addRow("Player arguments:", self.player_args_edit)
        
        layout.addWidget(player_group)
        
        # Playback behavior
        behavior_group = QGroupBox("Playback Behavior")
        behavior_layout = QFormLayout(behavior_group)
        
        self.auto_play_next_check = QCheckBox("Automatically play next episode")
        self.auto_play_next_check.toggled.connect(self.on_setting_changed)
        behavior_layout.addRow(self.auto_play_next_check)
        
        self.resume_playback_check = QCheckBox("Resume from last position")
        self.resume_playback_check.toggled.connect(self.on_setting_changed)
        behavior_layout.addRow(self.resume_playback_check)
        
        self.fullscreen_playback_check = QCheckBox("Start playback in fullscreen")
        self.fullscreen_playback_check.toggled.connect(self.on_setting_changed)
        behavior_layout.addRow(self.fullscreen_playback_check)
        
        # Mark as watched threshold
        threshold_layout = QHBoxLayout()
        self.watched_threshold_spin = QSpinBox()
        self.watched_threshold_spin.setRange(50, 100)
        self.watched_threshold_spin.setSuffix("%")
        self.watched_threshold_spin.valueChanged.connect(self.on_setting_changed)
        threshold_layout.addWidget(self.watched_threshold_spin)
        threshold_layout.addStretch()
        behavior_layout.addRow("Mark as watched at:", threshold_layout)
        
        # Volume settings
        volume_layout = QHBoxLayout()
        self.default_volume_spin = QSpinBox()
        self.default_volume_spin.setRange(0, 100)
        self.default_volume_spin.setSuffix("%")
        self.default_volume_spin.valueChanged.connect(self.on_setting_changed)
        
        self.remember_volume_check = QCheckBox("Remember volume")
        self.remember_volume_check.toggled.connect(self.on_setting_changed)
        
        volume_layout.addWidget(self.default_volume_spin)
        volume_layout.addWidget(self.remember_volume_check)
        behavior_layout.addRow("Default volume:", volume_layout)
        
        layout.addWidget(behavior_group)
        
        # Audio & Video preferences
        av_group = QGroupBox("Audio & Video Preferences")
        av_layout = QFormLayout(av_group)
        
        self.preferred_audio_combo = QComboBox()
        self.preferred_audio_combo.addItems(["Japanese", "English", "First Available"])
        self.preferred_audio_combo.currentTextChanged.connect(self.on_setting_changed)
        av_layout.addRow("Preferred audio:", self.preferred_audio_combo)
        
        self.preferred_subtitle_combo = QComboBox()
        self.preferred_subtitle_combo.addItems(["English", "Japanese", "Off", "Auto"])
        self.preferred_subtitle_combo.currentTextChanged.connect(self.on_setting_changed)
        av_layout.addRow("Preferred subtitles:", self.preferred_subtitle_combo)
        
        self.hardware_decode_check = QCheckBox("Use hardware decoding (if available)")
        self.hardware_decode_check.toggled.connect(self.on_setting_changed)
        av_layout.addRow(self.hardware_decode_check)
        
        layout.addWidget(av_group)
        layout.addStretch()
        tab.setWidget(content)
        return tab
    
    def create_advanced_tab(self) -> QWidget:
        """Create advanced settings tab"""
        tab = QScrollArea()
        content = QWidget()
        layout = QVBoxLayout(content)
        
        # Performance settings
        perf_group = QGroupBox("Performance")
        perf_layout = QFormLayout(perf_group)
        
        self.use_native_backend_check = QCheckBox("Use native C++ backend (recommended)")
        self.use_native_backend_check.toggled.connect(self.on_setting_changed)
        perf_layout.addRow(self.use_native_backend_check)
        
        self.concurrent_scans_spin = QSpinBox()
        self.concurrent_scans_spin.setRange(1, 16)
        self.concurrent_scans_spin.valueChanged.connect(self.on_setting_changed)
        perf_layout.addRow("Concurrent scan threads:", self.concurrent_scans_spin)
        
        self.gpu_thumbnails_check = QCheckBox("Use GPU for thumbnail generation")
        self.gpu_thumbnails_check.toggled.connect(self.on_setting_changed)
        perf_layout.addRow(self.gpu_thumbnails_check)
        
        layout.addWidget(perf_group)
        
        # Cache settings
        cache_group = QGroupBox("Cache & Storage")
        cache_layout = QFormLayout(cache_group)
        
        cache_size_layout = QHBoxLayout()
        self.cache_size_spin = QSpinBox()
        self.cache_size_spin.setRange(100, 10000)
        self.cache_size_spin.setSuffix(" MB")
        self.cache_size_spin.valueChanged.connect(self.on_setting_changed)
        
        self.clear_cache_btn = QPushButton("Clear Cache")
        self.clear_cache_btn.clicked.connect(self.clear_cache)
        
        cache_size_layout.addWidget(self.cache_size_spin)
        cache_size_layout.addWidget(self.clear_cache_btn)
        cache_layout.addRow("Cache size limit:", cache_size_layout)
        
        self.thumbnail_cache_check = QCheckBox("Enable thumbnail cache")
        self.thumbnail_cache_check.toggled.connect(self.on_setting_changed)
        cache_layout.addRow(self.thumbnail_cache_check)
        
        layout.addWidget(cache_group)
        
        # Logging settings
        log_group = QGroupBox("Logging & Debug")
        log_layout = QFormLayout(log_group)
        
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["Error", "Warning", "Info", "Debug"])
        self.log_level_combo.currentTextChanged.connect(self.on_setting_changed)
        log_layout.addRow("Log level:", self.log_level_combo)
        
        self.log_to_file_check = QCheckBox("Log to file")
        self.log_to_file_check.toggled.connect(self.on_setting_changed)
        log_layout.addRow(self.log_to_file_check)
        
        self.debug_logging_check = QCheckBox("Enable debug logging")
        self.debug_logging_check.toggled.connect(self.on_setting_changed)
        log_layout.addRow(self.debug_logging_check)
        
        # Log viewer button
        self.view_logs_btn = QPushButton("View Logs")
        self.view_logs_btn.clicked.connect(self.view_logs)
        log_layout.addRow("Log viewer:", self.view_logs_btn)
        
        layout.addWidget(log_group)
        
        # Experimental features
        experimental_group = QGroupBox("Experimental Features")
        experimental_layout = QFormLayout(experimental_group)
        
        self.experimental_features_check = QCheckBox("Enable experimental features")
        self.experimental_features_check.toggled.connect(self.on_setting_changed)
        experimental_layout.addRow(self.experimental_features_check)
        
        experimental_warning = QLabel("⚠️ Experimental features may be unstable")
        experimental_warning.setStyleSheet("color: orange; font-style: italic;")
        experimental_layout.addRow(experimental_warning)
        
        layout.addWidget(experimental_group)
        layout.addStretch()
        tab.setWidget(content)
        return tab
    
    def create_database_tab(self) -> QWidget:
        """Create database management tab"""
        tab = QScrollArea()
        content = QWidget()
        layout = QVBoxLayout(content)
        
        # Database info
        info_group = QGroupBox("Database Information")
        info_layout = QFormLayout(info_group)
        
        self.db_path_label = QLabel("Loading...")
        info_layout.addRow("Database file:", self.db_path_label)
        
        self.db_size_label = QLabel("Loading...")
        info_layout.addRow("File size:", self.db_size_label)
        
        self.db_records_label = QLabel("Loading...")
        info_layout.addRow("Total records:", self.db_records_label)
        
        layout.addWidget(info_group)
        
        # Database maintenance
        maintenance_group = QGroupBox("Database Maintenance")
        maintenance_layout = QVBoxLayout(maintenance_group)
        
        # Progress bar for operations
        self.db_progress = QProgressBar()
        self.db_progress.setVisible(False)
        maintenance_layout.addWidget(self.db_progress)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        self.optimize_db_btn = QPushButton("Optimize Database")
        self.backup_db_btn = QPushButton("Create Backup")
        self.restore_db_btn = QPushButton("Restore from Backup")
        
        self.optimize_db_btn.clicked.connect(self.optimize_database)
        self.backup_db_btn.clicked.connect(self.backup_database)
        self.restore_db_btn.clicked.connect(self.restore_database)
        
        buttons_layout.addWidget(self.optimize_db_btn)
        buttons_layout.addWidget(self.backup_db_btn)
        buttons_layout.addWidget(self.restore_db_btn)
        
        maintenance_layout.addLayout(buttons_layout)
        
        # Backup settings
        backup_settings_layout = QFormLayout()
        
        self.backup_database_check = QCheckBox("Automatically backup database")
        self.backup_database_check.toggled.connect(self.on_setting_changed)
        backup_settings_layout.addRow(self.backup_database_check)
        
        self.backup_frequency_combo = QComboBox()
        self.backup_frequency_combo.addItems(["Daily", "Weekly", "Monthly"])
        self.backup_frequency_combo.currentTextChanged.connect(self.on_setting_changed)
        backup_settings_layout.addRow("Backup frequency:", self.backup_frequency_combo)
        
        maintenance_layout.addLayout(backup_settings_layout)
        layout.addWidget(maintenance_group)
        
        # Statistics
        stats_group = QGroupBox("Statistics")
        stats_layout = QFormLayout(stats_group)
        
        # We'll populate these when the tab is shown
        self.stats_labels = {}
        stat_names = [
            ("Total Anime", "total_anime"),
            ("Total Episodes", "total_episodes"),
            ("Watched Episodes", "watched_episodes"),
            ("Favorites", "favorites"),
            ("Watch Time", "total_watch_time_hours")
        ]
        
        for display_name, key in stat_names:
            label = QLabel("Loading...")
            self.stats_labels[key] = label
            stats_layout.addRow(f"{display_name}:", label)
        
        layout.addWidget(stats_group)
        layout.addStretch()
        tab.setWidget(content)
        return tab
    
    def create_about_tab(self) -> QWidget:
        """Create about/info tab"""
        tab = QScrollArea()
        content = QWidget()
        layout = QVBoxLayout(content)
        
        # Application info
        app_group = QGroupBox("Application Information")
        app_layout = QFormLayout(app_group)
        
        app_layout.addRow("Name:", QLabel("AniPlay"))
        app_layout.addRow("Version:", QLabel("1.0.0"))
        app_layout.addRow("Author:", QLabel("AniPlay Developer"))
        
        # System info
        import platform
        app_layout.addRow("Platform:", QLabel(platform.system()))
        app_layout.addRow("Python:", QLabel(platform.python_version()))
        
        # Backend status
        try:
            from ..core.media_backend import is_native_backend_available
            backend_status = "Available" if is_native_backend_available() else "Not Available"
        except ImportError:
            backend_status = "Unknown"
        
        app_layout.addRow("C++ Backend:", QLabel(backend_status))
        
        layout.addWidget(app_group)
        
        # Links and credits
        credits_group = QGroupBox("Credits & Links")
        credits_layout = QVBoxLayout(credits_group)
        
        credits_text = QTextEdit()
        credits_text.setReadOnly(True)
        credits_text.setMaximumHeight(150)
        credits_text.setPlainText(
            "AniPlay is built with:\n"
            "• PyQt5 - Cross-platform GUI toolkit\n"
            "• libmpv - Media player library\n"
            "• FFmpeg - Multimedia processing\n"
            "• SQLite - Database engine\n"
            "• pybind11 - Python/C++ bindings\n\n"
            "Special thanks to the open source community!"
        )
        
        credits_layout.addWidget(credits_text)
        layout.addWidget(credits_group)
        
        layout.addStretch()
        tab.setWidget(content)
        return tab
    
    def load_current_settings(self):
        """Load current settings into UI"""
        try:
            # Store original settings for change detection
            self.original_settings = {
                'appearance': self.settings.get_category_dict('appearance'),
                'library': self.settings.get_category_dict('library'),
                'playback': self.settings.get_category_dict('playback'),
                'general': self.settings.get_category_dict('general'),
                'advanced': self.settings.get_category_dict('advanced'),
            }
            
            # Load general settings
            self.language_combo.setCurrentText(self.settings.general.language.title())
            self.startup_scan_check.setChecked(self.settings.general.startup_scan)
            self.minimize_to_tray_check.setChecked(self.settings.general.minimize_to_tray)
            self.remember_window_state_check.setChecked(self.settings.general.remember_window_state)
            self.max_recent_items_spin.setValue(self.settings.general.max_recent_items)
            self.check_updates_check.setChecked(self.settings.general.check_updates)
            self.update_frequency_combo.setCurrentText(self.settings.general.update_frequency.title())
            self.send_analytics_check.setChecked(self.settings.general.send_analytics)
            
            # Load appearance settings
            self.theme_combo.setCurrentText(self.settings.appearance.theme.title())
            self.accent_color_combo.setCurrentText(self.settings.appearance.accent_color.title())
            self.poster_size_slider.setValue(self.settings.appearance.poster_size)
            self.grid_spacing_slider.setValue(self.settings.appearance.grid_spacing)
            self.ui_font_size_spin.setValue(self.settings.appearance.ui_font_size)
            self.show_progress_check.setChecked(self.settings.appearance.show_progress)
            self.show_ratings_check.setChecked(self.settings.appearance.show_ratings)
            self.show_thumbnails_check.setChecked(self.settings.appearance.show_episode_thumbnails)
            
            # Load library settings
            self.library_path_edit.setText(self.settings.library.library_path)
            self.additional_paths_list.clear()
            for path in self.settings.library.additional_library_paths:
                self.additional_paths_list.addItem(path)
            
            self.auto_scan_check.setChecked(self.settings.library.auto_scan)
            self.scan_interval_combo.setCurrentText(self.settings.library.scan_interval.title())
            self.deep_scan_check.setChecked(self.settings.library.deep_scan)
            self.scan_subdirs_check.setChecked(self.settings.library.scan_subdirs)
            self.min_file_size_spin.setValue(self.settings.library.min_file_size_mb)
            self.auto_fetch_covers_check.setChecked(self.settings.library.auto_fetch_covers)
            self.auto_fetch_info_check.setChecked(self.settings.library.auto_fetch_info)
            self.metadata_source_combo.setCurrentText(self.settings.library.metadata_source.title())
            self.generate_thumbnails_check.setChecked(self.settings.library.generate_thumbnails)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load settings: {e}")
            self.reject()
            return