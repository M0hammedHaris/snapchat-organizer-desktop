"""Core logic for utility tools.

This module provides the backend implementation for various utility tools:
- File verification
- Duplicate detection and removal
- Overlay application
- Timezone conversion
- Year-based organization
- Timestamp correction
"""

import hashlib
import shutil
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from datetime import datetime
from collections import defaultdict

from PIL import Image
import piexif

from ..utils.logger import get_logger

logger = get_logger(__name__)


class ToolsCore:
    """Core implementation of utility tools."""
    
    SUPPORTED_IMAGE_FORMATS = {'.jpg', '.jpeg', '.png', '.heic', '.heif'}
    SUPPORTED_VIDEO_FORMATS = {'.mp4', '.mov', '.avi', '.mkv'}
    
    def __init__(self, target_folder: Path):
        """Initialize the tools core.
        
        Args:
            target_folder: Folder to operate on
        """
        self.target_folder = Path(target_folder)
        self._cancelled = False
        
        if not self.target_folder.exists():
            raise ValueError(f"Target folder does not exist: {target_folder}")
        
        logger.debug(f"ToolsCore initialized for: {target_folder}")
    
    def cancel(self):
        """Cancel the current operation."""
        self._cancelled = True
        logger.info("Tool operation cancelled")
    
    def verify_files(self) -> Dict[str, any]:
        """Verify file integrity.
        
        Returns:
            Dictionary with verification results
        """
        logger.info("Starting file verification")
        
        results = {
            'total_files': 0,
            'valid_files': 0,
            'corrupted_files': 0,
            'corrupted_list': [],
            'unsupported_files': 0,
        }
        
        files = self._get_media_files()
        results['total_files'] = len(files)
        
        for i, file_path in enumerate(files):
            if self._cancelled:
                logger.info("Verification cancelled")
                break
            
            try:
                # Try to open and verify the file
                if file_path.suffix.lower() in self.SUPPORTED_IMAGE_FORMATS:
                    with Image.open(file_path) as img:
                        img.verify()
                    results['valid_files'] += 1
                elif file_path.suffix.lower() in self.SUPPORTED_VIDEO_FORMATS:
                    # Basic existence check for videos
                    if file_path.stat().st_size > 0:
                        results['valid_files'] += 1
                    else:
                        results['corrupted_files'] += 1
                        results['corrupted_list'].append(str(file_path))
                else:
                    results['unsupported_files'] += 1
                    
            except Exception as e:
                logger.error(f"File verification failed for {file_path}: {e}")
                results['corrupted_files'] += 1
                results['corrupted_list'].append(str(file_path))
        
        logger.info(f"Verification complete: {results['valid_files']} valid, "
                   f"{results['corrupted_files']} corrupted")
        return results
    
    def remove_duplicates(self) -> Dict[str, any]:
        """Remove duplicate files using hash comparison.
        
        Returns:
            Dictionary with duplicate removal results
        """
        logger.info("Starting duplicate detection")
        
        results = {
            'total_files': 0,
            'unique_files': 0,
            'duplicate_files': 0,
            'bytes_saved': 0,
            'duplicates_list': [],
        }
        
        # Get all media files
        files = self._get_media_files()
        results['total_files'] = len(files)
        
        # Calculate hashes and detect duplicates
        hash_to_files: Dict[str, List[Path]] = defaultdict(list)
        
        for i, file_path in enumerate(files):
            if self._cancelled:
                logger.info("Duplicate detection cancelled")
                break
            
            try:
                file_hash = self._calculate_file_hash(file_path)
                hash_to_files[file_hash].append(file_path)
            except Exception as e:
                logger.error(f"Failed to hash {file_path}: {e}")
        
        # Create duplicates folder
        duplicates_folder = self.target_folder / "duplicates"
        duplicates_folder.mkdir(exist_ok=True)
        
        # Move duplicates
        for file_hash, file_list in hash_to_files.items():
            if len(file_list) > 1:
                # Keep the first file, move the rest
                results['unique_files'] += 1
                
                for duplicate_file in file_list[1:]:
                    if self._cancelled:
                        break
                    
                    try:
                        # Move duplicate to duplicates folder
                        dest_path = duplicates_folder / duplicate_file.name
                        
                        # Handle name collision
                        counter = 1
                        while dest_path.exists():
                            stem = duplicate_file.stem
                            suffix = duplicate_file.suffix
                            dest_path = duplicates_folder / f"{stem}_{counter}{suffix}"
                            counter += 1
                        
                        shutil.move(str(duplicate_file), str(dest_path))
                        
                        file_size = dest_path.stat().st_size
                        results['duplicate_files'] += 1
                        results['bytes_saved'] += file_size
                        results['duplicates_list'].append(str(duplicate_file))
                        
                        logger.debug(f"Moved duplicate: {duplicate_file.name}")
                        
                    except Exception as e:
                        logger.error(f"Failed to move duplicate {duplicate_file}: {e}")
            else:
                results['unique_files'] += 1
        
        logger.info(f"Duplicate removal complete: {results['duplicate_files']} "
                   f"duplicates removed, {results['bytes_saved'] / (1024*1024):.2f} MB saved")
        return results
    
    def organize_by_year(self) -> Dict[str, any]:
        """Organize files into year-based folder structure.
        
        Returns:
            Dictionary with organization results
        """
        logger.info("Starting year-based organization")
        
        results = {
            'total_files': 0,
            'organized_files': 0,
            'failed_files': 0,
            'years_created': [],
        }
        
        files = self._get_media_files()
        results['total_files'] = len(files)
        
        year_folders: Set[str] = set()
        
        for i, file_path in enumerate(files):
            if self._cancelled:
                logger.info("Organization cancelled")
                break
            
            try:
                # Get file creation date (from EXIF or file system)
                year = self._get_file_year(file_path)
                
                if year:
                    # Create year folder if it doesn't exist
                    year_folder = self.target_folder / str(year)
                    year_folder.mkdir(exist_ok=True)
                    year_folders.add(str(year))
                    
                    # Move file to year folder
                    dest_path = year_folder / file_path.name
                    
                    # Handle name collision
                    counter = 1
                    while dest_path.exists():
                        stem = file_path.stem
                        suffix = file_path.suffix
                        dest_path = year_folder / f"{stem}_{counter}{suffix}"
                        counter += 1
                    
                    shutil.move(str(file_path), str(dest_path))
                    results['organized_files'] += 1
                    
                    logger.debug(f"Moved {file_path.name} to {year} folder")
                else:
                    results['failed_files'] += 1
                    logger.warning(f"Could not determine year for {file_path.name}")
                    
            except Exception as e:
                logger.error(f"Failed to organize {file_path}: {e}")
                results['failed_files'] += 1
        
        results['years_created'] = sorted(list(year_folders))
        logger.info(f"Organization complete: {results['organized_files']} files "
                   f"organized into {len(year_folders)} year folders")
        return results
    
    def fix_timestamps(self) -> Dict[str, any]:
        """Fix file timestamps from EXIF metadata.
        
        Returns:
            Dictionary with timestamp correction results
        """
        logger.info("Starting timestamp correction")
        
        results = {
            'total_files': 0,
            'fixed_files': 0,
            'skipped_files': 0,
            'failed_files': 0,
        }
        
        files = self._get_media_files()
        results['total_files'] = len(files)
        
        for i, file_path in enumerate(files):
            if self._cancelled:
                logger.info("Timestamp correction cancelled")
                break
            
            # Only process image files
            if file_path.suffix.lower() not in self.SUPPORTED_IMAGE_FORMATS:
                results['skipped_files'] += 1
                continue
            
            try:
                # Get EXIF timestamp
                timestamp = self._get_exif_timestamp(file_path)
                
                if timestamp:
                    # Update file modification time
                    import os
                    os.utime(file_path, (timestamp, timestamp))
                    results['fixed_files'] += 1
                    logger.debug(f"Fixed timestamp for {file_path.name}")
                else:
                    results['skipped_files'] += 1
                    
            except Exception as e:
                logger.error(f"Failed to fix timestamp for {file_path}: {e}")
                results['failed_files'] += 1
        
        logger.info(f"Timestamp correction complete: {results['fixed_files']} files fixed")
        return results
    
    def convert_timezone(self) -> Dict[str, any]:
        """Convert timestamps using GPS-based timezone detection.
        
        Returns:
            Dictionary with timezone conversion results
        """
        logger.info("Starting timezone conversion")
        
        # Placeholder implementation
        results = {
            'total_files': 0,
            'converted_files': 0,
            'no_gps_files': 0,
            'failed_files': 0,
        }
        
        files = self._get_media_files()
        results['total_files'] = len(files)
        
        # TODO: Implement GPS-based timezone conversion
        # This requires timezonefinder library and GPS coordinate extraction
        
        logger.info("Timezone conversion not yet fully implemented")
        return results
    
    def apply_overlays(self) -> Dict[str, any]:
        """Apply Snapchat overlays to media files.
        
        Returns:
            Dictionary with overlay application results
        """
        logger.info("Starting overlay application")
        
        # Placeholder implementation
        results = {
            'total_files': 0,
            'processed_files': 0,
            'skipped_files': 0,
            'failed_files': 0,
        }
        
        files = self._get_media_files()
        results['total_files'] = len(files)
        
        # TODO: Implement overlay compositing
        # This requires overlay image files and compositing logic
        
        logger.info("Overlay application not yet fully implemented")
        return results
    
    # Helper methods
    
    def _get_media_files(self) -> List[Path]:
        """Get all media files in the target folder.
        
        Returns:
            List of media file paths
        """
        media_files = []
        
        all_formats = self.SUPPORTED_IMAGE_FORMATS | self.SUPPORTED_VIDEO_FORMATS
        
        for file_path in self.target_folder.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in all_formats:
                media_files.append(file_path)
        
        logger.debug(f"Found {len(media_files)} media files")
        return media_files
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Hexadecimal hash string
        """
        sha256_hash = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            # Read in chunks for memory efficiency
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()
    
    def _get_file_year(self, file_path: Path) -> Optional[int]:
        """Get the year from a file's EXIF or creation date.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Year as integer, or None if unavailable
        """
        try:
            # Try EXIF first for images
            if file_path.suffix.lower() in self.SUPPORTED_IMAGE_FORMATS:
                timestamp = self._get_exif_timestamp(file_path)
                if timestamp:
                    return datetime.fromtimestamp(timestamp).year
            
            # Fall back to file modification time
            return datetime.fromtimestamp(file_path.stat().st_mtime).year
            
        except Exception as e:
            logger.error(f"Failed to get year for {file_path}: {e}")
            return None
    
    def _get_exif_timestamp(self, file_path: Path) -> Optional[float]:
        """Get timestamp from EXIF data.
        
        Args:
            file_path: Path to the image file
            
        Returns:
            Unix timestamp, or None if unavailable
        """
        try:
            img = Image.open(file_path)
            exif_dict = piexif.load(img.info.get('exif', b''))
            
            # Try DateTimeOriginal first
            if piexif.ExifIFD.DateTimeOriginal in exif_dict.get("Exif", {}):
                date_str = exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal].decode()
                dt = datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
                return dt.timestamp()
            
            # Fall back to DateTime
            if piexif.ImageIFD.DateTime in exif_dict.get("0th", {}):
                date_str = exif_dict["0th"][piexif.ImageIFD.DateTime].decode()
                dt = datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
                return dt.timestamp()
            
        except Exception as e:
            logger.debug(f"No EXIF timestamp for {file_path.name}: {e}")
        
        return None
