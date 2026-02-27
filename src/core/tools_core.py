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
        
        Extracts GPS coordinates from EXIF data, determines the timezone
        using timezonefinder, and updates the EXIF timestamps accordingly.
        
        Returns:
            Dictionary with timezone conversion results
        """
        logger.info("Starting timezone conversion")
        
        results = {
            'total_files': 0,
            'converted_files': 0,
            'no_gps_files': 0,
            'failed_files': 0,
            'conversion_details': [],
        }
        
        files = self._get_media_files()
        results['total_files'] = len(files)
        
        # Only process images (videos don't have EXIF GPS data typically)
        image_files = [f for f in files if f.suffix.lower() in self.SUPPORTED_IMAGE_FORMATS]
        
        for i, file_path in enumerate(image_files):
            if self._cancelled:
                logger.info("Timezone conversion cancelled")
                break
            
            try:
                # Extract GPS coordinates
                gps_coords = self._extract_gps_coordinates(file_path)
                
                if gps_coords is None:
                    results['no_gps_files'] += 1
                    logger.debug(f"No GPS data in {file_path.name}")
                    continue
                
                lat, lon = gps_coords
                
                # Get timezone from coordinates
                timezone_name = self._get_timezone_from_gps(lat, lon)
                
                if timezone_name is None:
                    results['failed_files'] += 1
                    logger.warning(f"Could not determine timezone for {file_path.name}")
                    continue
                
                # Update EXIF timestamp with timezone
                if self._update_exif_timezone(file_path, timezone_name):
                    results['converted_files'] += 1
                    results['conversion_details'].append({
                        'file': file_path.name,
                        'lat': lat,
                        'lon': lon,
                        'timezone': timezone_name
                    })
                    logger.debug(f"Converted {file_path.name} to {timezone_name}")
                else:
                    results['failed_files'] += 1
                    
            except Exception as e:
                logger.error(f"Failed to convert timezone for {file_path}: {e}")
                results['failed_files'] += 1
        
        logger.info(f"Timezone conversion complete: {results['converted_files']} converted, "
                   f"{results['no_gps_files']} no GPS, {results['failed_files']} failed")
        return results
    
    def apply_overlays(self, overlay_folder: Optional[Path] = None) -> Dict[str, any]:
        """Apply Snapchat overlays to media files.
        
        Looks for overlay files matching base media files and composites them.
        Overlay files should have "-overlay" suffix (e.g., photo-overlay.png).
        
        Args:
            overlay_folder: Optional folder containing overlays (default: same as target)
        
        Returns:
            Dictionary with overlay application results
        """
        logger.info("Starting overlay application")
        
        results = {
            'total_files': 0,
            'processed_files': 0,
            'skipped_files': 0,
            'failed_files': 0,
            'no_overlay_files': 0,
        }
        
        # Get base media files (images only for now)
        image_files = [f for f in self._get_media_files() 
                       if f.suffix.lower() in self.SUPPORTED_IMAGE_FORMATS]
        results['total_files'] = len(image_files)
        
        # Filter out overlay files from base files
        base_files = [f for f in image_files if '-overlay' not in f.stem.lower()]
        
        # Build overlay map
        if overlay_folder is None:
            overlay_folder = self.target_folder
        
        overlay_map = self._build_overlay_map(overlay_folder)
        
        for i, file_path in enumerate(base_files):
            if self._cancelled:
                logger.info("Overlay application cancelled")
                break
            
            try:
                # Find matching overlay
                overlay_path = self._find_overlay_for_file(file_path, overlay_map)
                
                if overlay_path is None:
                    results['no_overlay_files'] += 1
                    logger.debug(f"No overlay found for {file_path.name}")
                    continue
                
                # Apply overlay
                if self._apply_overlay_to_image(file_path, overlay_path):
                    results['processed_files'] += 1
                    logger.debug(f"Applied overlay to {file_path.name}")
                else:
                    results['failed_files'] += 1
                    
            except Exception as e:
                logger.error(f"Failed to apply overlay to {file_path}: {e}")
                results['failed_files'] += 1
        
        results['skipped_files'] = results['no_overlay_files']
        logger.info(f"Overlay application complete: {results['processed_files']} processed, "
                   f"{results['no_overlay_files']} no overlay, {results['failed_files']} failed")
        return results
    
    # GPS and timezone helper methods
    
    def _extract_gps_coordinates(self, file_path: Path) -> Optional[Tuple[float, float]]:
        """Extract GPS coordinates from image EXIF data.
        
        Args:
            file_path: Path to the image file
            
        Returns:
            Tuple of (latitude, longitude) or None if not available
        """
        try:
            img = Image.open(file_path)
            exif_data = img.info.get('exif', b'')
            
            if not exif_data:
                return None
            
            exif_dict = piexif.load(exif_data)
            gps_data = exif_dict.get("GPS", {})
            
            if not gps_data:
                return None
            
            # Extract latitude
            lat_data = gps_data.get(piexif.GPSIFD.GPSLatitude)
            lat_ref = gps_data.get(piexif.GPSIFD.GPSLatitudeRef)
            
            # Extract longitude
            lon_data = gps_data.get(piexif.GPSIFD.GPSLongitude)
            lon_ref = gps_data.get(piexif.GPSIFD.GPSLongitudeRef)
            
            if not all([lat_data, lat_ref, lon_data, lon_ref]):
                return None
            
            # Convert to decimal degrees
            lat = self._gps_to_decimal(lat_data)
            lon = self._gps_to_decimal(lon_data)
            
            # Apply reference (N/S, E/W)
            if lat_ref == b'S':
                lat = -lat
            if lon_ref == b'W':
                lon = -lon
            
            return (lat, lon)
            
        except Exception as e:
            logger.debug(f"Failed to extract GPS from {file_path.name}: {e}")
            return None
    
    def _gps_to_decimal(self, gps_data) -> float:
        """Convert GPS EXIF data to decimal degrees.
        
        Args:
            gps_data: GPS data from EXIF (tuple of rationals)
            
        Returns:
            Decimal degrees as float
        """
        degrees = gps_data[0][0] / gps_data[0][1]
        minutes = gps_data[1][0] / gps_data[1][1]
        seconds = gps_data[2][0] / gps_data[2][1]
        
        return degrees + (minutes / 60.0) + (seconds / 3600.0)
    
    def _get_timezone_from_gps(self, lat: float, lon: float) -> Optional[str]:
        """Get timezone name from GPS coordinates.
        
        Args:
            lat: Latitude in decimal degrees
            lon: Longitude in decimal degrees
            
        Returns:
            Timezone name (e.g., 'America/New_York') or None
        """
        try:
            from timezonefinder import TimezoneFinder
            tf = TimezoneFinder()
            return tf.timezone_at(lat=lat, lng=lon)
        except ImportError:
            logger.warning("timezonefinder not installed, cannot determine timezone")
            return None
        except Exception as e:
            logger.error(f"Error determining timezone for ({lat}, {lon}): {e}")
            return None
    
    def _update_exif_timezone(self, file_path: Path, timezone_name: str) -> bool:
        """Update EXIF timestamp with timezone information.
        
        This converts the existing DateTimeOriginal to include timezone offset
        and updates the file accordingly.
        
        Args:
            file_path: Path to the image file
            timezone_name: Timezone name (e.g., 'America/New_York')
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import pytz
            
            # Load image and EXIF
            img = Image.open(file_path)
            exif_bytes = img.info.get('exif', b'')
            
            if not exif_bytes:
                return False
            
            exif_dict = piexif.load(exif_bytes)
            
            # Get current timestamp
            if piexif.ExifIFD.DateTimeOriginal not in exif_dict.get("Exif", {}):
                return False
            
            date_str = exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal].decode()
            
            # Parse datetime
            naive_dt = datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
            
            # Localize to the GPS-derived timezone
            tz = pytz.timezone(timezone_name)
            local_dt = tz.localize(naive_dt)
            
            # Store the offset in OffsetTime tags (EXIF 2.31+)
            offset_str = local_dt.strftime("%z")
            offset_formatted = f"{offset_str[:3]}:{offset_str[3:]}"  # Format: +HH:MM
            
            # Update EXIF with offset tags
            if "Exif" not in exif_dict:
                exif_dict["Exif"] = {}
            
            # OffsetTimeOriginal tag (0x9011)
            exif_dict["Exif"][36881] = offset_formatted.encode()
            
            # Save updated EXIF
            exif_bytes = piexif.dump(exif_dict)
            
            # Save image with updated EXIF
            img.save(file_path, exif=exif_bytes)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update timezone for {file_path}: {e}")
            return False
    
    # Overlay helper methods
    
    def _build_overlay_map(self, overlay_folder: Path) -> Dict[str, Path]:
        """Build a map of base names to overlay file paths.
        
        Args:
            overlay_folder: Folder containing overlay files
            
        Returns:
            Dictionary mapping base names to overlay paths
        """
        overlay_map = {}
        
        for file_path in overlay_folder.rglob("*"):
            if file_path.is_file() and '-overlay' in file_path.stem.lower():
                # Extract base name (remove -overlay suffix)
                base_name = file_path.stem.lower().replace('-overlay', '')
                overlay_map[base_name] = file_path
        
        logger.debug(f"Found {len(overlay_map)} overlay files")
        return overlay_map
    
    def _find_overlay_for_file(self, file_path: Path, overlay_map: Dict[str, Path]) -> Optional[Path]:
        """Find the overlay file for a given media file.
        
        Args:
            file_path: Path to the base media file
            overlay_map: Dictionary of base names to overlay paths
            
        Returns:
            Path to overlay file or None if not found
        """
        # Try exact match
        base_name = file_path.stem.lower()
        if base_name in overlay_map:
            return overlay_map[base_name]
        
        # Try without extension-like suffixes
        # e.g., "photo_123" might match "photo_123-overlay"
        for overlay_base, overlay_path in overlay_map.items():
            if base_name.startswith(overlay_base) or overlay_base.startswith(base_name):
                return overlay_path
        
        return None
    
    def _apply_overlay_to_image(self, base_path: Path, overlay_path: Path) -> bool:
        """Composite an overlay onto a base image.
        
        The overlay is centered and scaled to fit the base image.
        The original EXIF data is preserved.
        
        Args:
            base_path: Path to the base image
            overlay_path: Path to the overlay image
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Open base image
            with Image.open(base_path) as base_img:
                # Preserve EXIF
                exif_bytes = base_img.info.get('exif', b'')
                
                # Convert to RGBA for compositing
                if base_img.mode != 'RGBA':
                    base_img = base_img.convert('RGBA')
                
                # Open overlay
                with Image.open(overlay_path) as overlay_img:
                    # Convert overlay to RGBA
                    if overlay_img.mode != 'RGBA':
                        overlay_img = overlay_img.convert('RGBA')
                    
                    # Resize overlay to match base image if needed
                    if overlay_img.size != base_img.size:
                        overlay_img = overlay_img.resize(base_img.size, Image.Resampling.LANCZOS)
                    
                    # Composite overlay onto base
                    result = Image.alpha_composite(base_img, overlay_img)
                
                # Convert back to RGB for saving as JPEG
                if base_path.suffix.lower() in {'.jpg', '.jpeg'}:
                    result = result.convert('RGB')
                
                # Save with original EXIF
                if exif_bytes:
                    result.save(base_path, exif=exif_bytes)
                else:
                    result.save(base_path)
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply overlay to {base_path}: {e}")
            return False
    
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
