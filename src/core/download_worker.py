"""
Download Worker - QThread for background downloading

This module provides a QThread worker that runs the download process
in the background without blocking the GUI.
"""

import time
from pathlib import Path
from typing import Dict
from PySide6.QtCore import QThread, Signal

from src.core.downloader import DownloadCore, DownloadProgress
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DownloadWorker(QThread):
    """Background worker thread for downloading Snapchat memories.
    
    This QThread runs the download process in the background and emits
    signals to update the GUI with progress information.
    
    Signals:
        progress_updated: Emitted when progress changes (DownloadProgress object)
        status_message: Emitted with status text (str)
        file_downloaded: Emitted when a file is downloaded (filename, success, message)
        finished: Emitted when download completes (success, total_downloaded, total_failed)
        error: Emitted on critical error (error_message)
    """
    
    # Define signals
    progress_updated = Signal(object)  # DownloadProgress object
    status_message = Signal(str)       # Status text
    file_downloaded = Signal(str, bool, str)  # filename, success, message
    finished = Signal(bool, int, int)  # success, total_downloaded, total_failed
    error = Signal(str)                # error_message
    
    def __init__(self, config: Dict):
        """Initialize the download worker.
        
        Args:
            config: Configuration dictionary containing:
                - html_file: Path to memories_history.html
                - output_dir: Output directory for downloads
                - delay: Delay between downloads (seconds)
                - gps_enabled: Whether to extract GPS data
                - overlay_enabled: Whether to composite overlays
                - timezone_enabled: Whether to convert timezones
                - year_folders: Whether to organize by year
        """
        super().__init__()
        
        self.config = config
        self.downloader: DownloadCore = None
        self._is_running = False
        self._should_stop = False
        
        logger.info(f"DownloadWorker initialized with config: {config}")
    
    def run(self):
        """Main thread execution - runs the download process."""
        self._is_running = True
        self._should_stop = False
        
        try:
            # Initialize downloader
            self.status_message.emit("Initializing downloader...")
            self.downloader = DownloadCore(
                html_file=self.config['html_file'],
                output_dir=self.config['output_dir']
            )
            
            # Load existing progress
            self.status_message.emit("Loading previous progress...")
            self.downloader.load_progress()
            
            # Parse HTML to get memories list
            self.status_message.emit("Parsing HTML file...")
            memories = self.downloader.parse_html_for_memories()
            
            if not memories:
                self.error.emit("No memories found in HTML file")
                self.finished.emit(False, 0, 0)
                return
            
            # Setup progress tracking
            self.downloader.progress.total_files = len(memories)
            already_downloaded = len([m for m in memories if self.downloader.is_downloaded(m['sid'])])
            self.downloader.progress.skipped_files = already_downloaded
            
            # Emit initial status
            self.status_message.emit(
                f"Found {len(memories)} memories ({already_downloaded} already downloaded)"
            )
            self.progress_updated.emit(self.downloader.progress)
            
            # Download each memory
            delay = self.config.get('delay', 2.0)
            start_time = time.time()
            
            for i, memory in enumerate(memories, 1):
                # Check if we should stop
                if self._should_stop:
                    self.status_message.emit("Download cancelled by user")
                    break
                
                # Update current file
                self.downloader.progress.current_file = memory['filename']
                
                # Calculate ETA
                if i > 1:
                    elapsed = time.time() - start_time
                    files_processed = self.downloader.progress.downloaded_files + self.downloader.progress.skipped_files
                    if files_processed > 0:
                        avg_time_per_file = elapsed / files_processed
                        remaining_files = self.downloader.progress.total_files - files_processed
                        self.downloader.progress.eta_seconds = int(avg_time_per_file * remaining_files)
                        self.downloader.progress.current_speed = files_processed / elapsed
                
                # Emit progress
                self.progress_updated.emit(self.downloader.progress)
                
                # Download the file
                success, message = self.downloader.download_memory(memory)
                
                # Emit file status
                self.file_downloaded.emit(memory['filename'], success, message)
                
                if success and message != "Already downloaded":
                    self.status_message.emit(f"Downloaded: {memory['filename']}")
                elif not success:
                    self.status_message.emit(f"Failed: {memory['filename']} - {message}")
                
                # Update progress
                self.progress_updated.emit(self.downloader.progress)
                
                # Delay between downloads (except for last file or already downloaded)
                if i < len(memories) and message != "Already downloaded":
                    time.sleep(delay)
            
            # Final statistics
            downloaded = self.downloader.progress.downloaded_files
            failed = self.downloader.progress.failed_files
            skipped = self.downloader.progress.skipped_files
            
            if self._should_stop:
                self.status_message.emit(
                    f"Download cancelled - {downloaded} downloaded, {failed} failed, {skipped} skipped"
                )
                self.finished.emit(False, downloaded, failed)
            else:
                self.status_message.emit(
                    f"Download complete - {downloaded} new, {failed} failed, {skipped} existing"
                )
                self.finished.emit(True, downloaded, failed)
            
        except FileNotFoundError as e:
            logger.error(f"File not found: {e}")
            self.error.emit(f"File not found: {str(e)}")
            self.finished.emit(False, 0, 0)
            
        except Exception as e:
            logger.exception(f"Download error: {e}")
            self.error.emit(f"Download failed: {str(e)}")
            self.finished.emit(False, 0, 0)
            
        finally:
            self._is_running = False
    
    def stop(self):
        """Request the worker to stop downloading."""
        logger.info("Stop requested for download worker")
        self._should_stop = True
        self.status_message.emit("Stopping download...")
    
    @property
    def is_running(self) -> bool:
        """Check if worker is currently running."""
        return self._is_running
