"""License validation logic.

This module provides functions for validating licenses against
the local database and optional remote verification.
"""

from datetime import datetime
from typing import Dict, Optional, Tuple, Any
from enum import Enum

from .models import License, Device, TrialInfo, get_session, init_database
from .device import get_hardware_id, get_device_name, get_platform_name
from .key_generator import parse_license_key, validate_license_key_checksum
from ..utils.config import TIER_FREE, TIER_PRO, TIER_PREMIUM, TRIAL_TIER
from ..utils.logger import get_logger

logger = get_logger(__name__)


class LicenseStatus(Enum):
    """Status codes for license validation."""
    VALID = "valid"
    EXPIRED = "expired"
    INVALID_KEY = "invalid_key"
    DEVICE_LIMIT = "device_limit"
    REVOKED = "revoked"
    NOT_FOUND = "not_found"
    TRIAL_ACTIVE = "trial_active"
    TRIAL_EXPIRED = "trial_expired"
    FREE_TIER = "free_tier"
    ERROR = "error"


class ValidationResult:
    """Result of license validation.
    
    Attributes:
        status: LicenseStatus enum value
        tier: License tier string
        message: Human-readable message
        days_remaining: Days until expiration (None for lifetime)
        license_key: The validated license key (if applicable)
        can_use_feature: Dict mapping feature names to boolean access
    """
    
    def __init__(
        self,
        status: LicenseStatus,
        tier: str = TIER_FREE,
        message: str = "",
        days_remaining: Optional[int] = None,
        license_key: Optional[str] = None,
    ):
        self.status = status
        self.tier = tier
        self.message = message
        self.days_remaining = days_remaining
        self.license_key = license_key
    
    @property
    def is_valid(self) -> bool:
        """Check if the license is valid for use."""
        return self.status in (
            LicenseStatus.VALID,
            LicenseStatus.TRIAL_ACTIVE,
            LicenseStatus.FREE_TIER,
        )
    
    @property
    def is_paid(self) -> bool:
        """Check if this is a paid license (not trial or free)."""
        return self.status == LicenseStatus.VALID and self.tier in (TIER_PRO, TIER_PREMIUM)
    
    @property
    def is_trial(self) -> bool:
        """Check if this is an active trial."""
        return self.status == LicenseStatus.TRIAL_ACTIVE
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'status': self.status.value,
            'tier': self.tier,
            'message': self.message,
            'days_remaining': self.days_remaining,
            'license_key': self.license_key,
            'is_valid': self.is_valid,
            'is_paid': self.is_paid,
            'is_trial': self.is_trial,
        }


def validate_license(license_key: str) -> ValidationResult:
    """Validate a license key.
    
    This performs both format validation and database lookup.
    
    Args:
        license_key: The license key to validate
        
    Returns:
        ValidationResult with status and tier information
    """
    logger.info(f"Validating license key: {license_key[:8]}...")
    
    # First, validate format and checksum
    is_valid, tier_from_key, normalized_key = parse_license_key(license_key)
    
    if not is_valid:
        logger.warning("License key format or checksum invalid")
        return ValidationResult(
            status=LicenseStatus.INVALID_KEY,
            message="Invalid license key format"
        )
    
    # Look up in database
    try:
        session = get_session()
        try:
            license_obj = session.query(License).filter_by(
                license_key=normalized_key
            ).first()
            
            if not license_obj:
                logger.info("License key not found in database")
                return ValidationResult(
                    status=LicenseStatus.NOT_FOUND,
                    message="License key not found"
                )
            
            # Check if license is active
            if not license_obj.is_active:
                logger.warning("License has been revoked")
                return ValidationResult(
                    status=LicenseStatus.REVOKED,
                    message="This license has been revoked"
                )
            
            # Check if license is expired
            if license_obj.is_expired:
                logger.warning("License has expired")
                return ValidationResult(
                    status=LicenseStatus.EXPIRED,
                    tier=license_obj.tier,
                    message="This license has expired",
                    days_remaining=0,
                    license_key=normalized_key
                )
            
            # License is valid!
            logger.info(f"License validated successfully: tier={license_obj.tier}")
            return ValidationResult(
                status=LicenseStatus.VALID,
                tier=license_obj.tier,
                message="License is valid",
                days_remaining=license_obj.days_remaining,
                license_key=normalized_key
            )
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Database error during license validation: {e}")
        return ValidationResult(
            status=LicenseStatus.ERROR,
            message=f"Validation error: {str(e)}"
        )


