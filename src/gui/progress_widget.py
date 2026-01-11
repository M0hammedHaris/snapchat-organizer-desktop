"""Reusable progress widget for long-running operations.

This widget provides a consistent progress display with:
- Progress bar showing completion percentage
- Status text showing current operation
- File counters (X / Y files)
- ETA (estimated time remaining)
- Cancel button functionality
"""

from typing import Optional
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QProgressBar,
    QLabel,
    QPushButton,
)
from PySide6.QtCore import Signal, Slot, Qt
from datetime import datetime, timedelta


class ProgressWidget(QWidget):
    """Reusable progress display widget.
    
    Signals:
        cancel_requested: Emitted when user clicks Cancel button
    """
    
    cancel_requested = Signal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize the progress widget.
        
        Args:
            parent: Parent widget (optional)
        """
        super().__init__(parent)
        
        # State tracking
        self._start_time: Optional[datetime] = None
        self._current_count = 0
        self._total_count = 0
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)
        
        # Status row (file counter + ETA)
        status_layout = QHBoxLayout()
        
        self.status_label = QLabel("Ready")
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        self.eta_label = QLabel("")
        self.eta_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        status_layout.addWidget(self.eta_label)
        
        layout.addLayout(status_layout)
        
        # Current operation label
        self.operation_label = QLabel("")
        self.operation_label.setWordWrap(True)
        self.operation_label.setStyleSheet("color: #666;")
        layout.addWidget(self.operation_label)
        
        # Cancel button (hidden by default)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self._on_cancel_clicked)
        self.cancel_button.setVisible(False)
        layout.addWidget(self.cancel_button)
        
    @Slot()
    def _on_cancel_clicked(self):
        """Handle cancel button click."""
        self.cancel_button.setEnabled(False)
        self.cancel_button.setText("Cancelling...")
        self.cancel_requested.emit()
    
    def start(self, total: int, status_text: str = "Processing..."):
        """Start a new progress operation.
        
        Args:
            total: Total number of items to process
            status_text: Initial status text
        """
        self._start_time = datetime.now()
        self._current_count = 0
        self._total_count = total
        
        self.progress_bar.setValue(0)
        self.status_label.setText(f"0 / {total} files")
        self.operation_label.setText(status_text)
        self.eta_label.setText("")
        
        self.cancel_button.setVisible(True)
        self.cancel_button.setEnabled(True)
        self.cancel_button.setText("Cancel")
    
    def update_progress(
        self,
        current: int,
        total: Optional[int] = None,
        operation: Optional[str] = None,
    ):
        """Update progress display.
        
        Args:
            current: Current number of completed items
            total: Total items (if changed from start())
            operation: Current operation description (optional)
        """
        if total is not None:
            self._total_count = total
        
        self._current_count = current
        
        # Update progress bar
        if self._total_count > 0:
            percentage = int((current / self._total_count) * 100)
            self.progress_bar.setValue(percentage)
        
        # Update status text
        self.status_label.setText(f"{current} / {self._total_count} files")
        
        # Update operation text
        if operation is not None:
            self.operation_label.setText(operation)
        
        # Calculate and update ETA
        self._update_eta()
    
    def _update_eta(self):
        """Calculate and display estimated time remaining."""
        if self._start_time is None or self._current_count == 0:
            self.eta_label.setText("")
            return
        
        elapsed = (datetime.now() - self._start_time).total_seconds()
        
        if self._current_count >= self._total_count:
            # Completed
            self.eta_label.setText(f"Completed in {self._format_duration(elapsed)}")
            return
        
        # Calculate ETA
        avg_time_per_item = elapsed / self._current_count
        remaining_items = self._total_count - self._current_count
        eta_seconds = avg_time_per_item * remaining_items
        
        self.eta_label.setText(f"ETA: {self._format_duration(eta_seconds)}")
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in seconds to human-readable string.
        
        Args:
            seconds: Duration in seconds
            
        Returns:
            Formatted string (e.g., "2m 30s", "1h 5m", "45s")
        """
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours}h {minutes}m"
    
    def set_status(self, text: str):
        """Set status text without changing progress.
        
        Args:
            text: Status text to display
        """
        self.operation_label.setText(text)
    
    def set_error(self, error_text: str):
        """Display an error message.
        
        Args:
            error_text: Error message to display
        """
        self.operation_label.setText(f"❌ {error_text}")
        self.operation_label.setStyleSheet("color: #d32f2f;")
    
    def set_success(self, success_text: str):
        """Display a success message.
        
        Args:
            success_text: Success message to display
        """
        self.operation_label.setText(f"✅ {success_text}")
        self.operation_label.setStyleSheet("color: #388e3c;")
    
    def complete(self, message: str = "Operation completed successfully"):
        """Mark operation as complete.
        
        Args:
            message: Completion message
        """
        self.progress_bar.setValue(100)
        self.set_success(message)
        self.cancel_button.setVisible(False)
        self._update_eta()
    
    def reset(self):
        """Reset the widget to initial state."""
        self._start_time = None
        self._current_count = 0
        self._total_count = 0
        
        self.progress_bar.setValue(0)
        self.status_label.setText("Ready")
        self.operation_label.setText("")
        self.operation_label.setStyleSheet("color: #666;")
        self.eta_label.setText("")
        self.cancel_button.setVisible(False)
        self.cancel_button.setEnabled(True)
        self.cancel_button.setText("Cancel")
    
    def show_cancel_button(self, show: bool = True):
        """Show or hide the cancel button.
        
        Args:
            show: True to show, False to hide
        """
        self.cancel_button.setVisible(show)
