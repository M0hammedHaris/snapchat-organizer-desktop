"""Worker thread for running utility tools in the background.

This module provides QThread-based workers for executing tool operations
without blocking the UI, with progress reporting and cancellation support.
"""

from pathlib import Path
from typing import Dict, Optional

from PySide6.QtCore import QThread, Signal, Slot

from .tools_core import ToolsCore
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ToolsWorker(QThread):
    """Worker thread for executing utility tools.
    
    Signals:
        progress_updated: Emitted with (current, total, message) during processing
        tool_completed: Emitted with results dictionary when tool completes
        tool_failed: Emitted with error message if tool fails
    """
    
    progress_updated = Signal(int, int, str)  # current, total, message
    tool_completed = Signal(dict)  # results dictionary
    tool_failed = Signal(str)  # error message
    
    def __init__(
        self,
        tool_name: str,
        target_folder: Path,
        parent: Optional[QThread] = None
    ):
        """Initialize the tools worker.
        
        Args:
            tool_name: Name of tool to run
            target_folder: Folder to operate on
            parent: Parent thread (optional)
        """
        super().__init__(parent)
        
        self.tool_name = tool_name
        self.target_folder = Path(target_folder)
        self._core: Optional[ToolsCore] = None
        
        logger.debug(f"ToolsWorker initialized for {tool_name}")
    
    def run(self):
        """Execute the tool operation."""
        logger.info(f"Starting tool worker: {self.tool_name}")
        
        try:
            # Create core instance
            self._core = ToolsCore(self.target_folder)
            
            # Execute the appropriate tool
            if self.tool_name == "verify":
                results = self._run_verify()
            elif self.tool_name == "duplicates":
                results = self._run_duplicates()
            elif self.tool_name == "overlays":
                results = self._run_overlays()
            elif self.tool_name == "timezone":
                results = self._run_timezone()
            elif self.tool_name == "year":
                results = self._run_year()
            elif self.tool_name == "timestamp":
                results = self._run_timestamp()
            else:
                raise ValueError(f"Unknown tool: {self.tool_name}")
            
            # Add tool name to results
            results['tool_name'] = self.tool_name
            
            # Emit completion signal
            self.tool_completed.emit(results)
            logger.info(f"Tool worker completed: {self.tool_name}")
            
        except Exception as e:
            error_msg = f"Tool failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.tool_failed.emit(error_msg)
    
    def cancel(self):
        """Cancel the running tool operation."""
        if self._core:
            self._core.cancel()
            logger.info(f"Cancelling tool: {self.tool_name}")
    
    def _run_verify(self) -> Dict[str, any]:
        """Run file verification tool.
        
        Returns:
            Results dictionary
        """
        logger.info("Running verify tool")
        
        # Get all files first to report total
        files = self._core._get_media_files()
        total_files = len(files)
        
        self.progress_updated.emit(0, total_files, "Verifying files...")
        
        # Run verification (in a real implementation, we'd update progress)
        results = self._core.verify_files()
        
        self.progress_updated.emit(total_files, total_files, "Verification complete!")
        
        return results
    
    def _run_duplicates(self) -> Dict[str, any]:
        """Run duplicate removal tool.
        
        Returns:
            Results dictionary
        """
        logger.info("Running duplicates tool")
        
        # Get all files first
        files = self._core._get_media_files()
        total_files = len(files)
        
        self.progress_updated.emit(0, total_files, "Scanning for duplicates...")
        
        # Run duplicate detection
        results = self._core.remove_duplicates()
        
        self.progress_updated.emit(total_files, total_files, "Duplicate removal complete!")
        
        return results
    
    def _run_overlays(self) -> Dict[str, any]:
        """Run overlay application tool.
        
        Returns:
            Results dictionary
        """
        logger.info("Running overlays tool")
        
        files = self._core._get_media_files()
        total_files = len(files)
        
        self.progress_updated.emit(0, total_files, "Applying overlays...")
        
        results = self._core.apply_overlays()
        
        self.progress_updated.emit(total_files, total_files, "Overlay application complete!")
        
        return results
    
    def _run_timezone(self) -> Dict[str, any]:
        """Run timezone conversion tool.
        
        Returns:
            Results dictionary
        """
        logger.info("Running timezone tool")
        
        files = self._core._get_media_files()
        total_files = len(files)
        
        self.progress_updated.emit(0, total_files, "Converting timezones...")
        
        results = self._core.convert_timezone()
        
        self.progress_updated.emit(total_files, total_files, "Timezone conversion complete!")
        
        return results
    
    def _run_year(self) -> Dict[str, any]:
        """Run year organization tool.
        
        Returns:
            Results dictionary
        """
        logger.info("Running year organization tool")
        
        files = self._core._get_media_files()
        total_files = len(files)
        
        self.progress_updated.emit(0, total_files, "Organizing by year...")
        
        results = self._core.organize_by_year()
        
        self.progress_updated.emit(total_files, total_files, "Organization complete!")
        
        return results
    
    def _run_timestamp(self) -> Dict[str, any]:
        """Run timestamp correction tool.
        
        Returns:
            Results dictionary
        """
        logger.info("Running timestamp correction tool")
        
        files = self._core._get_media_files()
        total_files = len(files)
        
        self.progress_updated.emit(0, total_files, "Fixing timestamps...")
        
        results = self._core.fix_timestamps()
        
        self.progress_updated.emit(total_files, total_files, "Timestamp correction complete!")
        
        return results