def activate_license(license_key: str) -> ValidationResult:
    """Activate a license on the current device.
    
    This validates the license and registers the current device.
    
    Args:
        license_key: The license key to activate
        
    Returns:
        ValidationResult with activation status
    """
    logger.info("Activating license on current device")
    
    # First validate the license
    validation = validate_license(license_key)
    
    if validation.status not in (LicenseStatus.VALID, LicenseStatus.NOT_FOUND):
        return validation
    
    # If key is valid but not in our database, it might be a new key
    # In production, we'd verify with Lemonsqueezy here
    if validation.status == LicenseStatus.NOT_FOUND:
        # For now, validate format and create local entry
        is_valid, tier, normalized_key = parse_license_key(license_key)
        if not is_valid:
            return ValidationResult(
                status=LicenseStatus.INVALID_KEY,
                message="Invalid license key format"
            )
        
        # This would normally be created after Lemonsqueezy verification
        logger.info("Creating new license entry (offline mode)")
        try:
            session = get_session()
            try:
                license_obj = License(
                    license_key=normalized_key,
                    tier=tier or TIER_PRO,
                    is_active=True,
                    max_devices=2
                )
                session.add(license_obj)
                session.commit()
                
                validation = ValidationResult(
                    status=LicenseStatus.VALID,
                    tier=license_obj.tier,
                    message="License activated",
                    days_remaining=license_obj.days_remaining,
                    license_key=normalized_key
                )
            finally:
                session.close()
        except Exception as e:
            logger.error(f"Failed to create license entry: {e}")
            return ValidationResult(
                status=LicenseStatus.ERROR,
                message=f"Activation error: {str(e)}"
            )
    
    # Register device
    try:
        session = get_session()
        try:
            hardware_id = get_hardware_id()
            
            license_obj = session.query(License).filter_by(
                license_key=validation.license_key
            ).first()
            
            if not license_obj:
                return ValidationResult(
                    status=LicenseStatus.ERROR,
                    message="License not found after validation"
                )
            
            # Check if device is already registered
            existing_device = session.query(Device).filter_by(
                license_id=license_obj.id,
                hardware_id=hardware_id
            ).first()
            
            if existing_device:
                existing_device.update_last_seen()
                session.commit()
                logger.info("Device already registered, updated last seen")
                return validation
            
            # Check device limit
            if not license_obj.can_add_device:
                logger.warning("Device limit reached")
                return ValidationResult(
                    status=LicenseStatus.DEVICE_LIMIT,
                    tier=license_obj.tier,
                    message=f"Device limit reached ({license_obj.max_devices} devices)",
                    license_key=validation.license_key
                )
            
            # Register new device
            new_device = Device(
                license_id=license_obj.id,
                hardware_id=hardware_id,
                device_name=get_device_name(),
                platform=get_platform_name()
            )
            session.add(new_device)
            session.commit()
            
            logger.info(f"Device registered successfully: {new_device.device_name}")
            return validation
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Device registration error: {e}")
        return ValidationResult(
            status=LicenseStatus.ERROR,
            message=f"Device registration error: {str(e)}"
        )


def check_device_license() -> ValidationResult:
    """Check if the current device has an active license.
    
    Returns:
        ValidationResult with the current license status
    """
    hardware_id = get_hardware_id()
    logger.debug(f"Checking device license for: {hardware_id[:16]}...")
    
    try:
        session = get_session()
        try:
            # First check for registered device with active license
            device = session.query(Device).filter_by(
                hardware_id=hardware_id,
                is_active=True
            ).first()
            
            if device and device.license:
                license_obj = device.license
                device.update_last_seen()
                session.commit()
                
                if not license_obj.is_active:
                    return ValidationResult(
                        status=LicenseStatus.REVOKED,
                        message="Your license has been revoked"
                    )
                
                if license_obj.is_expired:
                    return ValidationResult(
                        status=LicenseStatus.EXPIRED,
                        tier=license_obj.tier,
                        message="Your license has expired",
                        days_remaining=0,
                        license_key=license_obj.license_key
                    )
                
                return ValidationResult(
                    status=LicenseStatus.VALID,
                    tier=license_obj.tier,
                    message="License is valid",
                    days_remaining=license_obj.days_remaining,
                    license_key=license_obj.license_key
                )
            
            # Check for active trial
            trial = session.query(TrialInfo).filter_by(
                hardware_id=hardware_id
            ).first()
            
            if trial:
                if trial.is_converted:
                    # Trial was converted, but no device registration found
                    # This shouldn't happen in normal flow
                    logger.warning("Trial marked as converted but no device found")
                elif trial.is_active:
                    return ValidationResult(
                        status=LicenseStatus.TRIAL_ACTIVE,
                        tier=TRIAL_TIER,
                        message=f"Trial active: {trial.days_remaining} days remaining",
                        days_remaining=trial.days_remaining
                    )
                else:
                    return ValidationResult(
                        status=LicenseStatus.TRIAL_EXPIRED,
                        tier=TIER_FREE,
                        message="Your trial has expired"
                    )
            
            # No license or trial found - this is a free tier user
            return ValidationResult(
                status=LicenseStatus.FREE_TIER,
                tier=TIER_FREE,
                message="Free tier - some features are limited"
            )
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Error checking device license: {e}")
        return ValidationResult(
            status=LicenseStatus.ERROR,
            message=f"License check error: {str(e)}"
        )


def deactivate_device(license_key: str, hardware_id: Optional[str] = None) -> bool:
    """Deactivate a device from a license.
    
    Args:
        license_key: The license key
        hardware_id: Hardware ID to deactivate (default: current device)
        
    Returns:
        True if deactivation successful, False otherwise
    """
    if hardware_id is None:
        hardware_id = get_hardware_id()
    
    logger.info(f"Deactivating device: {hardware_id[:16]}...")
    
    try:
        session = get_session()
        try:
            _, _, normalized_key = parse_license_key(license_key)
            
            license_obj = session.query(License).filter_by(
                license_key=normalized_key
            ).first()
            
            if not license_obj:
                logger.warning("License not found for deactivation")
                return False
            
            device = session.query(Device).filter_by(
                license_id=license_obj.id,
                hardware_id=hardware_id
            ).first()
            
            if not device:
                logger.warning("Device not found for deactivation")
                return False
            
            device.is_active = False
            session.commit()
            
            logger.info("Device deactivated successfully")
            return True
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Device deactivation error: {e}")
        return False
