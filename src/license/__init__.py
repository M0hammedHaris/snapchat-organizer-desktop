"""Snapchat Organizer Desktop - License management package.

This package handles license validation, user authentication,
device fingerprinting, and API communication with the license server.
"""

from .license_manager import LicenseManager
from .api_client import LicenseAPIClient

__all__ = ['LicenseManager', 'LicenseAPIClient']
