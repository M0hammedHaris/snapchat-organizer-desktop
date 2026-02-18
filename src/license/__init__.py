"""Snapchat Organizer Desktop - License management package.

This package provides license validation, device fingerprinting,
trial management, and Lemonsqueezy integration for the application.

Key components:
- models: SQLAlchemy database models for licenses and devices
- device: Hardware fingerprinting and device identification
- key_generator: License key generation and validation
- validator: License validation logic
- trial: Trial period management
- manager: High-level license management interface
- lemonsqueezy: Lemonsqueezy API client for license verification
"""

from .manager import LicenseManager, get_license_manager
from .validator import LicenseStatus, ValidationResult
from .trial import TrialStatus, get_trial_status, start_trial
from .device import get_hardware_id, get_device_info
from .key_generator import generate_license_key, parse_license_key
from .models import init_database

__all__ = [
    'LicenseManager',
    'get_license_manager',
    'LicenseStatus',
    'ValidationResult',
    'TrialStatus',
    'get_trial_status',
    'start_trial',
    'get_hardware_id',
    'get_device_info',
    'generate_license_key',
    'parse_license_key',
    'init_database',
]
