"""Application configuration and constants.

This module contains all application-wide configuration settings, feature flags,
and constants used throughout the Snapchat Organizer Desktop application.
"""

from pathlib import Path
from typing import Dict, Any

# Application metadata
APP_NAME = "Snapchat Organizer"
APP_VERSION = "1.0.0-alpha"
APP_AUTHOR = "Mohammed Haris"
APP_ORG = "SnapchatOrganizer"

# Application directories
APP_DIR = Path.home() / ".snapchat-organizer"
DB_PATH = APP_DIR / "organizer.db"
LOG_PATH = APP_DIR / "logs"
CACHE_PATH = APP_DIR / "cache"

# Ensure directories exist
APP_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH.mkdir(parents=True, exist_ok=True)
CACHE_PATH.mkdir(parents=True, exist_ok=True)

# Feature flags
ENABLE_OVERLAY_COMPOSITING = True
ENABLE_GPS_EMBEDDING = True
ENABLE_TIMEZONE_CONVERSION = True
ENABLE_AUTO_UPDATE = False  # Will be enabled in Phase 3

# Download settings
DEFAULT_DOWNLOAD_DELAY = 2.0  # seconds between requests
MIN_DOWNLOAD_DELAY = 0.5
MAX_DOWNLOAD_DELAY = 10.0
DEFAULT_TIMEOUT = 30  # seconds for HTTP requests
MAX_RETRIES = 3

# Organize settings
DEFAULT_TIMESTAMP_THRESHOLD = 300  # seconds (5 minutes)
MIN_TIMESTAMP_THRESHOLD = 60
MAX_TIMESTAMP_THRESHOLD = 900

# License tiers
TIER_FREE = "free"
TIER_PRO = "pro"
TIER_PREMIUM = "premium"

# Feature access control by tier
FEATURE_ACCESS: Dict[str, Dict[str, Any]] = {
    TIER_FREE: {
        'max_files_per_month': 100,
        'download_memories': False,
        'organize_chat_media': True,
        'overlay_compositing': False,
        'gps_embedding': False,
        'timezone_conversion': False,
        'remove_duplicates': False,
        'verify_downloads': False,
        'organize_by_year': True,
        'fix_timestamps': True,
        'advanced_analytics': False,
        'cloud_backup': False,
    },
    TIER_PRO: {
        'max_files_per_month': -1,  # unlimited
        'download_memories': True,
        'organize_chat_media': True,
        'overlay_compositing': True,
        'gps_embedding': True,
        'timezone_conversion': True,
        'remove_duplicates': True,
        'verify_downloads': True,
        'organize_by_year': True,
        'fix_timestamps': True,
        'advanced_analytics': False,
        'cloud_backup': False,
    },
    TIER_PREMIUM: {
        'max_files_per_month': -1,
        'download_memories': True,
        'organize_chat_media': True,
        'overlay_compositing': True,
        'gps_embedding': True,
        'timezone_conversion': True,
        'remove_duplicates': True,
        'verify_downloads': True,
        'organize_by_year': True,
        'fix_timestamps': True,
        'advanced_analytics': True,
        'cloud_backup': True,
    }
}

# Trial settings
TRIAL_DURATION_DAYS = 7
TRIAL_TIER = TIER_PRO  # Full features during trial

# UI settings
WINDOW_MIN_WIDTH = 800
WINDOW_MIN_HEIGHT = 600
WINDOW_DEFAULT_WIDTH = 1000
WINDOW_DEFAULT_HEIGHT = 700

# Progress update interval (milliseconds)
PROGRESS_UPDATE_INTERVAL = 100

# File types
IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp', '.gif', '.heic']
VIDEO_EXTENSIONS = ['.mp4', '.mov', '.avi', '.mkv', '.webm']
OVERLAY_EXTENSIONS = ['.png', '.webp']

# External tool paths (will be detected at runtime)
FFMPEG_PATH = None  # Auto-detect or bundled
EXIFTOOL_PATH = None  # Auto-detect or bundled

# Logging configuration
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10 MB
LOG_BACKUP_COUNT = 5

# Database configuration
DB_ECHO = False  # Set to True for SQL query logging


def get_feature_access(tier: str, feature: str) -> Any:
    """Get feature access for a specific tier.
    
    Args:
        tier: License tier (free, pro, premium)
        feature: Feature name to check
        
    Returns:
        Feature value (bool, int, or other type)
        
    Raises:
        KeyError: If tier or feature doesn't exist
    """
    if tier not in FEATURE_ACCESS:
        raise KeyError(f"Unknown tier: {tier}")
    
    if feature not in FEATURE_ACCESS[tier]:
        raise KeyError(f"Unknown feature: {feature}")
    
    return FEATURE_ACCESS[tier][feature]


def can_access_feature(tier: str, feature: str) -> bool:
    """Check if a tier has access to a feature.
    
    Args:
        tier: License tier (free, pro, premium)
        feature: Feature name to check
        
    Returns:
        True if feature is accessible, False otherwise
    """
    try:
        value = get_feature_access(tier, feature)
        # For boolean features, return directly
        if isinstance(value, bool):
            return value
        # For numeric features, return True if not 0
        if isinstance(value, (int, float)):
            return value != 0
        # For other types, return True if not None
        return value is not None
    except KeyError:
        return False
