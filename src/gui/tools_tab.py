"""Tools Tab for various utility operations on media files.

This tab provides UI for:
- File verification (check integrity)
- Remove duplicates (hash-based deduplication)
- Apply overlays (composite Snapchat overlays)
- Convert timezone (GPS-based timezone conversion)
- Organize by year (reorganize files by year)
- Fix timestamps (correct file timestamps)
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
    QMessageBox,
    QGridLayout,
    QTextEdit,
    QScrollArea,
    QFrame,
)
from PySide6.QtCore import Signal, Slot, Qt
from PySide6.QtGui import QFont

from .progress_widget import ProgressWidget
from ..core.tools_worker import ToolsWorker
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ToolButton(QPushButton):
    """Custom styled tool button with icon and description."""
    
    def __init__(
        self,
        icon: str,
        title: str,
        description: str,
        parent: Optional[QWidget] = None
    ):
        """Initialize the tool button.
        
        Args:
            icon: Emoji icon for the tool
            title: Tool name
            description: Brief description of what the tool does
            parent: Parent widget (optional)
        """
        super().__init__(parent)
        
        self.setMinimumHeight(100)
        self.setMinimumHeight(100)
        
        # Use QSS class for styling
        self.setProperty("class", "ToolButton")
        
        # Create button text with icon, title, and description with better spacing
        button_text = f"{icon}  {title}\n\n{description}"
        self.setText(button_text)


class ToolsTab(QWidget):
    """Tools tab widget for utility operations.
    
    Signals:
        tool_started: Emitted when a tool operation starts
        tool_completed: Emitted when a tool operation completes
        tool_cancelled: Emitted when a tool operation is cancelled
    """
    
    tool_started = Signal(str)  # tool name
    tool_completed = Signal(str)  # tool name
    tool_cancelled = Signal(str)  # tool name
    
    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize the tools tab.
        
        Args:
            parent: Parent widget (optional)
        """
        super().__init__(parent)
        
        self._is_running = False
        self._current_tool = None
        self._selected_folder = None
        self._worker: Optional[ToolsWorker] = None
        
        self._setup_ui()
        logger.debug("Tools tab initialized")
    
    def _setup_ui(self):
        """Set up the user interface."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Scroll area setup
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Container widget for scroll area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(30, 25, 30, 25)
        
        # Instructions header
        instructions = self._create_instructions_widget()
        content_layout.addWidget(instructions)
        
        # Folder selection
        folder_group = self._create_folder_selection_group()
        content_layout.addWidget(folder_group)
        
        # Tools grid
        tools_group = self._create_tools_grid()
        content_layout.addWidget(tools_group)
        
        # Progress widget
        self.progress_widget = ProgressWidget()
        self.progress_widget.cancel_requested.connect(self._on_cancel_requested)
        content_layout.addWidget(self.progress_widget)
        
        # Statistics display
        self.stats_display = self._create_statistics_display()
        content_layout.addWidget(self.stats_display)
        
        # Add stretch to push everything to top
        content_layout.addStretch()
        
        # Set scroll area widget
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
    
    def _create_instructions_widget(self) -> QWidget:
        """Create instructions header widget.
        
        Returns:
            QWidget with instructions
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Title
        title = QLabel("🔧 Utility Tools")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Description
        desc = QLabel(
            "Select a folder and choose a tool to perform various operations "
            "on your media files. Each tool provides specific functionality "
            "for managing and optimizing your Snapchat media collection."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #666;")
        layout.addWidget(desc)
        
        return widget
    
    def _create_folder_selection_group(self) -> QGroupBox:
        """Create folder selection group box.
        
        Returns:
            QGroupBox with folder selection controls
        """
        group = QGroupBox("📁 Folder Selection")
        layout = QVBoxLayout(group)
        
        # Folder input row
        folder_layout = QHBoxLayout()
        
        folder_label = QLabel("Target Folder:")
        folder_label.setFixedWidth(100)
        folder_layout.addWidget(folder_label)
        
        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText("Select folder containing media files...")
        self.folder_input.setReadOnly(True)
        folder_layout.addWidget(self.folder_input)
        
        self.folder_button = QPushButton("Browse...")
        self.folder_button.setFixedWidth(100)
        self.folder_button.clicked.connect(self._on_browse_folder)
        folder_layout.addWidget(self.folder_button)
        
        layout.addLayout(folder_layout)
        
        return group
    
    def _create_tools_grid(self) -> QGroupBox:
        """Create tools grid with all available tools.
        
        Returns:
            QGroupBox containing tool buttons
        """
        group = QGroupBox("🛠️ Available Tools")
        layout = QGridLayout(group)
        layout.setSpacing(15)
        
        # Row 1
        self.verify_button = ToolButton(
            "✅",
            "Verify Files",
            "Check file integrity and detect corrupted media"
        )
        self.verify_button.clicked.connect(lambda: self._on_tool_clicked("verify"))
        layout.addWidget(self.verify_button, 0, 0)
        
        self.duplicates_button = ToolButton(
            "🔄",
            "Remove Duplicates",
            "Detect and remove duplicate files using hash comparison"
        )
        self.duplicates_button.clicked.connect(
            lambda: self._on_tool_clicked("duplicates")
        )
        layout.addWidget(self.duplicates_button, 0, 1)
        
        # Row 2
        self.overlays_button = ToolButton(
            "🎨",
            "Apply Overlays",
            "Composite Snapchat overlays onto media files"
        )
        self.overlays_button.clicked.connect(
            lambda: self._on_tool_clicked("overlays")
        )
        layout.addWidget(self.overlays_button, 1, 0)
        
        self.timezone_button = ToolButton(
            "🌍",
            "Convert Timezone",
            "Convert timestamps using GPS-based timezone detection"
        )
        self.timezone_button.clicked.connect(
            lambda: self._on_tool_clicked("timezone")
        )
        layout.addWidget(self.timezone_button, 1, 1)
        
        # Row 3
        self.year_button = ToolButton(
            "📅",
            "Organize by Year",
            "Reorganize files into year-based folder structure"
        )
        self.year_button.clicked.connect(lambda: self._on_tool_clicked("year"))
        layout.addWidget(self.year_button, 2, 0)
        
        self.timestamp_button = ToolButton(
            "⏰",
            "Fix Timestamps",
            "Correct file timestamps from EXIF metadata"
        )
        self.timestamp_button.clicked.connect(
            lambda: self._on_tool_clicked("timestamp")
        )
        layout.addWidget(self.timestamp_button, 2, 1)
        
        return group
    
    def _create_statistics_display(self) -> QGroupBox:
        """Create statistics display area.
        
        Returns:
            QGroupBox with statistics text area
        """
        group = QGroupBox("📊 Results & Statistics")
        layout = QVBoxLayout(group)
        
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setMaximumHeight(200)
        self.stats_text.setPlaceholderText(
            "Statistics and results will appear here after running a tool..."
        )
        layout.addWidget(self.stats_text)
        
        return group
    
    @Slot()
    def _on_browse_folder(self):
        """Handle browse folder button click."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Folder",
            str(Path.home()),
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        
        if folder:
            self._selected_folder = Path(folder)
            self.folder_input.setText(str(self._selected_folder))
            logger.info(f"Selected folder: {self._selected_folder}")
    
    @Slot(str)
    def _on_tool_clicked(self, tool_name: str):
        """Handle tool button click.
        
        Args:
            tool_name: Name of the tool that was clicked
        """
        # Validate folder selection
        if not self._selected_folder:
            QMessageBox.warning(
                self,
                "No Folder Selected",
                "Please select a target folder before running a tool.",
            )
            return
        
        if not self._selected_folder.exists():
            QMessageBox.warning(
                self,
                "Invalid Folder",
                f"The selected folder does not exist:\n{self._selected_folder}",
            )
            return
        
        # Check if already running
        if self._is_running:
            QMessageBox.warning(
                self,
                "Tool Running",
                "A tool is currently running. Please wait for it to complete "
                "or cancel it before starting another tool.",
            )
            return
        
        logger.info(f"Tool clicked: {tool_name}")
        self._current_tool = tool_name
        
        # Show confirmation dialog with tool-specific message
        confirmation = self._get_tool_confirmation(tool_name)
        
        result = QMessageBox.question(
            self,
            f"Run {self._get_tool_title(tool_name)}",
            confirmation,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if result == QMessageBox.Yes:
            self._run_tool(tool_name)
    
    def _get_tool_title(self, tool_name: str) -> str:
        """Get the display title for a tool.
        
        Args:
            tool_name: Internal tool name
            
        Returns:
            Display title for the tool
        """
        titles = {
            "verify": "Verify Files",
            "duplicates": "Remove Duplicates",
            "overlays": "Apply Overlays",
            "timezone": "Convert Timezone",
            "year": "Organize by Year",
            "timestamp": "Fix Timestamps",
        }
        return titles.get(tool_name, tool_name)
    
    def _get_tool_confirmation(self, tool_name: str) -> str:
        """Get confirmation message for a tool.
        
        Args:
            tool_name: Internal tool name
            
        Returns:
            Confirmation message text
        """
        confirmations = {
            "verify": (
                f"Verify all files in:\n{self._selected_folder}\n\n"
                "This will check file integrity and detect any corrupted media.\n"
                "No files will be modified.\n\n"
                "Do you want to continue?"
            ),
            "duplicates": (
                f"Remove duplicates in:\n{self._selected_folder}\n\n"
                "This will detect duplicate files using hash comparison and "
                "move duplicates to a 'duplicates' subfolder.\n\n"
                "Do you want to continue?"
            ),
            "overlays": (
                f"Apply overlays to files in:\n{self._selected_folder}\n\n"
                "This will composite Snapchat overlays onto media files to "
                "recreate the original Snapchat appearance.\n\n"
                "Do you want to continue?"
            ),
            "timezone": (
                f"Convert timezone for files in:\n{self._selected_folder}\n\n"
                "This will convert file timestamps using GPS-based timezone "
                "detection and update EXIF metadata.\n\n"
                "Do you want to continue?"
            ),
            "year": (
                f"Organize files by year in:\n{self._selected_folder}\n\n"
                "This will reorganize files into year-based subfolders "
                "(e.g., 2023/, 2024/, 2025/).\n\n"
                "Do you want to continue?"
            ),
            "timestamp": (
                f"Fix timestamps for files in:\n{self._selected_folder}\n\n"
                "This will correct file timestamps using EXIF metadata "
                "from the images and videos.\n\n"
                "Do you want to continue?"
            ),
        }
        return confirmations.get(tool_name, "Do you want to run this tool?")
    
    def _run_tool(self, tool_name: str):
        """Run the selected tool.
        
        Args:
            tool_name: Name of tool to run
        """
        logger.info(f"Starting tool: {tool_name}")
        
        # Disable all tool buttons
        self._set_tools_enabled(False)
        self._is_running = True
        
        # Clear previous statistics
        self.stats_text.clear()
        
        # Start progress
        self.progress_widget.start(0, f"Preparing {self._get_tool_title(tool_name)}...")
        
        # Emit signal
        self.tool_started.emit(tool_name)
        
        # Create and start worker
        self._worker = ToolsWorker(tool_name, self._selected_folder)
        
        # Connect signals
        self._worker.progress_updated.connect(self._on_progress_updated)
        self._worker.tool_completed.connect(self._on_tool_completed)
        self._worker.tool_failed.connect(self._on_tool_failed)
        self._worker.finished.connect(self._on_worker_finished)
        
        # Start worker
        self._worker.start()
        logger.info(f"Worker started for tool: {tool_name}")
    
    def _set_tools_enabled(self, enabled: bool):
        """Enable or disable all tool buttons.
        
        Args:
            enabled: Whether to enable the buttons
        """
        self.verify_button.setEnabled(enabled)
        self.duplicates_button.setEnabled(enabled)
        self.overlays_button.setEnabled(enabled)
        self.timezone_button.setEnabled(enabled)
        self.year_button.setEnabled(enabled)
        self.timestamp_button.setEnabled(enabled)
        self.folder_button.setEnabled(enabled)
    
    @Slot()
    def _on_cancel_requested(self):
        """Handle cancel request from progress widget."""
        if not self._is_running or not self._worker:
            return
        
        logger.info(f"Cancel requested for tool: {self._current_tool}")
        
        # Cancel the worker
        self._worker.cancel()
        
        # Emit signal
        if self._current_tool:
            self.tool_cancelled.emit(self._current_tool)
    
    @Slot(str)
    def update_statistics(self, stats: str):
        """Update the statistics display.
        
        Args:
            stats: Statistics text to display
        """
        self.stats_text.setPlainText(stats)
        logger.debug("Statistics updated")
    
    @Slot(int, int, str)
    def _on_progress_updated(self, current: int, total: int, message: str):
        """Handle progress update from worker.
        
        Args:
            current: Current item count
            total: Total item count
            message: Status message
        """
        if total > 0:
            percentage = int((current / total) * 100)
            self.progress_widget.update_progress(current, total, message)
        else:
            self.progress_widget.set_status(message)
    
    @Slot(dict)
    def _on_tool_completed(self, results: dict):
        """Handle tool completion.
        
        Args:
            results: Results dictionary from the tool
        """
        logger.info(f"Tool completed: {results.get('tool_name', 'unknown')}")
        
        # Format and display statistics
        stats_text = self._format_results(results)
        self.update_statistics(stats_text)
        
        # Show completion message
        tool_name = results.get('tool_name', 'Tool')
        QMessageBox.information(
            self,
            "Tool Completed",
            f"{self._get_tool_title(tool_name)} completed successfully!\n\n"
            f"Check the Results & Statistics section for details."
        )
        
        # Emit signal
        self.tool_completed.emit(results.get('tool_name', ''))
    
    @Slot(str)
    def _on_tool_failed(self, error_message: str):
        """Handle tool failure.
        
        Args:
            error_message: Error message from the tool
        """
        logger.error(f"Tool failed: {error_message}")
        
        # Display error
        self.stats_text.setPlainText(f"ERROR: {error_message}")
        
        # Show error dialog
        QMessageBox.critical(
            self,
            "Tool Failed",
            f"The tool operation failed:\n\n{error_message}"
        )
    
    @Slot()
    def _on_worker_finished(self):
        """Handle worker thread completion."""
        logger.debug("Worker thread finished")
        
        # Reset state
        self._is_running = False
        self._set_tools_enabled(True)
        self.progress_widget.complete("Tool operation complete!")
        
        # Clean up worker
        if self._worker:
            self._worker.deleteLater()
            self._worker = None
    
    def _format_results(self, results: dict) -> str:
        """Format results dictionary into readable text.
        
        Args:
            results: Results dictionary from tool
            
        Returns:
            Formatted statistics text
        """
        tool_name = results.get('tool_name', 'unknown')
        
        if tool_name == 'verify':
            return self._format_verify_results(results)
        elif tool_name == 'duplicates':
            return self._format_duplicates_results(results)
        elif tool_name == 'year':
            return self._format_year_results(results)
        elif tool_name == 'timestamp':
            return self._format_timestamp_results(results)
        elif tool_name == 'timezone':
            return self._format_timezone_results(results)
        elif tool_name == 'overlays':
            return self._format_overlays_results(results)
        else:
            return str(results)
    
    def _format_verify_results(self, results: dict) -> str:
        """Format verification results."""
        return f"""FILE VERIFICATION RESULTS
{'=' * 50}

Total Files Scanned: {results.get('total_files', 0)}
Valid Files: {results.get('valid_files', 0)}
Corrupted Files: {results.get('corrupted_files', 0)}
Unsupported Files: {results.get('unsupported_files', 0)}

Status: {'✅ All files are valid' if results.get('corrupted_files', 0) == 0 else '⚠️ Some files are corrupted'}

{f"Corrupted files: {', '.join(results.get('corrupted_list', [])[:10])}" if results.get('corrupted_list') else ''}
"""
    
    def _format_duplicates_results(self, results: dict) -> str:
        """Format duplicate removal results."""
        bytes_saved = results.get('bytes_saved', 0)
        mb_saved = bytes_saved / (1024 * 1024)
        
        return f"""DUPLICATE REMOVAL RESULTS
{'=' * 50}

Total Files Scanned: {results.get('total_files', 0)}
Unique Files: {results.get('unique_files', 0)}
Duplicate Files Found: {results.get('duplicate_files', 0)}
Space Saved: {mb_saved:.2f} MB

Duplicates moved to: {self._selected_folder}/duplicates/

Status: {'✅ No duplicates found' if results.get('duplicate_files', 0) == 0 else f"✅ {results.get('duplicate_files', 0)} duplicates removed"}
"""
    
    def _format_year_results(self, results: dict) -> str:
        """Format year organization results."""
        years = results.get('years_created', [])
        years_str = ', '.join(years) if years else 'None'
        
        return f"""YEAR ORGANIZATION RESULTS
{'=' * 50}

Total Files Processed: {results.get('total_files', 0)}
Files Organized: {results.get('organized_files', 0)}
Files Failed: {results.get('failed_files', 0)}

Year Folders Created: {years_str}

Status: ✅ Files organized into year-based folders
"""
    
    def _format_timestamp_results(self, results: dict) -> str:
        """Format timestamp correction results."""
        return f"""TIMESTAMP CORRECTION RESULTS
{'=' * 50}

Total Files Processed: {results.get('total_files', 0)}
Timestamps Fixed: {results.get('fixed_files', 0)}
Files Skipped: {results.get('skipped_files', 0)}
Files Failed: {results.get('failed_files', 0)}

Status: ✅ Timestamps corrected from EXIF metadata
"""
    
    def _format_timezone_results(self, results: dict) -> str:
        """Format timezone conversion results."""
        return f"""TIMEZONE CONVERSION RESULTS
{'=' * 50}

Total Files Processed: {results.get('total_files', 0)}
Files Converted: {results.get('converted_files', 0)}
No GPS Data: {results.get('no_gps_files', 0)}
Files Failed: {results.get('failed_files', 0)}

Status: ⚠️ Timezone conversion not yet fully implemented
"""
    
    def _format_overlays_results(self, results: dict) -> str:
        """Format overlay application results."""
        return f"""OVERLAY APPLICATION RESULTS
{'=' * 50}

Total Files Processed: {results.get('total_files', 0)}
Overlays Applied: {results.get('processed_files', 0)}
Files Skipped: {results.get('skipped_files', 0)}
Files Failed: {results.get('failed_files', 0)}

Status: ⚠️ Overlay application not yet fully implemented
"""
