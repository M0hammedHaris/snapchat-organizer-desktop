"""License manager - main interface for license operations.

This module provides a unified interface for all license-related operations,
including validation, activation, trial management, and feature access control.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime

from .models import License, Device, TrialInfo, get_session, init_database
from .device import get_hardware_id, get_device_name, get_platform_name, get_device_info
from .key_generator import generate_license_key, parse_license_key
from .validator import (
    validate_license, activate_license, check_device_license,
    deactivate_device, ValidationResult, LicenseStatus
)
from .trial import (
    get_trial_status, start_trial, record_trial_usage,
    mark_trial_converted, can_use_pro_features, TrialStatus
)
from ..utils.config import (
    TIER_FREE, TIER_PRO, TIER_PREMIUM, TRIAL_TIER,
    FEATURE_ACCESS, can_access_feature
)
from ..utils.logger import get_logger

logger = get_logger(__name__)


class LicenseManager:
    """Central manager for all license operations.
    
    This class provides a high-level API for:
    - License validation and activation
    - Trial management
    - Feature access control
    - Device management
    
    Usage:
        manager = LicenseManager()
        manager.initialize()
        
        # Check current status
        status = manager.get_current_status()
        
        # Activate a license
        result = manager.activate("XXXX-XXXX-XXXX-XXXX-XXXX")
        
        # Check feature access
        can_download = manager.can_access("download_memories")
    """
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern - only one license manager per app."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._current_status: Optional[ValidationResult] = None
        self._trial_status: Optional[TrialStatus] = None
        self._initialized = True
        logger.debug("LicenseManager instance created")
    
    def initialize(self) -> None:
        """Initialize the license system.
        
        This should be called once at application startup.
        It initializes the database and checks the current device status.
        """
        logger.info("Initializing license system...")
        
        try:
            # Initialize database
            init_database()
            logger.debug("License database initialized")
            
            # Check current device status
            self._refresh_status()
            
            logger.info(f"License system initialized: tier={self.current_tier}, status={self._current_status.status.value}")
            
        except Exception as e:
            logger.error(f"Failed to initialize license system: {e}")
            # Set to free tier as fallback
            self._current_status = ValidationResult(
                status=LicenseStatus.FREE_TIER,
                tier=TIER_FREE,
                message="License system unavailable"
            )
    
    def _refresh_status(self) -> None:
        """Refresh the current license status from database."""
        self._current_status = check_device_license()
        self._trial_status = get_trial_status()
    
    @property
    def current_tier(self) -> str:
        """Get the current license tier."""
        if self._current_status is None:
            return TIER_FREE
        return self._current_status.tier
    
    @property
    def is_licensed(self) -> bool:
        """Check if the device has a valid license (not free tier)."""
        if self._current_status is None:
            return False
        return self._current_status.is_paid
    
    @property
    def is_trial(self) -> bool:
        """Check if the device is in trial mode."""
        if self._current_status is None:
            return False
        return self._current_status.is_trial
    
    @property
    def trial_available(self) -> bool:
        """Check if a trial can be started."""
        if self._trial_status is None:
            return True
        return self._trial_status.is_available
    
    @property
    def days_remaining(self) -> Optional[int]:
        """Get days remaining on license or trial."""
        if self._current_status is None:
            return None
        return self._current_status.days_remaining
    
    def get_current_status(self) -> ValidationResult:
        """Get the current license validation result.
        
        Returns:
            ValidationResult with current status
        """
        if self._current_status is None:
            self._refresh_status()
        return self._current_status
    
    def get_trial_status(self) -> TrialStatus:
        """Get the current trial status.
        
        Returns:
            TrialStatus with trial information
        """
        if self._trial_status is None:
            self._trial_status = get_trial_status()
        return self._trial_status
    
    def can_access(self, feature: str) -> bool:
        """Check if the current license allows access to a feature.
        
        Args:
            feature: Feature name to check (e.g., "download_memories")
            
        Returns:
            True if feature is accessible, False otherwise
        """
        return can_access_feature(self.current_tier, feature)
    
    def get_feature_access_map(self) -> Dict[str, bool]:
        """Get a map of all features and their access status.
        
        Returns:
            Dictionary mapping feature names to boolean access
        """
        tier = self.current_tier
        return {
            feature: can_access_feature(tier, feature)
            for feature in FEATURE_ACCESS[TIER_FREE].keys()
        }
    
    def activate(self, license_key: str) -> ValidationResult:
        """Activate a license on the current device.
        
        Args:
            license_key: The license key to activate
            
        Returns:
            ValidationResult with activation status
        """
        logger.info("Activating license...")
        result = activate_license(license_key)
        
        if result.is_valid:
            # Mark trial as converted if exists
            mark_trial_converted()
            
            # Refresh status
            self._refresh_status()
            
        return result
    
    def start_trial(self) -> TrialStatus:
        """Start a free trial on the current device.
        
        Returns:
            TrialStatus with trial information
        """
        logger.info("Starting trial...")
        status = start_trial()
        self._trial_status = status
        
        if status.is_active:
            self._refresh_status()
        
        return status
    
    def deactivate(self) -> bool:
        """Deactivate the current device from its license.
        
        Returns:
            True if deactivation successful, False otherwise
        """
        if self._current_status is None or not self._current_status.license_key:
            logger.warning("No active license to deactivate")
            return False
        
        success = deactivate_device(self._current_status.license_key)
        
        if success:
            self._refresh_status()
        
        return success
    
    def record_usage(self, files_count: int = 1) -> None:
        """Record file processing for trial tracking.
        
        Args:
            files_count: Number of files processed
        """
        if self.is_trial:
            record_trial_usage(files_count)
    
    def get_registered_devices(self) -> List[Dict[str, Any]]:
        """Get list of devices registered to the current license.
        
        Returns:
            List of device information dictionaries
        """
        if self._current_status is None or not self._current_status.license_key:
            return []
        
        try:
            session = get_session()
            try:
                _, _, normalized_key = parse_license_key(self._current_status.license_key)
                
                license_obj = session.query(License).filter_by(
                    license_key=normalized_key
                ).first()
                
                if not license_obj:
                    return []
                
                devices = []
                for device in license_obj.devices:
                    devices.append({
                        'device_name': device.device_name,
                        'platform': device.platform,
                        'registered_at': device.registered_at.isoformat() if device.registered_at else None,
                        'last_seen_at': device.last_seen_at.isoformat() if device.last_seen_at else None,
                        'is_active': device.is_active,
                        'is_current': device.hardware_id == get_hardware_id(),
                    })
                
                return devices
                
            finally:
                session.close()
                
        except Exception as e:
            logger.error(f"Error getting registered devices: {e}")
            return []
    
    def get_license_info(self) -> Dict[str, Any]:
        """Get comprehensive license information.
        
        Returns:
            Dictionary with all license-related information
        """
        status = self.get_current_status()
        trial_status = self.get_trial_status()
        
        return {
            'status': status.status.value,
            'tier': status.tier,
            'message': status.message,
            'is_valid': status.is_valid,
            'is_paid': status.is_paid,
            'is_trial': status.is_trial,
            'days_remaining': status.days_remaining,
            'license_key': status.license_key,
            'trial': {
                'is_active': trial_status.is_active,
                'is_expired': trial_status.is_expired,
                'is_available': trial_status.is_available,
                'days_remaining': trial_status.days_remaining,
                'files_processed': trial_status.files_processed,
            },
            'device': get_device_info(),
            'features': self.get_feature_access_map(),
        }
    
    def get_status_message(self) -> str:
        """Get a human-readable status message for display.
        
        Returns:
            Status message string
        """
        status = self.get_current_status()
        
        if status.status == LicenseStatus.VALID:
            tier_name = status.tier.capitalize()
            if status.days_remaining is not None:
                return f"{tier_name} License ({status.days_remaining} days remaining)"
            return f"{tier_name} License (Lifetime)"
        
        if status.status == LicenseStatus.TRIAL_ACTIVE:
            days = status.days_remaining or 0
            if days == 0:
                return "Trial expires today!"
            elif days == 1:
                return "Trial (1 day remaining)"
            return f"Trial ({days} days remaining)"
        
        if status.status == LicenseStatus.TRIAL_EXPIRED:
            return "Trial Expired - Upgrade to Pro"
        
        if status.status == LicenseStatus.EXPIRED:
            return "License Expired - Renew to continue"
        
        if status.status == LicenseStatus.FREE_TIER:
            if self.trial_available:
                return "Free Tier - Start a free trial!"
            return "Free Tier - Upgrade for full access"
        
        return "Free Tier"


# Global instance getter
def get_license_manager() -> LicenseManager:
    """Get the global LicenseManager instance.
    
    Returns:
        LicenseManager singleton instance
    """
    return LicenseManager()
