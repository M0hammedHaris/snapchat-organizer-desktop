"""Settings dialog for application configuration.

This module provides a settings dialog where users can configure application
preferences, default paths, behavior options, and view application information.
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QSpinBox,
    QDoubleSpinBox,
    QFileDialog,
    QWidget,
    QFormLayout,
    QMessageBox,
)

from src.utils.config import (
    APP_NAME,
    APP_VERSION,
    APP_AUTHOR,
    APP_ORG,
    DEFAULT_DOWNLOAD_DELAY,
    MIN_DOWNLOAD_DELAY,
    MAX_DOWNLOAD_DELAY,
    DEFAULT_TIMESTAMP_THRESHOLD,
    MIN_TIMESTAMP_THRESHOLD,
    MAX_TIMESTAMP_THRESHOLD,
)

logger = logging.getLogger(__name__)


class SettingsDialog(QDialog):
    """Dialog for application settings and preferences.
    
    Provides tabs for:
    - General settings (default paths, behavior)
    - Download settings (delay, retries, timeout)
    - Organize settings (matching thresholds, time windows)
    - About information (version, license, author)
    
    Signals:
        settings_changed: Emitted when settings are saved with updated values
    """

    settings_changed = Signal(dict)  # Emits dictionary of changed settings

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize the settings dialog.
        
        Args:
            parent: Optional parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumSize(600, 500)
        
        # Store original settings to detect changes
        self._original_settings: Dict[str, Any] = {}
        self._current_settings: Dict[str, Any] = {}
        
        self._setup_ui()
        self._load_settings()
        logger.info("Settings dialog initialized")

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        # Create tab widget
        tab_widget = QTabWidget()
        tab_widget.addTab(self._create_general_tab(), "General")
        tab_widget.addTab(self._create_download_tab(), "Download")
        tab_widget.addTab(self._create_organize_tab(), "Organize")
        tab_widget.addTab(self._create_about_tab(), "About")

        layout.addWidget(tab_widget)

        # Button layout
        button_layout = QHBoxLayout()
        
        # Restore defaults button
        restore_btn = QPushButton("Restore Defaults")
        restore_btn.clicked.connect(self._restore_defaults)
        button_layout.addWidget(restore_btn)
        
        button_layout.addStretch()
        
        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        # Save button
        save_btn = QPushButton("Save")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self._save_settings)
        button_layout.addWidget(save_btn)

        layout.addLayout(button_layout)

    def _create_general_tab(self) -> QWidget:
        """Create the general settings tab.
        
        Returns:
            Widget containing general settings
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Default Paths Group
        paths_group = QGroupBox("Default Paths")
        paths_layout = QFormLayout(paths_group)

        # Default download directory
        self.default_download_edit = QLineEdit()
        download_browse = QPushButton("Browse...")
        download_browse.clicked.connect(
            lambda: self._browse_directory(self.default_download_edit)
        )
        download_layout = QHBoxLayout()
        download_layout.addWidget(self.default_download_edit)
        download_layout.addWidget(download_browse)
        paths_layout.addRow("Default Download Folder:", download_layout)

        # Default export directory
        self.default_export_edit = QLineEdit()
        export_browse = QPushButton("Browse...")
        export_browse.clicked.connect(
            lambda: self._browse_directory(self.default_export_edit)
        )
        export_layout = QHBoxLayout()
        export_layout.addWidget(self.default_export_edit)
        export_layout.addWidget(export_browse)
        paths_layout.addRow("Default Export Folder:", export_layout)

        layout.addWidget(paths_group)

        # Behavior Group
        behavior_group = QGroupBox("Behavior")
        behavior_layout = QVBoxLayout(behavior_group)

        self.remember_last_paths_check = QCheckBox("Remember last used paths")
        self.remember_last_paths_check.setChecked(True)
        behavior_layout.addWidget(self.remember_last_paths_check)

        self.auto_open_output_check = QCheckBox("Automatically open output folder when complete")
        self.auto_open_output_check.setChecked(False)
        behavior_layout.addWidget(self.auto_open_output_check)

        self.confirm_operations_check = QCheckBox("Confirm before destructive operations")
        self.confirm_operations_check.setChecked(True)
        behavior_layout.addWidget(self.confirm_operations_check)

        layout.addWidget(behavior_group)

        layout.addStretch()
        return widget

    def _create_download_tab(self) -> QWidget:
        """Create the download settings tab.
        
        Returns:
            Widget containing download settings
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Download Settings Group
        download_group = QGroupBox("Download Settings")
        download_layout = QFormLayout(download_group)

        # Download delay
        self.download_delay_spin = QDoubleSpinBox()
        self.download_delay_spin.setRange(MIN_DOWNLOAD_DELAY, MAX_DOWNLOAD_DELAY)
        self.download_delay_spin.setSingleStep(0.5)
        self.download_delay_spin.setSuffix(" seconds")
        self.download_delay_spin.setValue(DEFAULT_DOWNLOAD_DELAY)
        download_layout.addRow("Download Delay:", self.download_delay_spin)

        # Max retries
        self.max_retries_spin = QSpinBox()
        self.max_retries_spin.setRange(0, 10)
        self.max_retries_spin.setValue(3)
        download_layout.addRow("Max Retries:", self.max_retries_spin)

        # Timeout
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(10, 300)
        self.timeout_spin.setSuffix(" seconds")
        self.timeout_spin.setValue(30)
        download_layout.addRow("Request Timeout:", self.timeout_spin)

        layout.addWidget(download_group)

        # Default Options Group
        options_group = QGroupBox("Default Download Options")
        options_layout = QVBoxLayout(options_group)

        self.default_gps_check = QCheckBox("Apply GPS metadata by default")
        self.default_gps_check.setChecked(True)
        options_layout.addWidget(self.default_gps_check)

        self.default_overlay_check = QCheckBox("Apply overlays by default")
        self.default_overlay_check.setChecked(True)
        options_layout.addWidget(self.default_overlay_check)

        self.default_timezone_check = QCheckBox("Convert timezone by default")
        self.default_timezone_check.setChecked(True)
        options_layout.addWidget(self.default_timezone_check)

        layout.addWidget(options_group)

        layout.addStretch()
        return widget

    def _create_organize_tab(self) -> QWidget:
        """Create the organize settings tab.
        
        Returns:
            Widget containing organize settings
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Matching Settings Group
        matching_group = QGroupBox("Matching Settings")
        matching_layout = QFormLayout(matching_group)

        # Time window
        self.time_window_spin = QSpinBox()
        self.time_window_spin.setRange(60, 86400)  # 1 minute to 24 hours
        self.time_window_spin.setSuffix(" seconds")
        self.time_window_spin.setValue(7200)  # 2 hours default
        matching_layout.addRow("Time Window:", self.time_window_spin)
        
        time_help = QLabel("Maximum time difference for timestamp matching (default: 2 hours)")
        time_help.setWordWrap(True)
        time_help.setStyleSheet("color: #666; font-size: 11px;")
        matching_layout.addRow("", time_help)

        # Minimum score
        self.min_score_spin = QSpinBox()
        self.min_score_spin.setRange(0, 100)
        self.min_score_spin.setSuffix("%")
        self.min_score_spin.setValue(45)
        matching_layout.addRow("Minimum Match Score:", self.min_score_spin)
        
        score_help = QLabel("Minimum confidence score for matching (default: 45%)")
        score_help.setWordWrap(True)
        score_help.setStyleSheet("color: #666; font-size: 11px;")
        matching_layout.addRow("", score_help)

        layout.addWidget(matching_group)

        # Organization Options Group
        org_options_group = QGroupBox("Organization Options")
        org_options_layout = QVBoxLayout(org_options_group)

        self.copy_files_check = QCheckBox("Copy files instead of moving")
        self.copy_files_check.setChecked(False)
        org_options_layout.addWidget(self.copy_files_check)

        self.preserve_structure_check = QCheckBox("Preserve original folder structure")
        self.preserve_structure_check.setChecked(False)
        org_options_layout.addWidget(self.preserve_structure_check)

        self.create_report_check = QCheckBox("Generate matching report after organization")
        self.create_report_check.setChecked(True)
        org_options_layout.addWidget(self.create_report_check)

        layout.addWidget(org_options_group)

        layout.addStretch()
        return widget

    def _create_about_tab(self) -> QWidget:
        """Create the about information tab.
        
        Returns:
            Widget containing about information
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # App icon/logo placeholder
        title = QLabel(f"<h1>{APP_NAME}</h1>")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Version
        version = QLabel(f"Version {APP_VERSION}")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version.setStyleSheet("color: #666; font-size: 14px;")
        layout.addWidget(version)

        layout.addSpacing(20)

        # Description
        description = QLabel(
            "Professional desktop application for downloading and organizing "
            "Snapchat memories locally with overlay compositing, GPS metadata "
            "preservation, and timezone conversion."
        )
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(description)

        layout.addSpacing(20)

        # Info group
        info_group = QGroupBox("Information")
        info_layout = QFormLayout(info_group)
        info_layout.addRow("Author:", QLabel(APP_AUTHOR))
        info_layout.addRow("Organization:", QLabel(APP_ORG))
        info_layout.addRow("License:", QLabel("Proprietary - All Rights Reserved"))
        info_layout.addRow("Python:", QLabel("3.11+"))
        info_layout.addRow("Framework:", QLabel("PySide6 (Qt for Python)"))
        layout.addWidget(info_group)

        # Copyright
        copyright_label = QLabel(f"© 2026 {APP_AUTHOR}. All Rights Reserved.")
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        copyright_label.setStyleSheet("color: #999; font-size: 11px; margin-top: 20px;")
        layout.addWidget(copyright_label)

        layout.addStretch()
        return widget

    def _browse_directory(self, line_edit: QLineEdit):
        """Browse for a directory and update line edit.
        
        Args:
            line_edit: Line edit to update with selected path
        """
        current_path = line_edit.text() or str(Path.home())
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Directory",
            current_path,
            QFileDialog.Option.ShowDirsOnly
        )
        
        if directory:
            line_edit.setText(directory)
            logger.debug(f"Directory selected: {directory}")

    def _load_settings(self):
        """Load current settings from configuration."""
        # TODO: Load from actual config file when implemented
        # For now, use defaults
        self._original_settings = {
            'default_download_dir': str(Path.home() / "Downloads"),
            'default_export_dir': str(Path.home() / "Downloads"),
            'remember_last_paths': True,
            'auto_open_output': False,
            'confirm_operations': True,
            'download_delay': DEFAULT_DOWNLOAD_DELAY,
            'max_retries': 3,
            'timeout': 30,
            'default_gps': True,
            'default_overlay': True,
            'default_timezone': True,
            'time_window': 7200,
            'min_score': 45,
            'copy_files': False,
            'preserve_structure': False,
            'create_report': True,
        }
        
        # Apply to UI
        self.default_download_edit.setText(self._original_settings['default_download_dir'])
        self.default_export_edit.setText(self._original_settings['default_export_dir'])
        self.remember_last_paths_check.setChecked(self._original_settings['remember_last_paths'])
        self.auto_open_output_check.setChecked(self._original_settings['auto_open_output'])
        self.confirm_operations_check.setChecked(self._original_settings['confirm_operations'])
        self.download_delay_spin.setValue(self._original_settings['download_delay'])
        self.max_retries_spin.setValue(self._original_settings['max_retries'])
        self.timeout_spin.setValue(self._original_settings['timeout'])
        self.default_gps_check.setChecked(self._original_settings['default_gps'])
        self.default_overlay_check.setChecked(self._original_settings['default_overlay'])
        self.default_timezone_check.setChecked(self._original_settings['default_timezone'])
        self.time_window_spin.setValue(self._original_settings['time_window'])
        self.min_score_spin.setValue(self._original_settings['min_score'])
        self.copy_files_check.setChecked(self._original_settings['copy_files'])
        self.preserve_structure_check.setChecked(self._original_settings['preserve_structure'])
        self.create_report_check.setChecked(self._original_settings['create_report'])
        
        logger.info("Settings loaded")

    def _save_settings(self):
        """Save current settings and emit changes."""
        self._current_settings = {
            'default_download_dir': self.default_download_edit.text(),
            'default_export_dir': self.default_export_edit.text(),
            'remember_last_paths': self.remember_last_paths_check.isChecked(),
            'auto_open_output': self.auto_open_output_check.isChecked(),
            'confirm_operations': self.confirm_operations_check.isChecked(),
            'download_delay': self.download_delay_spin.value(),
            'max_retries': self.max_retries_spin.value(),
            'timeout': self.timeout_spin.value(),
            'default_gps': self.default_gps_check.isChecked(),
            'default_overlay': self.default_overlay_check.isChecked(),
            'default_timezone': self.default_timezone_check.isChecked(),
            'time_window': self.time_window_spin.value(),
            'min_score': self.min_score_spin.value(),
            'copy_files': self.copy_files_check.isChecked(),
            'preserve_structure': self.preserve_structure_check.isChecked(),
            'create_report': self.create_report_check.isChecked(),
        }
        
        # TODO: Save to actual config file
        logger.info("Settings saved")
        
        # Emit changed settings
        self.settings_changed.emit(self._current_settings)
        
        # Show confirmation
        QMessageBox.information(
            self,
            "Settings Saved",
            "Your settings have been saved successfully."
        )
        
        self.accept()

    def _restore_defaults(self):
        """Restore all settings to default values."""
        reply = QMessageBox.question(
            self,
            "Restore Defaults",
            "Are you sure you want to restore all settings to their default values?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Reset to defaults
            self.default_download_edit.setText(str(Path.home() / "Downloads"))
            self.default_export_edit.setText(str(Path.home() / "Downloads"))
            self.remember_last_paths_check.setChecked(True)
            self.auto_open_output_check.setChecked(False)
            self.confirm_operations_check.setChecked(True)
            self.download_delay_spin.setValue(DEFAULT_DOWNLOAD_DELAY)
            self.max_retries_spin.setValue(3)
            self.timeout_spin.setValue(30)
            self.default_gps_check.setChecked(True)
            self.default_overlay_check.setChecked(True)
            self.default_timezone_check.setChecked(True)
            self.time_window_spin.setValue(7200)
            self.min_score_spin.setValue(45)
            self.copy_files_check.setChecked(False)
            self.preserve_structure_check.setChecked(False)
            self.create_report_check.setChecked(True)
            
            logger.info("Settings restored to defaults")
            
            QMessageBox.information(
                self,
                "Defaults Restored",
                "All settings have been restored to their default values.\n\n"
                "Click 'Save' to apply these changes."
            )

    def get_settings(self) -> Dict[str, Any]:
        """Get current settings as dictionary.
        
        Returns:
            Dictionary of current settings
        """
        return self._current_settings if self._current_settings else self._original_settings
