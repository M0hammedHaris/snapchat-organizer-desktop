"""Chat media organizer core logic.

This module provides the OrganizerCore class that handles organizing Snapchat
chat media files by contact using a probabilistic scoring-based matching strategy.
"""

import json
import shutil
import re
import hashlib
import math
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Callable, Tuple
from collections import defaultdict

from ..utils.logger import get_logger

logger = get_logger(__name__)


class OrganizerCore:
    """Core logic for organizing Snapchat chat media by contact.
    
    Uses a probabilistic scoring-based matching strategy with:
    - Media ID normalization and fuzzy matching
    - Time-based clustering for multi-file sends
    - Composite scoring (media ID, timestamp, date, contact frequency)
    - Enhanced logging and backwards compatibility
    """
    
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
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ):
        """Initialize the organizer.
        
        Args:
            export_path: Path to Snapchat export folder
            output_path: Path to output folder for organized media
            timestamp_threshold: Time window for Gaussian decay scoring (default: 2 hours)
            match_score_threshold: Minimum composite score for match (default: 0.45)
            enable_tier1: Enable Media ID matching (kept for backwards compatibility)
            enable_tier2: Enable single contact matching (kept for backwards compatibility)
            enable_tier3: Enable timestamp proximity matching (kept for backwards compatibility)
            organize_by_year: Create year subdirectories
            create_debug_report: Generate detailed matching report
            preserve_originals: Create .snapchat_original sidecar files
            progress_callback: Callback for progress updates (current, total, status)
        """
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
        self.progress_callback = progress_callback
        
        # Processing state
        self.media_map: Dict = {}
        self.contact_freq_map: Dict[str, List[datetime]] = defaultdict(list)
        self.debug_report: List[Dict] = []
        self.stats = {
            "total": 0,
            "organized": 0,
            "unmatched": 0,
            "low_confidence": 0,  # Matches with score < 0.8
            "exact_media_id": 0,
            "fuzzy_media_id": 0,
            "time_based": 0,
        }
        
        self._cancelled = False
        
        logger.info(f"Organizer initialized: {export_path} -> {output_path}")
        logger.info(f"Score threshold: {match_score_threshold}, Time window: {timestamp_threshold}s")
    
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
            
            # Build media mapping and contact frequency map
            logged_sample = False
            for contact_username, messages in chats.items():
                for msg in messages:
                    media_type = msg.get("Media Type")
                    # Check for various media types (sometimes labeled differently in older exports)
                    if media_type in ["MEDIA", "VIDEO", "IMAGE", "AUDIO"] or (media_type and "MEDIA" in media_type):
                        ts = self._parse_timestamp(msg.get("Created", ""))
                        if ts:
                            media_id = msg.get("Media IDs", "")
                            media_id_normalized = self._normalize_media_id(media_id)
                            ts_micro = msg.get("Created(microseconds)", 0)
                            
                            # Log first Media ID for debugging (only once)
                            if not logged_sample and media_id:
                                logger.debug(f"Sample Media ID from JSON: {media_id[:100]}")
                                logger.debug(f"Normalized: {media_id_normalized}")
                                logged_sample = True
                            
                            self.media_map[ts_micro] = {
                                "contact": contact_username,
                                "datetime": ts,
                                "media_id": media_id,
                                "media_id_normalized": media_id_normalized,
                                "is_sender": msg.get("IsSender", False),
                                "is_saved": msg.get("IsSaved", False),
                            }
                            
                            # Build contact frequency map
                            self.contact_freq_map[contact_username].append(ts)
            
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
        """Match a file to a contact using composite scoring.
        
        Args:
            media_file: Path to media file
            
        Returns:
            bool: True if matched and copied
        """
        filename = media_file.name
        
        # Extract date from filename
        date_match = re.match(r"(\d{4})-(\d{2})-(\d{2})", filename)
        if not date_match:
            return False
        
        file_date = datetime(
            int(date_match.group(1)),
            int(date_match.group(2)),
            int(date_match.group(3)),
        )
        
        # Extract media ID from filename if present
        file_media_id = self._extract_media_id_from_filename(filename)
        
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
        
        # Get file timestamp for scoring
        file_mtime_utc = datetime.fromtimestamp(
            media_file.stat().st_mtime, 
            tz=timezone.utc
        )
        
        # Score all candidates
        scored_candidates = []
        for ts_micro, info in candidates:
            score, breakdown = self._compute_match_score(
                file_media_id=file_media_id,
                file_datetime=file_mtime_utc,
                file_date=file_date,
                candidate_info=info,
                all_candidates=candidates,
            )
            
            # Apply tier filters for backwards compatibility
            # Skip if disabled and this would be the primary matching strategy
            if breakdown["media_id_score"] > 0 and not self.enable_tier1:
                continue  # Skip media ID matches if tier 1 disabled
            
            # Tier 2: Single contact matching
            unique_contacts = {c_info["contact"] for _, c_info in candidates}
            if (breakdown["media_id_score"] == 0 and 
                len(unique_contacts) == 1 and 
                not self.enable_tier2):
                continue  # Skip single-contact matches if tier 2 disabled
            
            # Tier 3: Timestamp-only matching
            if (breakdown["media_id_score"] == 0 and 
                len(unique_contacts) > 1 and 
                not self.enable_tier3):
                continue  # Skip multi-contact timestamp matches if tier 3 disabled
            
            if score >= self.match_score_threshold:
                scored_candidates.append((score, ts_micro, info, breakdown))
        
        if not scored_candidates:
            # Log best rejected candidate for debugging
            if self.create_debug_report and candidates:
                best_rejected = max(
                    candidates,
                    key=lambda x: self._compute_match_score(
                        file_media_id, file_mtime_utc, file_date, x[1], candidates
                    )[0]
                )
                _, best_info = best_rejected
                rejected_score, rejected_breakdown = self._compute_match_score(
                    file_media_id, file_mtime_utc, file_date, best_info, candidates
                )
                
                self.debug_report.append({
                    "file": filename,
                    "contact": "REJECTED",
                    "date": file_date.strftime("%Y-%m-%d"),
                    "score": f"{rejected_score:.3f}",
                    "threshold": f"{self.match_score_threshold:.3f}",
                    "breakdown": rejected_breakdown,
                    "reason": f"Best score {rejected_score:.3f} below threshold {self.match_score_threshold:.3f}",
                    "candidates": len(candidates),
                })
            return False
        
        # Select best match (highest score)
        best_score, best_ts_micro, best_info, best_breakdown = max(scored_candidates, key=lambda x: x[0])
        
        # Copy file with enhanced naming
        self._copy_to_contact_enhanced(media_file, best_info, best_score)
        
        # Update statistics
        self.stats["organized"] += 1
        if best_score < 0.8:
            self.stats["low_confidence"] += 1
        
        if best_breakdown["media_id_score"] == 1.0:
            self.stats["exact_media_id"] += 1
        elif best_breakdown["media_id_score"] > 0.0:
            self.stats["fuzzy_media_id"] += 1
        else:
            self.stats["time_based"] += 1
        
        # Detailed logging
        if self.create_debug_report:
            confidence = "HIGH" if best_score >= 0.8 else "LOW"
            self.debug_report.append({
                "file": filename,
                "contact": best_info["contact"],
                "date": best_info["datetime"].strftime("%Y-%m-%d %H:%M:%S"),
                "score": f"{best_score:.3f}",
                "confidence": confidence,
                "breakdown": best_breakdown,
                "reason": self._format_match_reason(best_breakdown),
                "candidates": len(candidates),
                "rejected_count": len(candidates) - len(scored_candidates),
            })
        
        return True
    
    def _copy_to_contact(self, media_file: Path, info: Dict):
        """Copy file to contact's organized folder (legacy method for backwards compatibility).
        
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
    
    def _copy_to_contact_enhanced(self, media_file: Path, info: Dict, match_score: float):
        """Copy file to contact's organized folder with enhanced naming and sidecar.
        
        New naming format: YYYYMMDD_HHMMSS_contactHash6_mediaHash8.ext
        
        Args:
            media_file: Source file path
            info: Contact information dict
            match_score: Match confidence score
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
        
        # Generate hash components
        contact_hash = hashlib.md5(contact_name.encode()).hexdigest()[:6]
        
        # Use media ID from JSON if available, otherwise hash filename
        media_id = info.get("media_id_normalized", media_file.name)
        media_hash = hashlib.md5(media_id.encode()).hexdigest()[:8]
        
        # Create new filename
        new_name = f"{dt.strftime('%Y%m%d_%H%M%S')}_{contact_hash}_{media_hash}{ext}"
        
        # Handle duplicates
        counter = 1
        target_path = target_dir / new_name
        while target_path.exists():
            new_name = f"{dt.strftime('%Y%m%d_%H%M%S')}_{contact_hash}_{media_hash}_{counter}{ext}"
            target_path = target_dir / new_name
            counter += 1
        
        # Copy file
        try:
            shutil.copy2(media_file, target_path)
            logger.debug(f"Copied: {media_file.name} -> {contact_name}/{dt.year}/{new_name} (score: {match_score:.3f})")
            
            # Create sidecar file with original metadata
            if self.preserve_originals:
                sidecar_path = target_path.with_suffix(target_path.suffix + ".snapchat_original")
                with open(sidecar_path, "w", encoding="utf-8") as f:
                    f.write(f"Original filename: {media_file.name}\n")
                    f.write(f"Match score: {match_score:.3f}\n")
                    f.write(f"Contact: {info['contact']}\n")
                    f.write(f"Timestamp: {dt.strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
                    f.write(f"Is sender: {info['is_sender']}\n")
                    f.write(f"Is saved: {info['is_saved']}\n")
                    if info.get("media_id"):
                        f.write(f"Media ID: {info['media_id'][:100]}\n")
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
        """Write detailed matching report to file with enhanced scoring information."""
        report_path = self.output_path / "matching_report.txt"
        
        try:
            with open(report_path, "w", encoding="utf-8") as f:
                f.write("MEDIA FILE MATCHING REPORT (Scoring-Based Strategy)\n")
                f.write("=" * 100 + "\n\n")
                f.write("Configuration:\n")
                f.write(f"  Score threshold: {self.match_score_threshold}\n")
                f.write(f"  Time window: {self.timestamp_threshold}s ({self.timestamp_threshold/3600:.1f} hours)\n")
                f.write(f"  Preserve originals: {'Yes' if self.preserve_originals else 'No'}\n")
                f.write(f"  Organize by year: {'Yes' if self.organize_by_year else 'No'}\n\n")
                
                f.write("Statistics:\n")
                f.write(f"  Total files: {self.stats['total']}\n")
                f.write(f"  Organized: {self.stats['organized']} ({self.stats['organized']/max(self.stats['total'],1)*100:.1f}%)\n")
                f.write(f"  Unmatched: {self.stats['unmatched']} ({self.stats['unmatched']/max(self.stats['total'],1)*100:.1f}%)\n")
                f.write(f"  Low confidence: {self.stats['low_confidence']} (score < 0.8)\n\n")
                
                f.write("Match Type Breakdown:\n")
                f.write(f"  Exact Media ID: {self.stats['exact_media_id']}\n")
                f.write(f"  Fuzzy Media ID: {self.stats['fuzzy_media_id']}\n")
                f.write(f"  Time-based: {self.stats['time_based']}\n\n")
                f.write("=" * 100 + "\n\n")
                
                # Group by matched/rejected/low confidence
                matched = [e for e in self.debug_report if e.get("contact") not in ["REJECTED", "UNMATCHED"]]
                rejected = [e for e in self.debug_report if e.get("contact") in ["REJECTED", "UNMATCHED"]]
                low_conf = [e for e in matched if e.get("confidence") == "LOW"]
                
                # Write low confidence matches first
                if low_conf:
                    f.write(f"\n⚠️  LOW CONFIDENCE MATCHES ({len(low_conf)}) - Review Recommended\n")
                    f.write("=" * 100 + "\n\n")
                    for entry in low_conf:
                        self._write_report_entry(f, entry)
                
                # Write successful matches
                f.write(f"\n✓ SUCCESSFUL MATCHES ({len(matched)})\n")
                f.write("=" * 100 + "\n\n")
                for entry in matched:
                    self._write_report_entry(f, entry)
                
                # Write rejected candidates
                if rejected:
                    f.write(f"\n✗ REJECTED/UNMATCHED ({len(rejected)})\n")
                    f.write("=" * 100 + "\n\n")
                    for entry in rejected:
                        self._write_report_entry(f, entry)
            
            logger.info(f"Debug report written to: {report_path}")
        except Exception as e:
            logger.error(f"Failed to write debug report: {e}")
    
    def _write_report_entry(self, f, entry: Dict):
        """Write a single report entry with formatting.
        
        Args:
            f: File handle
            entry: Report entry dictionary
        """
        f.write(f"File: {entry['file']}\n")
        f.write(f"  Contact: {entry['contact']}\n")
        f.write(f"  Date: {entry['date']}\n")
        
        if "score" in entry:
            f.write(f"  Score: {entry['score']}")
            if "confidence" in entry:
                f.write(f" ({entry['confidence']} CONFIDENCE)")
            f.write("\n")
        
        if "breakdown" in entry:
            bd = entry["breakdown"]
            f.write("  Score Breakdown:\n")
            f.write(f"    • Media ID: {bd.get('media_id_score', 0):.3f} (weight: 0.5)\n")
            f.write(f"    • Time diff: {bd.get('time_diff_score', 0):.3f} (weight: 0.3)\n")
            f.write(f"    • Same day: {bd.get('same_day_score', 0):.3f} (weight: 0.1)\n")
            f.write(f"    • Contact freq: {bd.get('contact_freq_score', 0):.3f} (weight: 0.1)\n")
        
        if "reason" in entry:
            f.write(f"  Reason: {entry['reason']}\n")
        
        if "candidates" in entry:
            f.write(f"  Candidates: {entry['candidates']}")
            if "rejected_count" in entry:
                f.write(f" ({entry['rejected_count']} rejected)")
            f.write("\n")
        
        f.write("-" * 100 + "\n")
    
    def _normalize_media_id(self, media_id_str: str) -> str:
        """Normalize media ID for fuzzy matching.
        
        Handles b_ prefix variations and extracts base64 content.
        
        Args:
            media_id_str: Raw media ID string from JSON
            
        Returns:
            Normalized media ID string
        """
        if not media_id_str:
            return ""
        
        # Try to extract base64 part (with or without b~ or b_ prefix)
        # Pattern: b~base64 or b_base64 or just base64
        match = re.search(r"b[~_]([A-Za-z0-9_-]+)", media_id_str)
        if match:
            return match.group(1).lower()  # Lowercase for case-insensitive matching
        
        # If no prefix found but string looks like a valid base64 ID, return cleaned version
        if len(media_id_str) >= 20 and re.match(r"^[A-Za-z0-9_-]+$", media_id_str):
            return media_id_str.lower()
        
        return ""
    
    def _extract_media_id_from_filename(self, filename: str) -> str:
        """Extract normalized media ID from filename.
        
        Args:
            filename: Media file name
            
        Returns:
            Normalized media ID or empty string
        """
        # Pattern: YYYY-MM-DD_b_base64... or YYYY-MM-DD_b~base64...
        match = re.search(r"\d{4}-\d{2}-\d{2}_b[~_]([A-Za-z0-9_-]+)", filename)
        if match:
            return match.group(1).lower()
        
        return ""
    
    def _compute_match_score(
        self,
        file_media_id: str,
        file_datetime: datetime,
        file_date: datetime,
        candidate_info: Dict,
        all_candidates: List[Tuple],
    ) -> Tuple[float, Dict]:
        """Compute composite match score for a file-candidate pair.
        
        Scoring weights:
        - Media ID: 0.5 (exact=1.0, fuzzy=0.7, none=0.0)
        - Time diff: 0.3 (Gaussian decay over time window)
        - Same day: 0.1 (1.0 same, 0.5 adjacent)
        - Contact freq: 0.1 (0-1 based on activity near timestamp)
        
        Args:
            file_media_id: Normalized media ID from filename
            file_datetime: File modification timestamp (UTC)
            file_date: File date from filename
            candidate_info: Candidate metadata from JSON
            all_candidates: All candidates for this file
            
        Returns:
            Tuple of (total_score, breakdown_dict)
        """
        # 1. Media ID score
        media_id_score = 0.0
        candidate_media_id = candidate_info.get("media_id_normalized", "")
        
        if file_media_id and candidate_media_id:
            if file_media_id == candidate_media_id:
                # Exact match
                media_id_score = 1.0
            elif (file_media_id in candidate_media_id or 
                  candidate_media_id in file_media_id):
                # Fuzzy match (prefix/suffix match)
                overlap = len(set(file_media_id) & set(candidate_media_id))
                max_len = max(len(file_media_id), len(candidate_media_id))
                media_id_score = 0.7 * (overlap / max_len) if max_len > 0 else 0.7
        
        # 2. Time difference score (Gaussian decay)
        time_diff_seconds = abs((candidate_info["datetime"] - file_datetime).total_seconds())
        time_diff_score = math.exp(-time_diff_seconds / self.timestamp_threshold)
        
        # 3. Same day score
        same_day_score = 1.0 if candidate_info["datetime"].date() == file_date.date() else 0.5
        
        # 4. Contact frequency score
        contact_freq_score = self._compute_contact_frequency_score(
            candidate_info["contact"],
            file_datetime,
        )
        
        # Weighted sum with dynamic adjustment
        # If no media ID match, boost time/frequency weights for better time-based matching
        if media_id_score == 0.0:
            # No media ID: rely more on time proximity
            total_score = (
                0.0 * media_id_score +
                0.5 * time_diff_score +      # Boost from 0.3 to 0.5
                0.2 * same_day_score +       # Boost from 0.1 to 0.2
                0.3 * contact_freq_score     # Boost from 0.1 to 0.3
            )
        else:
            # Has media ID: use original weights
            total_score = (
                0.5 * media_id_score +
                0.3 * time_diff_score +
                0.1 * same_day_score +
                0.1 * contact_freq_score
            )
        
        breakdown = {
            "media_id_score": media_id_score,
            "time_diff_score": time_diff_score,
            "time_diff_seconds": int(time_diff_seconds),
            "same_day_score": same_day_score,
            "contact_freq_score": contact_freq_score,
        }
        
        return total_score, breakdown
    
    def _compute_contact_frequency_score(self, contact: str, timestamp: datetime) -> float:
        """Compute contact activity frequency score near timestamp.
        
        Args:
            contact: Contact username
            timestamp: File timestamp
            
        Returns:
            Score 0-1 based on contact's media activity
        """
        if contact not in self.contact_freq_map:
            return 0.0
        
        # Count messages within ±1 day
        window_start = timestamp - timedelta(days=1)
        window_end = timestamp + timedelta(days=1)
        
        nearby_count = sum(
            1 for ts in self.contact_freq_map[contact]
            if window_start <= ts <= window_end
        )
        
        # Normalize by total candidates in window (max 10 for scaling)
        return min(nearby_count / 10.0, 1.0)
    
    def _format_match_reason(self, breakdown: Dict) -> str:
        """Format human-readable match reason from score breakdown.
        
        Args:
            breakdown: Score breakdown dictionary
            
        Returns:
            Formatted reason string
        """
        parts = []
        
        if breakdown["media_id_score"] == 1.0:
            parts.append("Exact Media ID")
        elif breakdown["media_id_score"] > 0.0:
            parts.append(f"Fuzzy Media ID ({breakdown['media_id_score']:.2f})")
        
        if breakdown["time_diff_seconds"] < 300:
            parts.append(f"Close timestamp ({breakdown['time_diff_seconds']}s)")
        elif breakdown["time_diff_score"] > 0.5:
            parts.append(f"Moderate timestamp ({breakdown['time_diff_seconds']}s)")
        
        if breakdown["same_day_score"] == 1.0:
            parts.append("Same day")
        
        if breakdown["contact_freq_score"] > 0.5:
            parts.append("High contact activity")
        
        return " + ".join(parts) if parts else "Time-based matching"
    
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
