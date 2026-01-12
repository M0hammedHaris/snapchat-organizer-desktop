"""Chat media organizer core logic.

This module provides the OrganizerCore class that handles organizing Snapchat
chat media files by contact using a 3-tier matching strategy.
"""

import json
import shutil
import re
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Callable

from ..utils.logger import get_logger

logger = get_logger(__name__)


class OrganizerCore:
    """Core logic for organizing Snapchat chat media by contact.
    
    Uses a 3-tier matching strategy:
    - Tier 1: Media ID matching (most accurate)
    - Tier 2: Single contact on date
    - Tier 3: Timestamp proximity matching
    """
    
    def __init__(
        self,
        export_path: Path,
        output_path: Path,
        timestamp_threshold: int = 3600,
        enable_tier1: bool = True,
        enable_tier2: bool = True,
        enable_tier3: bool = True,
        organize_by_year: bool = True,
        create_debug_report: bool = True,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ):
        """Initialize the organizer.
        
        Args:
            export_path: Path to Snapchat export folder
            output_path: Path to output folder for organized media
            timestamp_threshold: Maximum seconds difference for Tier 3 matching (default: 1 hour)
            enable_tier1: Enable Media ID matching
            enable_tier2: Enable single contact matching
            enable_tier3: Enable timestamp proximity matching
            organize_by_year: Create year subdirectories
            create_debug_report: Generate detailed matching report
            progress_callback: Callback for progress updates (current, total, status)
        """
        self.export_path = Path(export_path)
        self.output_path = Path(output_path)
        self.timestamp_threshold = timestamp_threshold
        self.enable_tier1 = enable_tier1
        self.enable_tier2 = enable_tier2
        self.enable_tier3 = enable_tier3
        self.organize_by_year = organize_by_year
        self.create_debug_report = create_debug_report
        self.progress_callback = progress_callback
        
        # Processing state
        self.media_map: Dict = {}
        self.debug_report: List[Dict] = []
        self.stats = {
            "total": 0,
            "organized": 0,
            "unmatched": 0,
            "tier1": 0,
            "tier2": 0,
            "tier3": 0,
        }
        
        self._cancelled = False
        
        logger.info(f"Organizer initialized: {export_path} -> {output_path}")
    
    def cancel(self):
        """Cancel the organization process."""
        self._cancelled = True
        logger.info("Organization cancelled by user")
    
    def organize(self) -> bool:
        """Run the organization process.
        
        Returns:
            bool: True if successful, False if cancelled or error
        """
        try:
            # Step 1: Load chat history
            self._report_progress(0, 100, "Loading chat history...")
            if not self._load_chat_history():
                return False
            
            # Step 2: Detect media directories
            self._report_progress(10, 100, "Detecting media directories...")
            media_dirs = self._detect_media_directories()
            if not media_dirs:
                logger.error("No media directories found")
                return False
            
            logger.info(f"Found {len(media_dirs)} media directories")
            
            # Step 3: Count total files
            self._report_progress(15, 100, "Counting media files...")
            all_files = []
            for media_dir in media_dirs:
                files = list(Path(media_dir).glob("*"))
                all_files.extend([f for f in files if f.is_file()])
            
            self.stats["total"] = len(all_files)
            logger.info(f"Found {self.stats['total']} total media files")
            
            # Step 4: Process files
            self._report_progress(20, 100, f"Processing {self.stats['total']} files...")
            if not self._process_files(all_files):
                return False
            
            # Step 5: Write debug report
            if self.create_debug_report and self.debug_report:
                self._report_progress(95, 100, "Writing matching report...")
                self._write_debug_report()
            
            self._report_progress(100, 100, "Organization complete!")
            logger.info(f"Organization complete: {self.stats['organized']}/{self.stats['total']} organized")
            return True
            
        except Exception as e:
            logger.error(f"Organization failed: {e}", exc_info=True)
            return False
    
    def _load_chat_history(self) -> bool:
        """Load and parse chat_history.json.
        
        Returns:
            bool: True if successful
        """
        chat_json = self.export_path / "chat_history" / "json" / "chat_history.json"
        
        if not chat_json.exists():
            logger.error(f"Chat history not found: {chat_json}")
            return False
        
        try:
            with open(chat_json, "r", encoding="utf-8") as f:
                chats = json.load(f)
            
            # Build media mapping
            logged_sample = False
            for contact_username, messages in chats.items():
                for msg in messages:
                    media_type = msg.get("Media Type")
                    # Check for various media types (sometimes labeled differently in older exports)
                    if media_type in ["MEDIA", "VIDEO", "IMAGE", "AUDIO"] or (media_type and "MEDIA" in media_type):
                        ts = self._parse_timestamp(msg.get("Created", ""))
                        if ts:
                            media_id = msg.get("Media IDs", "")
                            media_id_hint = self._extract_media_id_hint(media_id)
                            ts_micro = msg.get("Created(microseconds)", 0)
                            
                            # Log first Media ID for debugging (only once)
                            if not logged_sample and media_id:
                                logger.debug(f"Sample Media ID from JSON: {media_id[:100]}")
                                logger.debug(f"Extracted hint: {media_id_hint}")
                                logged_sample = True
                            
                            self.media_map[ts_micro] = {
                                "contact": contact_username,
                                "datetime": ts,
                                "media_id": media_id,
                                "media_id_hint": media_id_hint,
                                "is_sender": msg.get("IsSender", False),
                                "is_saved": msg.get("IsSaved", False),
                            }
            
            logger.info(f"Loaded {len(self.media_map)} media messages from {len(chats)} contacts")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load chat history: {e}")
            return False
    
    def _detect_media_directories(self) -> List[Path]:
        """Detect chat_media directories in export folder.
        
        Returns:
            List of Path objects for media directories
        """
        media_dirs = sorted([
            d for d in self.export_path.glob("chat_media*")
            if d.is_dir()
        ])
        return media_dirs
    
    def _process_files(self, files: List[Path]) -> bool:
        """Process all media files.
        
        Args:
            files: List of file paths to process
            
        Returns:
            bool: True if not cancelled
        """
        unmatched_files = []
        
        for i, media_file in enumerate(files):
            if self._cancelled:
                return False
            
            # Update progress every 10 files or at key points
            if i % 10 == 0 or i == len(files) - 1:
                progress = 20 + int((i / len(files)) * 75)
                self._report_progress(
                    progress,
                    100,
                    f"Processing {i+1}/{len(files)}: {media_file.name[:40]}..."
                )
            
            matched = self._match_and_copy_file(media_file)
            
            if matched:
                self.stats["organized"] += 1
            else:
                unmatched_files.append(media_file)
                self.stats["unmatched"] += 1
        
        # Move unmatched files
        if unmatched_files:
            self._report_progress(95, 100, f"Moving {len(unmatched_files)} unmatched files...")
            self._move_unmatched_files(unmatched_files)
        
        return True
    
    def _match_and_copy_file(self, media_file: Path) -> bool:
        """Match a file to a contact and copy it.
        
        Args:
            media_file: Path to media file
            
        Returns:
            bool: True if matched and copied
        """
        filename = media_file.name
        best_match = None
        match_reason = None
        match_tier = None
        
        # Extract date from filename
        date_match = re.match(r"(\d{4})-(\d{2})-(\d{2})", filename)
        if not date_match:
            return False
        
        file_date = datetime(
            int(date_match.group(1)),
            int(date_match.group(2)),
            int(date_match.group(3)),
        )
        
        # Find candidates from same day and adjacent days (to handle timezone diffs)
        target_dates = {
            file_date.date(),
            (file_date - timedelta(days=1)).date(),
            (file_date + timedelta(days=1)).date()
        }
        
        candidates = [
            (ts_micro, info)
            for ts_micro, info in self.media_map.items()
            if info["datetime"].date() in target_dates
        ]
        
        if not candidates:
            return False
        
        # Tier 1: Media ID matching
        if self.enable_tier1:
            for ts_micro, info in candidates:
                if info["media_id_hint"]:
                    # Try matching both with and without b~ prefix
                    if (info["media_id_hint"] in filename or 
                        f"b~{info['media_id_hint']}" in filename):
                        best_match = (ts_micro, info)
                        match_reason = f"Tier 1: Media ID match (hint: {info['media_id_hint'][:30]}...)"
                        match_tier = "tier1"
                        break
        
        # Tier 2: Single contact on date
        unique_contacts = {info["contact"] for _, info in candidates}
        if not best_match and self.enable_tier2 and len(unique_contacts) == 1:
            # All media on this date belongs to one contact
            contact_name = list(unique_contacts)[0]
            
            if len(candidates) > 1:
                # Find closest timestamp to use as metadata source
                file_mtime_utc = datetime.fromtimestamp(
                    media_file.stat().st_mtime, 
                    tz=timezone.utc
                )
                closest = min(
                    candidates,
                    key=lambda x: abs((x[1]["datetime"] - file_mtime_utc).total_seconds())
                )
                best_match = closest
                diff = abs((closest[1]["datetime"] - file_mtime_utc).total_seconds())
                match_reason = f"Tier 2: Single contact active ({contact_name}), offset {diff:.0f}s"
            else:
                best_match = candidates[0]
                match_reason = f"Tier 2: Single contact active ({contact_name})"
            
            match_tier = "tier2"
        
        # Tier 3: Timestamp proximity
        if not best_match and self.enable_tier3 and len(candidates) > 1:
            # Convert file mtime to UTC for proper comparison with JSON timestamps
            file_mtime_utc = datetime.fromtimestamp(
                media_file.stat().st_mtime, 
                tz=timezone.utc
            )
            closest = min(
                candidates,
                key=lambda x: abs((x[1]["datetime"] - file_mtime_utc).total_seconds())
            )
            time_diff = abs((closest[1]["datetime"] - file_mtime_utc).total_seconds())
            
            if time_diff <= self.timestamp_threshold:
                best_match = closest
                match_reason = f"Tier 3: Timestamp match ({time_diff:.0f}s diff, {len(candidates)} contacts)"
                match_tier = "tier3"
            else:
                match_reason = f"REJECTED: {len(candidates)} contacts on {file_date.date()}, closest {time_diff:.0f}s away"
        
        # Copy file if matched
        if best_match:
            _, info = best_match
            self._copy_to_contact(media_file, info)
            
            if match_tier:
                self.stats[match_tier] += 1
            
            if self.create_debug_report:
                self.debug_report.append({
                    "file": filename,
                    "contact": info["contact"],
                    "date": info["datetime"].strftime("%Y-%m-%d %H:%M:%S"),
                    "reason": match_reason,
                    "candidates": len(candidates),
                })
            
            return True
        
        # Log unmatched if debug enabled
        if self.create_debug_report and match_reason:
            self.debug_report.append({
                "file": filename,
                "contact": "UNMATCHED",
                "date": file_date.strftime("%Y-%m-%d"),
                "reason": match_reason,
                "candidates": len(candidates),
            })
        
        return False
    
    def _copy_to_contact(self, media_file: Path, info: Dict):
        """Copy file to contact's organized folder.
        
        Args:
            media_file: Source file path
            info: Contact information dict
        """
        contact_name = self._sanitize_filename(info["contact"])
        dt = info["datetime"]
        
        # Create directory structure
        if self.organize_by_year:
            target_dir = self.output_path / contact_name / str(dt.year)
        else:
            target_dir = self.output_path / contact_name
        
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Determine extension
        ext = media_file.suffix
        if not ext or ext == ".unknown":
            ext = self._guess_extension(media_file.name)
        
        # Create filename
        direction = "sent" if info["is_sender"] else "received"
        saved = "_saved" if info["is_saved"] else ""
        new_name = f"{dt.strftime('%Y-%m-%d_%H%M%S')}_{direction}{saved}{ext}"
        
        # Handle duplicates
        counter = 1
        target_path = target_dir / new_name
        while target_path.exists():
            new_name = f"{dt.strftime('%Y-%m-%d_%H%M%S')}_{direction}{saved}_{counter}{ext}"
            target_path = target_dir / new_name
            counter += 1
        
        # Copy file
        try:
            shutil.copy2(media_file, target_path)
            logger.debug(f"Copied: {media_file.name} -> {contact_name}/{dt.year}/{new_name}")
        except Exception as e:
            logger.error(f"Failed to copy {media_file.name}: {e}")
    
    def _move_unmatched_files(self, files: List[Path]):
        """Move unmatched files to _Unmatched folder.
        
        Args:
            files: List of unmatched file paths
        """
        for media_file in files:
            try:
                # Extract year from filename
                date_match = re.match(r"(\d{4})-\d{2}-\d{2}", media_file.name)
                if date_match:
                    year = date_match.group(1)
                    unmatched_dir = self.output_path / "_Unmatched" / year
                else:
                    unmatched_dir = self.output_path / "_Unmatched" / "Unknown"
                
                unmatched_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(media_file, unmatched_dir / media_file.name)
                logger.debug(f"Moved to unmatched: {media_file.name}")
            except Exception as e:
                logger.error(f"Failed to move {media_file.name}: {e}")
    
    def _write_debug_report(self):
        """Write detailed matching report to file."""
        report_path = self.output_path / "matching_report.txt"
        
        try:
            with open(report_path, "w", encoding="utf-8") as f:
                f.write("MEDIA FILE MATCHING REPORT\n")
                f.write("=" * 80 + "\n\n")
                f.write("Configuration:\n")
                f.write(f"  Timestamp threshold: {self.timestamp_threshold}s\n")
                f.write(f"  Tier 1 (Media ID): {'Enabled' if self.enable_tier1 else 'Disabled'}\n")
                f.write(f"  Tier 2 (Single Contact): {'Enabled' if self.enable_tier2 else 'Disabled'}\n")
                f.write(f"  Tier 3 (Timestamp): {'Enabled' if self.enable_tier3 else 'Disabled'}\n\n")
                f.write("=" * 80 + "\n\n")
                
                for entry in self.debug_report:
                    f.write(f"File: {entry['file']}\n")
                    f.write(f"  Contact: {entry['contact']}\n")
                    f.write(f"  Date: {entry['date']}\n")
                    f.write(f"  Reason: {entry['reason']}\n")
                    f.write(f"  Candidates: {entry['candidates']}\n")
                    f.write("-" * 80 + "\n")
            
            logger.info(f"Debug report written to: {report_path}")
        except Exception as e:
            logger.error(f"Failed to write debug report: {e}")
    
    def _report_progress(self, current: int, total: int, status: str):
        """Report progress via callback.
        
        Args:
            current: Current progress value
            total: Total progress value
            status: Status message
        """
        if self.progress_callback:
            try:
                self.progress_callback(current, total, status)
            except Exception as e:
                logger.error(f"Progress callback error: {e}")
    
    @staticmethod
    def _parse_timestamp(ts_str: str) -> Optional[datetime]:
        """Convert Snapchat timestamp to datetime.
        
        Args:
            ts_str: Timestamp string (expected to be in UTC)
            
        Returns:
            datetime object with UTC timezone or None
        """
        try:
            dt = datetime.strptime(ts_str.replace(" UTC", ""), "%Y-%m-%d %H:%M:%S")
            # Mark as UTC for proper timezone comparison
            return dt.replace(tzinfo=timezone.utc)
        except Exception:
            return None
    
    @staticmethod
    def _extract_media_id_hint(media_id_str: str) -> Optional[str]:
        """Extract searchable hint from Media ID.
        
        Args:
            media_id_str: Media ID string
            
        Returns:
            Full hint string (not truncated) or None
        """
        if not media_id_str:
            return None
            
        # Check for b~ prefix format - return FULL string (not truncated)
        match = re.search(r"b~([A-Za-z0-9_-]+)", media_id_str)
        if match:
            return match.group(1)  # Return full base64 string
            
        # If no b~ prefix, return the whole ID (might be in JSON without prefix)
        if len(media_id_str) >= 20 and re.match(r"^[A-Za-z0-9_-]+$", media_id_str):
            return media_id_str
            
        return None
    
    @staticmethod
    def _sanitize_filename(name: str) -> str:
        """Remove unsafe characters from filename.
        
        Args:
            name: Filename to sanitize
            
        Returns:
            Sanitized filename
        """
        return re.sub(r'[<>:"/\\|?*]', "_", name)
    
    @staticmethod
    def _guess_extension(filename: str) -> str:
        """Guess file extension from filename hints.
        
        Args:
            filename: Filename to analyze
            
        Returns:
            Extension string with dot
        """
        if "media~" in filename or ".mp4" in filename or "b~" in filename:
            return ".mp4"
        elif "thumbnail~" in filename or ".jpg" in filename:
            return ".jpg"
        elif "overlay~" in filename:
            if ".webp" in filename:
                return ".webp"
            else:
                return ".png"
        return ".unknown"
