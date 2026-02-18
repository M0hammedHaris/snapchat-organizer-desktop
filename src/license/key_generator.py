"""License key generation and validation.

This module provides functions for generating and validating license keys
with built-in checksums for offline verification.
"""

import hashlib
import secrets
import string
import re
from typing import Optional, Tuple

from ..utils.logger import get_logger

logger = get_logger(__name__)

# License key format: XXXX-XXXX-XXXX-XXXX-XXXX (25 chars + 4 dashes)
KEY_LENGTH = 25
KEY_SEGMENT_LENGTH = 5
KEY_SEGMENTS = 5
KEY_CHARS = string.ascii_uppercase + string.digits
KEY_PATTERN = re.compile(r'^[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}$')

# Secret salt for checksum generation (in production, this would be more secure)
_SECRET_SALT = "snapchat-organizer-2026"


def _calculate_checksum(key_body: str) -> str:
    """Calculate a 2-character checksum for the key body.
    
    Args:
        key_body: The key without the checksum portion
        
    Returns:
        2-character checksum string
    """
    data = f"{key_body}{_SECRET_SALT}"
    hash_bytes = hashlib.sha256(data.encode('utf-8')).digest()
    # Convert first 2 bytes to base36 characters
    checksum = ''
    for byte in hash_bytes[:2]:
        checksum += KEY_CHARS[byte % len(KEY_CHARS)]
    return checksum


def generate_license_key(tier: str = "pro", prefix: Optional[str] = None) -> str:
    """Generate a new license key.
    
    The key format is: PPPP-XXXX-XXXX-XXXX-XXCC
    Where:
    - PPPP: Prefix (tier identifier or custom prefix)
    - XXXX-XXXX-XXXX: Random segments
    - CC: Checksum (last 2 chars of last segment)
    
    Args:
        tier: License tier (free, pro, premium)
        prefix: Optional custom prefix (4 chars)
        
    Returns:
        Formatted license key string (e.g., "PRO2-ABCD-EFGH-IJKL-MN12")
    """
    # Determine prefix based on tier or custom
    if prefix:
        key_prefix = prefix[:4].upper().ljust(4, '0')
    else:
        tier_prefixes = {
            'free': 'FREE',
            'pro': 'PRO2',
            'premium': 'PREM',
        }
        key_prefix = tier_prefixes.get(tier, 'UNKN')
    
    # Generate random segments (3 segments of 5 chars each)
    random_segments = []
    for _ in range(3):
        segment = ''.join(secrets.choice(KEY_CHARS) for _ in range(KEY_SEGMENT_LENGTH))
        random_segments.append(segment)
    
    # Generate last segment (3 random + 2 checksum)
    last_segment_body = ''.join(secrets.choice(KEY_CHARS) for _ in range(3))
    
    # Calculate checksum based on all previous segments
    key_body = f"{key_prefix}{''.join(random_segments)}{last_segment_body}"
    checksum = _calculate_checksum(key_body)
    last_segment = last_segment_body + checksum
    
    # Combine all segments
    all_segments = [key_prefix] + random_segments + [last_segment]
    license_key = '-'.join(all_segments)
    
    logger.debug(f"Generated license key: {license_key[:8]}...")
    return license_key


def validate_license_key_format(key: str) -> bool:
    """Validate the format of a license key.
    
    Args:
        key: License key to validate
        
    Returns:
        True if the format is valid, False otherwise
    """
    if not key:
        return False
    
    # Normalize key (remove spaces, uppercase)
    normalized = key.strip().upper().replace(' ', '-')
    
    # Check pattern
    return bool(KEY_PATTERN.match(normalized))


def validate_license_key_checksum(key: str) -> bool:
    """Validate the checksum of a license key.
    
    Args:
        key: License key to validate
        
    Returns:
        True if the checksum is valid, False otherwise
    """
    if not validate_license_key_format(key):
        return False
    
    # Normalize and extract segments
    normalized = key.strip().upper().replace(' ', '-')
    segments = normalized.split('-')
    
    if len(segments) != KEY_SEGMENTS:
        return False
    
    # Extract key body and checksum
    last_segment = segments[-1]
    last_segment_body = last_segment[:3]
    provided_checksum = last_segment[3:]
    
    key_body = ''.join(s for s in segments[:-1]) + last_segment_body
    expected_checksum = _calculate_checksum(key_body)
    
    return provided_checksum == expected_checksum


def normalize_license_key(key: str) -> str:
    """Normalize a license key to standard format.
    
    Args:
        key: License key in any format
        
    Returns:
        Normalized key (uppercase with dashes)
    """
    # Remove all non-alphanumeric characters and uppercase
    chars = ''.join(c.upper() for c in key if c.isalnum())
    
    # Split into segments
    segments = [chars[i:i+KEY_SEGMENT_LENGTH] for i in range(0, len(chars), KEY_SEGMENT_LENGTH)]
    
    # Join with dashes
    return '-'.join(segments)


def extract_tier_from_key(key: str) -> Optional[str]:
    """Extract the tier from a license key prefix.
    
    Args:
        key: License key
        
    Returns:
        Tier string or None if invalid
    """
    if not validate_license_key_format(key):
        return None
    
    normalized = key.strip().upper().replace(' ', '-')
    prefix = normalized.split('-')[0]
    
    prefix_to_tier = {
        'FREE': 'free',
        'PRO2': 'pro',
        'PREM': 'premium',
    }
    
    return prefix_to_tier.get(prefix)


def parse_license_key(key: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """Parse and validate a license key.
    
    Args:
        key: License key to parse
        
    Returns:
        Tuple of (is_valid, tier, normalized_key)
    """
    if not key:
        return (False, None, None)
    
    normalized = normalize_license_key(key)
    
    if not validate_license_key_format(normalized):
        logger.warning(f"Invalid license key format: {key[:8]}...")
        return (False, None, None)
    
    if not validate_license_key_checksum(normalized):
        logger.warning(f"Invalid license key checksum: {key[:8]}...")
        return (False, None, None)
    
    tier = extract_tier_from_key(normalized)
    
    return (True, tier, normalized)


def generate_batch_keys(tier: str, count: int) -> list:
    """Generate multiple license keys.
    
    Args:
        tier: License tier
        count: Number of keys to generate
        
    Returns:
        List of generated license keys
    """
    return [generate_license_key(tier) for _ in range(count)]
