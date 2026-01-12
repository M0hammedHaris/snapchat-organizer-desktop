"""Organize worker for background processing.

This module provides the OrganizeWorker class that runs the organization
process in a separate thread to avoid blocking the UI.
"""

from pathlib import Path
from typing import Optional

from PySide6.QtCore import QThread, Signal, Slot

from .organizer import OrganizerCore
from ..utils.logger import get_logger

logger = get_logger(__name__)


class OrganizeWorker(QThread):
    """Worker thread for organizing chat media.
    
    Signals:
        progress_updated: (current, total, status) - Progress update
        stats_updated: (stats_dict) - Statistics update
        finished: (success, message) - Organization completed
        error: (error_message) - Error occurred
    """
    
    progress_updated = Signal(int, int, str)  # current, total, status
    stats_updated = Signal(dict)  # statistics dictionary
    finished = Signal(bool, str)  # success, message
    error = Signal(str)  # error message
    
    def __init__(
        self,
        export_path: Path,
        output_path: Path,
        timestamp_threshold: int = 7200,
        match_score_threshold: float = 0.45,
        enable_tier1: bool = True,
        enable_tier2: bool = True,
        enable_tier3: bool = True,
        organize_by_year: bool = True,
        create_debug_report: bool = True,
        preserve_originals: bool = True,
        parent=None,
    ):
        """Initialize the organize worker.
        
        Args:
            export_path: Path to Snapchat export folder
            output_path: Path to output folder
            timestamp_threshold: Time window for Gaussian decay scoring (default: 2 hours)
            match_score_threshold: Minimum composite score for match (default: 0.45)
            enable_tier1: Enable Media ID matching
            enable_tier2: Enable single contact matching
            enable_tier3: Enable timestamp proximity matching
            organize_by_year: Create year subdirectories
            create_debug_report: Generate detailed matching report
            preserve_originals: Create .snapchat_original sidecar files
            parent: Parent QObject
        """
        super().__init__(parent)
        
        self.export_path = Path(export_path)
        self.output_path = Path(output_path)
        self.timestamp_threshold = timestamp_threshold
        self.match_score_threshold = match_score_threshold
        self.enable_tier1 = enable_tier1
        self.enable_tier2 = enable_tier2
        self.enable_tier3 = enable_tier3
        self.organize_by_year = organize_by_year
        self.create_debug_report = create_debug_report
        self.preserve_originals = preserve_originals
        
        self.organizer: Optional[OrganizerCore] = None
        
        logger.debug("OrganizeWorker initialized")
    
    def run(self):
        """Run the organization process in background thread."""
        try:
            logger.info(f"Starting organization: {self.export_path} -> {self.output_path}")
            
            # Create organizer with progress callback
            self.organizer = OrganizerCore(
                export_path=self.export_path,
                output_path=self.output_path,
                timestamp_threshold=self.timestamp_threshold,
                match_score_threshold=self.match_score_threshold,
                enable_tier1=self.enable_tier1,
                enable_tier2=self.enable_tier2,
                enable_tier3=self.enable_tier3,
                organize_by_year=self.organize_by_year,
                create_debug_report=self.create_debug_report,
                preserve_originals=self.preserve_originals,
                progress_callback=self._on_progress,
            )
            
            # Run organization
            success = self.organizer.organize()
            
            # Emit final statistics
            self.stats_updated.emit(self.organizer.stats)
            
            if success:
                message = self._format_success_message()
                logger.info(f"Organization completed successfully: {message}")
                self.finished.emit(True, message)
            else:
                message = "Organization was cancelled or encountered an error"
                logger.warning(message)
                self.finished.emit(False, message)
                
        except Exception as e:
            error_msg = f"Organization failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error.emit(error_msg)
            self.finished.emit(False, error_msg)
    
    @Slot()
    def cancel(self):
        """Cancel the organization process."""
        if self.organizer:
            logger.info("Cancelling organization...")
            self.organizer.cancel()
    
    def _on_progress(self, current: int, total: int, status: str):
        """Handle progress updates from organizer.
        
        Args:
            current: Current progress value
            total: Total progress value
            status: Status message
        """
        self.progress_updated.emit(current, total, status)
        
        # Emit stats update periodically
        if self.organizer and current % 20 == 0:
            self.stats_updated.emit(self.organizer.stats)
    
    def _format_success_message(self) -> str:
        """Format success message with statistics.
        
        Returns:
            Formatted message string
        """
        if not self.organizer:
            return "Organization completed"
        
        stats = self.organizer.stats
        total = stats.get("total", 0)
        organized = stats.get("organized", 0)
        unmatched = stats.get("unmatched", 0)
        low_conf = stats.get("low_confidence", 0)
        exact_id = stats.get("exact_media_id", 0)
        fuzzy_id = stats.get("fuzzy_media_id", 0)
        time_based = stats.get("time_based", 0)
        
        success_rate = (organized / total * 100) if total > 0 else 0
        
        message = (
            f"Successfully organized {organized}/{total} files ({success_rate:.1f}%)\n\n"
            f"Match Type Breakdown:\n"
            f"  • Exact Media ID: {exact_id}\n"
            f"  • Fuzzy Media ID: {fuzzy_id}\n"
            f"  • Time-based: {time_based}\n"
            f"  • Unmatched: {unmatched}\n\n"
            f"Quality Metrics:\n"
            f"  • Low confidence matches: {low_conf} (score < 0.8)\n\n"
            f"Files saved to: {self.output_path}"
        )
        
        return message
