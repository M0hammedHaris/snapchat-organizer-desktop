"""Download Tab for downloading Snapchat memories from HTML exports.

This tab provides UI for:
- Selecting HTML file and output folder
- Configuring download settings (delay, GPS, overlays, timezone, year organization)
- Real-time progress tracking with ETA
- Resume capability for interrupted downloads
- Cancel functionality
"""

from typing import Optional
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QSpinBox,
    QDoubleSpinBox,
    QCheckBox,
    QMessageBox,
)
from PySide6.QtCore import Qt, Signal, Slot

from .progress_widget import ProgressWidget
from ..utils.config import (
    DEFAULT_DOWNLOAD_DELAY,
    MIN_DOWNLOAD_DELAY,
    MAX_DOWNLOAD_DELAY,
)
from ..utils.logger import get_logger

logger = get_logger(__name__)


class DownloadTab(QWidget):
    """Download memories tab widget.
    
    Signals:
        download_started: Emitted when download starts
        download_completed: Emitted when download completes
        download_cancelled: Emitted when download is cancelled
    """
    
    download_started = Signal()
    download_completed = Signal()
    download_cancelled = Signal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize the download tab.
        
        Args:
            parent: Parent widget (optional)
        """
        super().__init__(parent)
        
        self._is_downloading = False
        
        self._setup_ui()
        logger.debug("Download tab initialized")
    
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # File selection group
        file_group = self._create_file_selection_group()
        layout.addWidget(file_group)
        
        # Configuration group
        config_group = self._create_configuration_group()
        layout.addWidget(config_group)
        
        # Action buttons
        button_layout = self._create_action_buttons()
        layout.addLayout(button_layout)
        
        # Progress widget
        self.progress_widget = ProgressWidget()
        self.progress_widget.cancel_requested.connect(self._on_cancel_requested)
        layout.addWidget(self.progress_widget)
        
        # Add stretch to push everything to top
        layout.addStretch()
    
    def _create_file_selection_group(self) -> QGroupBox:
        """Create file selection group box.
        
        Returns:
            QGroupBox with file selection controls
        """
        group = QGroupBox("📄 File Selection")
        layout = QVBoxLayout(group)
        
        # HTML file selector
        html_layout = QHBoxLayout()
        html_layout.addWidget(QLabel("HTML File:"))
        
        self.html_path_edit = QLineEdit()
        self.html_path_edit.setPlaceholderText("Select memories_history.html from your Snapchat export...")
        self.html_path_edit.setReadOnly(True)
        html_layout.addWidget(self.html_path_edit, stretch=1)
        
        self.browse_html_btn = QPushButton("Browse...")
        self.browse_html_btn.clicked.connect(self._browse_html_file)
        html_layout.addWidget(self.browse_html_btn)
        
        layout.addLayout(html_layout)
        
        # Output folder selector
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output Folder:"))
        
        self.output_path_edit = QLineEdit()
        self.output_path_edit.setPlaceholderText("Select output folder for downloaded memories...")
        self.output_path_edit.setReadOnly(True)
        output_layout.addWidget(self.output_path_edit, stretch=1)
        
        self.browse_output_btn = QPushButton("Browse...")
        self.browse_output_btn.clicked.connect(self._browse_output_folder)
        output_layout.addWidget(self.browse_output_btn)
        
        layout.addLayout(output_layout)
        
        return group
    
    def _create_configuration_group(self) -> QGroupBox:
        """Create configuration group box.
        
        Returns:
            QGroupBox with configuration controls
        """
        group = QGroupBox("⚙️ Download Settings")
        layout = QVBoxLayout(group)
        
        # Delay configuration
        delay_layout = QHBoxLayout()
        delay_layout.addWidget(QLabel("Delay between requests:"))
        
        self.delay_spinbox = QDoubleSpinBox()
        self.delay_spinbox.setMinimum(MIN_DOWNLOAD_DELAY)
        self.delay_spinbox.setMaximum(MAX_DOWNLOAD_DELAY)
        self.delay_spinbox.setValue(DEFAULT_DOWNLOAD_DELAY)
        self.delay_spinbox.setSingleStep(0.5)
        self.delay_spinbox.setSuffix(" seconds")
        self.delay_spinbox.setToolTip(
            "Time to wait between download requests to avoid rate limiting"
        )
        delay_layout.addWidget(self.delay_spinbox)
        
        delay_layout.addStretch()
        layout.addLayout(delay_layout)
        
        # Feature toggles
        self.embed_gps_checkbox = QCheckBox("Embed GPS metadata")
        self.embed_gps_checkbox.setChecked(True)
        self.embed_gps_checkbox.setToolTip(
            "Embed GPS coordinates from Snapchat data into file metadata (requires ExifTool)"
        )
        layout.addWidget(self.embed_gps_checkbox)
        
        self.apply_overlays_checkbox = QCheckBox("Apply overlays")
        self.apply_overlays_checkbox.setChecked(False)
        self.apply_overlays_checkbox.setToolTip(
            "Composite Snapchat overlays onto images and videos (requires Pillow and FFmpeg)"
        )
        layout.addWidget(self.apply_overlays_checkbox)
        
        self.convert_timezone_checkbox = QCheckBox("Convert timezone")
        self.convert_timezone_checkbox.setChecked(False)
        self.convert_timezone_checkbox.setToolTip(
            "Convert timestamps from UTC to GPS-based local timezone"
        )
        layout.addWidget(self.convert_timezone_checkbox)
        
        self.organize_by_year_checkbox = QCheckBox("Organize by year")
        self.organize_by_year_checkbox.setChecked(True)
        self.organize_by_year_checkbox.setToolTip(
            "Organize files into year-based subdirectories (e.g., 2023/, 2024/)"
        )
        layout.addWidget(self.organize_by_year_checkbox)
        
        return group
    
    def _create_action_buttons(self) -> QHBoxLayout:
        """Create action button layout.
        
        Returns:
            QHBoxLayout with action buttons
        """
        layout = QHBoxLayout()
        
        self.start_button = QPushButton("🚀 Start Download")
        self.start_button.clicked.connect(self._on_start_download)
        self.start_button.setMinimumHeight(40)
        layout.addWidget(self.start_button)
        
        layout.addStretch()
        
        self.verify_button = QPushButton("✅ Verify Downloads")
        self.verify_button.clicked.connect(self._on_verify_downloads)
        self.verify_button.setEnabled(False)
        layout.addWidget(self.verify_button)
        
        return layout
    
    @Slot()
    def _browse_html_file(self):
        """Browse for HTML file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Snapchat Memories HTML File",
            str(Path.home()),
            "HTML Files (*.html);;All Files (*.*)",
        )
        
        if file_path:
            self.html_path_edit.setText(file_path)
            logger.info(f"HTML file selected: {file_path}")
            
            # Auto-suggest output folder based on HTML location
            if not self.output_path_edit.text():
                suggested_output = Path(file_path).parent.parent / "memories"
                self.output_path_edit.setText(str(suggested_output))
    
    @Slot()
    def _browse_output_folder(self):
        """Browse for output folder."""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Select Output Folder",
            self.output_path_edit.text() or str(Path.home()),
        )
        
        if folder_path:
            self.output_path_edit.setText(folder_path)
            logger.info(f"Output folder selected: {folder_path}")
    
    @Slot()
    def _on_start_download(self):
        """Handle start download button click."""
        # Validate inputs
        html_path = self.html_path_edit.text()
        output_path = self.output_path_edit.text()
        
        if not html_path:
            QMessageBox.warning(
                self,
                "Missing HTML File",
                "Please select a Snapchat memories HTML file.",
            )
            return
        
        if not Path(html_path).exists():
            QMessageBox.warning(
                self,
                "File Not Found",
                f"The HTML file does not exist:\n{html_path}",
            )
            return
        
        if not output_path:
            QMessageBox.warning(
                self,
                "Missing Output Folder",
                "Please select an output folder.",
            )
            return
        
        # Create output directory if it doesn't exist
        try:
            Path(output_path).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error Creating Output Folder",
                f"Failed to create output folder:\n{str(e)}",
            )
            return
        
        # Start download
        logger.info("Starting download")
        logger.info(f"  HTML file: {html_path}")
        logger.info(f"  Output folder: {output_path}")
        logger.info(f"  Delay: {self.delay_spinbox.value()}s")
        logger.info(f"  GPS embedding: {self.embed_gps_checkbox.isChecked()}")
        logger.info(f"  Apply overlays: {self.apply_overlays_checkbox.isChecked()}")
        logger.info(f"  Convert timezone: {self.convert_timezone_checkbox.isChecked()}")
        logger.info(f"  Organize by year: {self.organize_by_year_checkbox.isChecked()}")
        
        self._is_downloading = True
        self._set_ui_enabled(False)
        
        # TODO: Start actual download process in background thread
        # For now, show a placeholder message
        self.progress_widget.start(100, "Preparing to download...")
        QMessageBox.information(
            self,
            "Download Started",
            "Download functionality will be implemented in the next phase.\n\n"
            "The downloader will parse the HTML file and download all memories "
            "with the configured settings.",
        )
        
        self._is_downloading = False
        self._set_ui_enabled(True)
        self.progress_widget.reset()
        
        self.download_started.emit()
    
    @Slot()
    def _on_cancel_requested(self):
        """Handle cancel request from progress widget."""
        logger.info("Download cancellation requested")
        
        if not self._is_downloading:
            return
        
        # TODO: Actually cancel the download
        self._is_downloading = False
        self._set_ui_enabled(True)
        self.progress_widget.set_status("Download cancelled by user")
        
        self.download_cancelled.emit()
    
    @Slot()
    def _on_verify_downloads(self):
        """Handle verify downloads button click."""
        logger.info("Verify downloads requested")
        QMessageBox.information(
            self,
            "Verify Downloads",
            "Verification functionality will be implemented in the next phase.\n\n"
            "This will check all downloaded files for completeness and corruption.",
        )
    
    def _set_ui_enabled(self, enabled: bool):
        """Enable or disable UI controls.
        
        Args:
            enabled: True to enable, False to disable
        """
        self.browse_html_btn.setEnabled(enabled)
        self.browse_output_btn.setEnabled(enabled)
        self.delay_spinbox.setEnabled(enabled)
        self.embed_gps_checkbox.setEnabled(enabled)
        self.apply_overlays_checkbox.setEnabled(enabled)
        self.convert_timezone_checkbox.setEnabled(enabled)
        self.organize_by_year_checkbox.setEnabled(enabled)
        self.start_button.setEnabled(enabled)
        self.verify_button.setEnabled(enabled)
    
    def get_configuration(self) -> dict:
        """Get current download configuration.
        
        Returns:
            Dictionary with download configuration
        """
        return {
            'html_path': self.html_path_edit.text(),
            'output_path': self.output_path_edit.text(),
            'delay': self.delay_spinbox.value(),
            'embed_gps': self.embed_gps_checkbox.isChecked(),
            'apply_overlays': self.apply_overlays_checkbox.isChecked(),
            'convert_timezone': self.convert_timezone_checkbox.isChecked(),
            'organize_by_year': self.organize_by_year_checkbox.isChecked(),
        }
