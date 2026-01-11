"""
Snapchat Memories Downloader Core Module

This module provides the core download functionality for Snapchat memories,
refactored from the CLI version for GUI integration.
"""

import os
import time
import zipfile
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class DownloadProgress:
    """Track download progress statistics."""
    total_files: int = 0
    downloaded_files: int = 0
    skipped_files: int = 0
    failed_files: int = 0
    current_file: str = ""
    current_speed: float = 0.0  # files per second
    eta_seconds: int = 0
    
    @property
    def percentage(self) -> float:
        """Calculate completion percentage."""
        if self.total_files == 0:
            return 0.0
        return (self.downloaded_files + self.skipped_files) / self.total_files * 100


class DownloadCore:
    """Core download functionality for Snapchat memories.
    
    This class handles the actual download logic, progress tracking,
    and file management. It is designed to work with both CLI and GUI.
    """
    
    def __init__(self, html_file: str, output_dir: str):
        """Initialize the downloader.
        
        Args:
            html_file: Path to memories_history.html from Snapchat export
            output_dir: Directory where memories will be saved
        """
        self.html_file = Path(html_file)
        self.output_dir = Path(output_dir)
        self.session = requests.Session()
        self.progress = DownloadProgress()
        
        # Progress tracking file
        self.progress_file = self.output_dir / "download_progress.json"
        self._downloaded_sids: set = set()
        
        # Create output directories
        self._create_output_dirs()
        
        logger.info(f"Initialized DownloadCore: {self.html_file} -> {self.output_dir}")
    
    def _create_output_dirs(self):
        """Create necessary output directory structure."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "images").mkdir(exist_ok=True)
        (self.output_dir / "videos").mkdir(exist_ok=True)
        (self.output_dir / "overlays").mkdir(exist_ok=True)
        
        logger.debug(f"Created output directories in {self.output_dir}")
    
    def parse_html_for_memories(self) -> List[Dict]:
        """Parse the HTML file to extract memory download URLs.
        
        Returns:
            List of memory dictionaries with download info
        """
        from bs4 import BeautifulSoup
        
        logger.info(f"Parsing HTML file: {self.html_file}")
        
        if not self.html_file.exists():
            raise FileNotFoundError(f"HTML file not found: {self.html_file}")
        
        with open(self.html_file, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        
        memories = []
        
        # Find all table rows with download links
        # Format: <a href="download_url" download="filename">
        for link in soup.find_all('a', download=True):
            download_url = link.get('href', '')
            download_name = link.get('download', '')
            
            if not download_url or not download_name:
                continue
            
            # Extract date from filename or surrounding text
            # Snapchat format: YYYY-MM-DD_HH-MM-SS_UTC.jpg/mp4
            memory = {
                'download_url': download_url,
                'filename': download_name,
                'sid': self._extract_sid(download_url),
                'media_type': self._detect_media_type_from_name(download_name),
                'date': self._extract_date_from_filename(download_name),
            }
            
            # Look for GPS location in surrounding table cells
            parent_row = link.find_parent('tr')
            if parent_row:
                cells = parent_row.find_all('td')
                for cell in cells:
                    text = cell.get_text(strip=True)
                    if ',' in text and any(char.isdigit() for char in text):
                        # Likely GPS coordinates
                        memory['location'] = text
                        break
            
            memories.append(memory)
        
        logger.info(f"Found {len(memories)} memories in HTML")
        return memories
    
    def _extract_sid(self, url: str) -> str:
        """Extract session ID from download URL."""
        # URL format: https://app.snapchat.com/web/deeplink/snapcode?...&sid=XXXXX
        if 'sid=' in url:
            return url.split('sid=')[1].split('&')[0]
        # Use hash of URL as fallback
        return str(hash(url))
    
    def _detect_media_type_from_name(self, filename: str) -> str:
        """Detect media type from filename extension."""
        ext = Path(filename).suffix.lower()
        if ext in ['.jpg', '.jpeg', '.png', '.heic']:
            return 'image'
        elif ext in ['.mp4', '.mov', '.avi']:
            return 'video'
        return 'unknown'
    
    def _extract_date_from_filename(self, filename: str) -> str:
        """Extract date/time from filename."""
        # Expected format: YYYY-MM-DD_HH-MM-SS_UTC.ext
        try:
            # Remove extension and split by underscore
            name_parts = Path(filename).stem.split('_')
            if len(name_parts) >= 2:
                date_part = name_parts[0]  # YYYY-MM-DD
                time_part = name_parts[1]  # HH-MM-SS
                return f"{date_part} {time_part.replace('-', ':')}"
        except Exception as e:
            logger.warning(f"Could not parse date from filename: {filename} - {e}")
        
        return "Unknown Date"
    
    def load_progress(self):
        """Load previously downloaded files from progress file."""
        import json
        
        if not self.progress_file.exists():
            logger.info("No existing progress file found")
            return
        
        try:
            with open(self.progress_file, 'r') as f:
                data = json.load(f)
                self._downloaded_sids = set(data.get('downloaded', []))
                logger.info(f"Loaded {len(self._downloaded_sids)} previously downloaded files")
        except Exception as e:
            logger.error(f"Error loading progress file: {e}")
    
    def save_progress(self, sid: str):
        """Save a successfully downloaded file to progress tracking.
        
        Args:
            sid: Session ID of the downloaded file
        """
        import json
        
        self._downloaded_sids.add(sid)
        
        try:
            with open(self.progress_file, 'w') as f:
                json.dump({'downloaded': list(self._downloaded_sids)}, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving progress: {e}")
    
    def is_downloaded(self, sid: str) -> bool:
        """Check if a file has already been downloaded.
        
        Args:
            sid: Session ID to check
            
        Returns:
            True if already downloaded
        """
        return sid in self._downloaded_sids
    
    def download_memory(self, memory: Dict) -> Tuple[bool, str]:
        """Download a single memory file.
        
        Args:
            memory: Memory dictionary with download info
            
        Returns:
            (success, message) tuple
        """
        sid = memory['sid']
        
        # Check if already downloaded
        if self.is_downloaded(sid):
            logger.debug(f"Skipping {sid} - already downloaded")
            return True, "Already downloaded"
        
        try:
            # Download the file
            logger.info(f"Downloading {memory['filename']}...")
            response = self.session.get(memory['download_url'], timeout=60)
            
            # Check for errors
            if response.status_code == 429:
                logger.warning("Rate limited by server")
                return False, "Rate limited - try again later"
            
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '')
            if 'text/html' in content_type:
                logger.error("Received HTML instead of media file")
                return False, "Server error - received HTML"
            
            # Save to temporary file
            temp_file = self.output_dir / f"temp_{sid}.download"
            with open(temp_file, 'wb') as f:
                f.write(response.content)
            
            # Process the file
            if zipfile.is_zipfile(temp_file):
                success = self._extract_zip(temp_file, memory, sid)
            else:
                success = self._save_media(temp_file, memory, sid)
            
            # Clean up temp file
            if temp_file.exists():
                temp_file.unlink()
            
            if success:
                self.save_progress(sid)
                self.progress.downloaded_files += 1
                logger.info(f"Successfully downloaded {memory['filename']}")
                return True, "Downloaded"
            else:
                self.progress.failed_files += 1
                return False, "Processing failed"
                
        except requests.RequestException as e:
            logger.error(f"Download error for {sid}: {e}")
            self.progress.failed_files += 1
            return False, f"Network error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error for {sid}: {e}")
            self.progress.failed_files += 1
            return False, f"Error: {str(e)}"
    
    def _extract_zip(self, zip_path: Path, memory: Dict, sid: str) -> bool:
        """Extract and save media from ZIP file.
        
        Args:
            zip_path: Path to temporary ZIP file
            memory: Memory metadata
            sid: Session ID
            
        Returns:
            True if successful
        """
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Extract to temp directory
                temp_dir = self.output_dir / f"temp_{sid}_extract"
                zip_ref.extractall(temp_dir)
                
                # Find the media file (usually the largest file)
                media_files = list(temp_dir.glob('*'))
                if not media_files:
                    logger.warning(f"No files found in ZIP for {sid}")
                    return False
                
                # Sort by size, take largest
                media_file = max(media_files, key=lambda p: p.stat().st_size)
                
                # Move to appropriate directory
                media_type = memory['media_type']
                if media_type == 'image':
                    dest_dir = self.output_dir / "images"
                elif media_type == 'video':
                    dest_dir = self.output_dir / "videos"
                else:
                    dest_dir = self.output_dir
                
                dest_file = dest_dir / memory['filename']
                media_file.rename(dest_file)
                
                # Clean up temp directory
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
                
                logger.debug(f"Extracted ZIP to {dest_file}")
                return True
                
        except Exception as e:
            logger.error(f"Error extracting ZIP for {sid}: {e}")
            return False
    
    def _save_media(self, temp_file: Path, memory: Dict, sid: str) -> bool:
        """Save media file to appropriate directory.
        
        Args:
            temp_file: Path to temporary downloaded file
            memory: Memory metadata
            sid: Session ID
            
        Returns:
            True if successful
        """
        try:
            media_type = memory['media_type']
            if media_type == 'image':
                dest_dir = self.output_dir / "images"
            elif media_type == 'video':
                dest_dir = self.output_dir / "videos"
            else:
                dest_dir = self.output_dir
            
            dest_file = dest_dir / memory['filename']
            temp_file.rename(dest_file)
            
            logger.debug(f"Saved media to {dest_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving media for {sid}: {e}")
            return False
