"""Organize Tab for organizing Snapchat chat media by contact.

This tab provides UI for:
- Selecting Snapchat export folder and output folder
- Configuring 3-tier matching strategy (Media ID, Single Contact, Timestamp)
- Real-time progress tracking with matching statistics
- Resume capability for interrupted organization
- Detailed matching report generation
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
    QCheckBox,
    QMessageBox,
    QTextEdit,
)
from PySide6.QtCore import Signal, Slot

from .progress_widget import ProgressWidget
from ..core.organize_worker import OrganizeWorker
from ..utils.logger import get_logger

logger = get_logger(__name__)


class OrganizeTab(QWidget):
    """Organize chat media tab widget.
    
    Signals:
        organize_started: Emitted when organization starts
        organize_completed: Emitted when organization completes
        organize_cancelled: Emitted when organization is cancelled
    """
    
    organize_started = Signal()
    organize_completed = Signal()
    organize_cancelled = Signal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize the organize tab.
        
        Args:
            parent: Parent widget (optional)
        """
        super().__init__(parent)
        
        self._is_organizing = False
        self._organize_worker = None
        
        self._setup_ui()
        logger.debug("Organize tab initialized")
    
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Instructions header
        instructions = self._create_instructions_widget()
        layout.addWidget(instructions)
        
        # Folder selection group
        folder_group = self._create_folder_selection_group()
        layout.addWidget(folder_group)
        
        # Matching configuration group
        config_group = self._create_configuration_group()
        layout.addWidget(config_group)
        
        # Action buttons
        button_layout = self._create_action_buttons()
        layout.addLayout(button_layout)
        
        # Progress widget
        self.progress_widget = ProgressWidget()
        self.progress_widget.cancel_requested.connect(self._on_cancel_requested)
        layout.addWidget(self.progress_widget)
        
        # Matching statistics display
        stats_group = self._create_statistics_group()
        layout.addWidget(stats_group)
        
        # Add stretch to push everything to top
        layout.addStretch()
    
    def _create_instructions_widget(self) -> QGroupBox:
        """Create instructions widget with folder requirements.
        
        Returns:
            QGroupBox with instructions
        """
        group = QGroupBox("ℹ️ Quick Start Guide")
        group.setStyleSheet(
            "QGroupBox { "
            "font-weight: bold; "
            "padding-top: 10px; "
            "background-color: #e8f4f8; "
            "border-radius: 6px; "
            "}"
        )
        layout = QVBoxLayout(group)
        layout.setSpacing(8)
        
        instructions_text = QLabel(
            "<b>Required Folder Structure:</b><br>"
            "Your Snapchat export folder must contain:<br>"
            "  • <b>chat_history/json/chat_history.json</b> - Contact message data<br>"
            "  • <b>chat_media/</b> or <b>chat_media_1/</b>, <b>chat_media_2/</b>, etc. - Media files<br><br>"
            "<b>What this does:</b> Organizes media files into folders by contact name using intelligent matching."
        )
        instructions_text.setWordWrap(True)
        instructions_text.setStyleSheet(
            "font-size: 11px; "
            "color: #2c3e50; "
            "padding: 8px; "
            "background-color: white; "
            "border-radius: 4px; "
            "font-weight: normal;"
        )
        layout.addWidget(instructions_text)
        
        return group
    
    def _create_folder_selection_group(self) -> QGroupBox:
        """Create folder selection group box.
        
        Returns:
            QGroupBox with folder selection controls
        """
        group = QGroupBox("📂 Folder Selection")
        group.setStyleSheet("QGroupBox { font-weight: bold; padding-top: 10px; }")
        layout = QVBoxLayout(group)
        layout.setSpacing(10)
        
        # Export folder selector
        export_layout = QHBoxLayout()
        export_layout.addWidget(QLabel("Snapchat Export:"))
        
        self.export_path_edit = QLineEdit()
        self.export_path_edit.setPlaceholderText("Select folder containing chat_media folders and chat_history.json...")
        self.export_path_edit.setReadOnly(True)
        export_layout.addWidget(self.export_path_edit, stretch=1)
        
        self.browse_export_btn = QPushButton("Browse...")
        self.browse_export_btn.clicked.connect(self._browse_export_folder)
        export_layout.addWidget(self.browse_export_btn)
        
        layout.addLayout(export_layout)
        
        # Output folder selector
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output Folder:"))
        
        self.output_path_edit = QLineEdit()
        self.output_path_edit.setPlaceholderText("Select output folder for organized media...")
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
        group = QGroupBox("⚙️ Matching Settings")
        group.setStyleSheet("QGroupBox { font-weight: bold; padding-top: 10px; }")
        layout = QVBoxLayout(group)
        layout.setSpacing(10)
        
        # Matching strategy info
        info_label = QLabel(
            "3-Tier Matching Strategy:\n"
            "  • Tier 1: Media ID matching (most accurate)\n"
            "  • Tier 2: Single contact on date\n"
            "  • Tier 3: Timestamp proximity matching"
        )
        info_label.setStyleSheet(
            "color: #555; "
            "font-size: 11px; "
            "padding: 8px; "
            "background-color: #f5f5f5; "
            "border-radius: 4px; "
            "border: 1px solid #ddd;"
        )
        layout.addWidget(info_label)
        
        # Timestamp threshold
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel("Timestamp threshold:"))
        
        self.threshold_spinbox = QSpinBox()
        self.threshold_spinbox.setMinimum(30)
        self.threshold_spinbox.setMaximum(3600)
        self.threshold_spinbox.setValue(300)
        self.threshold_spinbox.setSingleStep(30)
        self.threshold_spinbox.setSuffix(" seconds")
        self.threshold_spinbox.setToolTip(
            "Maximum time difference for Tier 3 timestamp matching (default: 5 minutes)"
        )
        threshold_layout.addWidget(self.threshold_spinbox)
        
        threshold_layout.addStretch()
        layout.addLayout(threshold_layout)
        
        # Feature toggles
        self.enable_tier1_checkbox = QCheckBox("Enable Tier 1 (Media ID matching)")
        self.enable_tier1_checkbox.setChecked(True)
        self.enable_tier1_checkbox.setToolTip("Match files by Media ID - most accurate")
        layout.addWidget(self.enable_tier1_checkbox)
        
        self.enable_tier2_checkbox = QCheckBox("Enable Tier 2 (Single contact matching)")
        self.enable_tier2_checkbox.setChecked(True)
        self.enable_tier2_checkbox.setToolTip("Match files when only one contact sent media that day")
        layout.addWidget(self.enable_tier2_checkbox)
        
        self.enable_tier3_checkbox = QCheckBox("Enable Tier 3 (Timestamp proximity)")
        self.enable_tier3_checkbox.setChecked(True)
        self.enable_tier3_checkbox.setToolTip("Match files by timestamp proximity - use with caution")
        layout.addWidget(self.enable_tier3_checkbox)
        
        self.organize_by_year_checkbox = QCheckBox("Organize by year")
        self.organize_by_year_checkbox.setChecked(True)
        self.organize_by_year_checkbox.setToolTip("Create year subdirectories (e.g., ContactName/2023/)")
        layout.addWidget(self.organize_by_year_checkbox)
        
        self.create_debug_report_checkbox = QCheckBox("Create detailed matching report")
        self.create_debug_report_checkbox.setChecked(True)
        self.create_debug_report_checkbox.setToolTip("Generate a detailed log of matching decisions")
        layout.addWidget(self.create_debug_report_checkbox)
        
        return group
    
    def _create_statistics_group(self) -> QGroupBox:
        """Create statistics display group box.
        
        Returns:
            QGroupBox with statistics display
        """
        group = QGroupBox("📊 Matching Statistics")
        group.setStyleSheet("QGroupBox { font-weight: bold; padding-top: 10px; }")
        layout = QVBoxLayout(group)
        layout.setSpacing(10)
        
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setMaximumHeight(150)
        self.stats_text.setPlaceholderText("Statistics will appear here after organization completes...")
        layout.addWidget(self.stats_text)
        
        return group
    
    def _create_action_buttons(self) -> QHBoxLayout:
        """Create action button layout.
        
        Returns:
            QHBoxLayout with action buttons
        """
        layout = QHBoxLayout()
        
        self.start_btn = QPushButton("🚀 Start Organization")
        self.start_btn.clicked.connect(self._on_start_clicked)
        self.start_btn.setMinimumHeight(40)
        layout.addWidget(self.start_btn)
        
        self.open_output_btn = QPushButton("📁 Open Output Folder")
        self.open_output_btn.clicked.connect(self._on_open_output_clicked)
        self.open_output_btn.setEnabled(False)
        layout.addWidget(self.open_output_btn)
        
        return layout
    
    @Slot()
    def _browse_export_folder(self):
        """Browse for Snapchat export folder."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Snapchat Export Folder",
            str(Path.home()),
            QFileDialog.ShowDirsOnly
        )
        
        if folder:
            # Validate folder contains required files
            export_path = Path(folder)
            chat_json = export_path / "chat_history" / "json" / "chat_history.json"
            
            if not chat_json.exists():
                QMessageBox.warning(
                    self,
                    "Invalid Export Folder",
                    f"Selected folder doesn't contain chat_history/json/chat_history.json\n\n"
                    f"Please select the root folder of your Snapchat export."
                )
                return
            
            # Check for chat_media folders
            media_dirs = list(export_path.glob("chat_media*"))
            if not media_dirs:
                QMessageBox.warning(
                    self,
                    "No Media Folders Found",
                    f"Selected folder doesn't contain any chat_media folders.\n\n"
                    f"Make sure you're selecting the correct Snapchat export folder."
                )
                return
            
            self.export_path_edit.setText(folder)
            logger.info(f"Export folder selected: {folder} ({len(media_dirs)} media folders found)")
    
    @Slot()
    def _browse_output_folder(self):
        """Browse for output folder."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Output Folder",
            str(Path.home()),
            QFileDialog.ShowDirsOnly
        )
        
        if folder:
            self.output_path_edit.setText(folder)
            logger.info(f"Output folder selected: {folder}")
    
    @Slot()
    def _on_start_clicked(self):
        """Handle start button click."""
        # Validate inputs
        if not self.export_path_edit.text():
            QMessageBox.warning(
                self,
                "Missing Export Folder",
                "Please select a Snapchat export folder."
            )
            return
        
        if not self.output_path_edit.text():
            QMessageBox.warning(
                self,
                "Missing Output Folder",
                "Please select an output folder."
            )
            return
        
        # Confirm start
        export_path = Path(self.export_path_edit.text())
        output_path = Path(self.output_path_edit.text())
        media_dirs = list(export_path.glob("chat_media*"))
        
        reply = QMessageBox.question(
            self,
            "Start Organization",
            f"Ready to organize media from:\n\n"
            f"Export: {export_path.name}\n"
            f"Media folders: {len(media_dirs)}\n"
            f"Output: {output_path}\n\n"
            f"Continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply == QMessageBox.No:
            return
        
        self._start_organization()
    
    def _start_organization(self):
        """Start the organization process."""
        logger.info("Starting organization process...")
        
        # Get settings
        export_path = Path(self.export_path_edit.text())
        output_path = Path(self.output_path_edit.text())
        threshold = self.threshold_spinbox.value()
        enable_tier1 = self.enable_tier1_checkbox.isChecked()
        enable_tier2 = self.enable_tier2_checkbox.isChecked()
        enable_tier3 = self.enable_tier3_checkbox.isChecked()
        organize_by_year = self.organize_by_year_checkbox.isChecked()
        create_report = self.create_debug_report_checkbox.isChecked()
        
        # Create and configure worker
        self._organize_worker = OrganizeWorker(
            export_path=export_path,
            output_path=output_path,
            timestamp_threshold=threshold,
            enable_tier1=enable_tier1,
            enable_tier2=enable_tier2,
            enable_tier3=enable_tier3,
            organize_by_year=organize_by_year,
            create_debug_report=create_report,
        )
        
        # Connect signals
        self._organize_worker.progress_updated.connect(self._on_progress_updated)
        self._organize_worker.stats_updated.connect(self._on_stats_updated)
        self._organize_worker.finished.connect(self._on_organization_finished)
        self._organize_worker.error.connect(self._on_organization_error)
        
        # Update UI state
        self._is_organizing = True
        self._update_ui_state()
        
        # Clear previous stats
        self.stats_text.clear()
        self.progress_widget.reset()
        self.progress_widget.set_status("Starting organization...")
        
        # Start worker
        self._organize_worker.start()
        
        logger.info("Organization worker started")
        self.organize_started.emit()
    
    @Slot()
    def _on_cancel_requested(self):
        """Handle cancel request from progress widget."""
        if not self._is_organizing:
            return
        
        reply = QMessageBox.question(
            self,
            "Cancel Organization",
            "Are you sure you want to cancel the organization?\n\n"
            "Progress will be saved and you can resume later.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            logger.info("User requested cancel")
            if self._organize_worker:
                self._organize_worker.cancel()
    
    @Slot(int, int, str)
    def _on_progress_updated(self, current: int, total: int, status: str):
        """Handle progress updates from worker.
        
        Args:
            current: Current progress value
            total: Total progress value
            status: Status message
        """
        self.progress_widget.set_progress(current, total)
        self.progress_widget.set_status(status)
    
    @Slot(dict)
    def _on_stats_updated(self, stats: dict):
        """Handle statistics updates from worker.
        
        Args:
            stats: Statistics dictionary
        """
        total = stats.get("total", 0)
        organized = stats.get("organized", 0)
        unmatched = stats.get("unmatched", 0)
        tier1 = stats.get("tier1", 0)
        tier2 = stats.get("tier2", 0)
        tier3 = stats.get("tier3", 0)
        
        stats_text = (
            f"Total files: {total}\\n"
            f"Organized: {organized}\\n"
            f"Unmatched: {unmatched}\\n\\n"
            f"Matching breakdown:\\n"
            f"  • Tier 1 (Media ID): {tier1}\\n"
            f"  • Tier 2 (Single Contact): {tier2}\\n"
            f"  • Tier 3 (Timestamp): {tier3}"
        )
        
        self.stats_text.setPlainText(stats_text)
    
    @Slot(bool, str)
    def _on_organization_finished(self, success: bool, message: str):
        """Handle organization completion.
        
        Args:
            success: Whether organization succeeded
            message: Completion message
        """
        self._is_organizing = False
        self._update_ui_state()
        
        if success:
            QMessageBox.information(
                self,
                "Organization Complete",
                message
            )
            logger.info("Organization completed successfully")
            self.organize_completed.emit()
        else:
            QMessageBox.warning(
                self,
                "Organization Cancelled",
                message
            )
            logger.warning(f"Organization cancelled: {message}")
            self.organize_cancelled.emit()
        
        # Clean up worker
        if self._organize_worker:
            self._organize_worker.deleteLater()
            self._organize_worker = None
    
    @Slot(str)
    def _on_organization_error(self, error_message: str):
        """Handle organization error.
        
        Args:
            error_message: Error message
        """
        self._is_organizing = False
        self._update_ui_state()
        
        QMessageBox.critical(
            self,
            "Organization Error",
            f"An error occurred during organization:\\n\\n{error_message}"
        )
        
        logger.error(f"Organization error: {error_message}")
        
        # Clean up worker
        if self._organize_worker:
            self._organize_worker.deleteLater()
            self._organize_worker = None
    
    @Slot()
    def _on_open_output_clicked(self):
        """Open the output folder in file explorer."""
        output_path = self.output_path_edit.text()
        if output_path and Path(output_path).exists():
            import subprocess
            import platform
            
            system = platform.system()
            if system == "Darwin":  # macOS
                subprocess.run(["open", output_path])
            elif system == "Windows":
                subprocess.run(["explorer", output_path])
            else:  # Linux
                subprocess.run(["xdg-open", output_path])
            
            logger.info(f"Opened output folder: {output_path}")
    
    def _update_ui_state(self):
        """Update UI elements based on current state."""
        is_idle = not self._is_organizing
        
        self.browse_export_btn.setEnabled(is_idle)
        self.browse_output_btn.setEnabled(is_idle)
        self.start_btn.setEnabled(is_idle)
        self.enable_tier1_checkbox.setEnabled(is_idle)
        self.enable_tier2_checkbox.setEnabled(is_idle)
        self.enable_tier3_checkbox.setEnabled(is_idle)
        self.threshold_spinbox.setEnabled(is_idle)
        self.organize_by_year_checkbox.setEnabled(is_idle)
        self.create_debug_report_checkbox.setEnabled(is_idle)
        
        # Update button text
        if self._is_organizing:
            self.start_btn.setText("⏳ Organizing...")
        else:
            self.start_btn.setText("🚀 Start Organization")
        
        # Enable open output button if output folder exists
        output_path = self.output_path_edit.text()
        self.open_output_btn.setEnabled(
            bool(output_path) and Path(output_path).exists()
        )
