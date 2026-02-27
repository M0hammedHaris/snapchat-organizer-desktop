"""Trial management for license system.

This module handles the 7-day trial period functionality,
including trial initialization, status checking, and expiration.
"""

from datetime import datetime
from typing import Optional, Dict, Any

from .models import TrialInfo, get_session, init_database
from .device import get_hardware_id
from ..utils.config import TRIAL_DURATION_DAYS, TRIAL_TIER, TIER_FREE
from ..utils.logger import get_logger

logger = get_logger(__name__)


class TrialStatus:
    """Status information about a trial.
    
    Attributes:
        is_active: Whether the trial is currently active
        is_expired: Whether the trial has expired
        is_available: Whether a trial can be started (never had one)
        days_remaining: Number of days left in the trial
        files_processed: Number of files processed during trial
        started_at: When the trial started
        expires_at: When the trial expires
    """
    
    def __init__(
        self,
        is_active: bool = False,
        is_expired: bool = False,
        is_available: bool = True,
        days_remaining: int = 0,
        files_processed: int = 0,
        started_at: Optional[datetime] = None,
        expires_at: Optional[datetime] = None,
    ):
        self.is_active = is_active
        self.is_expired = is_expired
        self.is_available = is_available
        self.days_remaining = days_remaining
        self.files_processed = files_processed
        self.started_at = started_at
        self.expires_at = expires_at
    
    @property
    def tier(self) -> str:
        """Get the tier for this trial status."""
        if self.is_active:
            return TRIAL_TIER
        return TIER_FREE
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'is_active': self.is_active,
            'is_expired': self.is_expired,
            'is_available': self.is_available,
            'days_remaining': self.days_remaining,
            'files_processed': self.files_processed,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'tier': self.tier,
        }


def get_trial_status(hardware_id: Optional[str] = None) -> TrialStatus:
    """Get the trial status for a device.
    
    Args:
        hardware_id: Hardware ID to check (default: current device)
        
    Returns:
        TrialStatus object with trial information
    """
    if hardware_id is None:
        hardware_id = get_hardware_id()
    
    logger.debug(f"Checking trial status for: {hardware_id[:16]}...")
    
    try:
        session = get_session()
        try:
            trial = session.query(TrialInfo).filter_by(
                hardware_id=hardware_id
            ).first()
            
            if trial is None:
                # No trial exists - trial is available
                return TrialStatus(
                    is_available=True,
                    days_remaining=TRIAL_DURATION_DAYS
                )
            
            if trial.is_converted:
                # Trial was converted to paid license
                return TrialStatus(
                    is_active=False,
                    is_expired=False,
                    is_available=False,
                    days_remaining=0,
                    files_processed=trial.files_processed,
                    started_at=trial.trial_started_at,
                    expires_at=trial.trial_expires_at,
                )
            
            if trial.is_active:
                return TrialStatus(
                    is_active=True,
                    is_expired=False,
                    is_available=False,
                    days_remaining=trial.days_remaining,
                    files_processed=trial.files_processed,
                    started_at=trial.trial_started_at,
                    expires_at=trial.trial_expires_at,
                )
            else:
                # Trial has expired
                return TrialStatus(
                    is_active=False,
                    is_expired=True,
                    is_available=False,
                    days_remaining=0,
                    files_processed=trial.files_processed,
                    started_at=trial.trial_started_at,
                    expires_at=trial.trial_expires_at,
                )
                
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Error getting trial status: {e}")
        # Return safe default
        return TrialStatus(
            is_available=False,
            days_remaining=0
        )


def start_trial(hardware_id: Optional[str] = None) -> TrialStatus:
    """Start a new trial for a device.
    
    Args:
        hardware_id: Hardware ID to start trial for (default: current device)
        
    Returns:
        TrialStatus object with the new trial information
    """
    if hardware_id is None:
        hardware_id = get_hardware_id()
    
    logger.info(f"Starting trial for device: {hardware_id[:16]}...")
    
    # Check if trial is available
    current_status = get_trial_status(hardware_id)
    if not current_status.is_available:
        logger.warning("Trial not available for this device")
        return current_status
    
    try:
        session = get_session()
        try:
            # Create new trial entry
            trial = TrialInfo(hardware_id=hardware_id)
            session.add(trial)
            session.commit()
            
            logger.info(f"Trial started, expires: {trial.trial_expires_at}")
            
            return TrialStatus(
                is_active=True,
                is_expired=False,
                is_available=False,
                days_remaining=trial.days_remaining,
                files_processed=0,
                started_at=trial.trial_started_at,
                expires_at=trial.trial_expires_at,
            )
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Error starting trial: {e}")
        return TrialStatus(
            is_available=False,
            days_remaining=0
        )


def record_trial_usage(files_count: int = 1, hardware_id: Optional[str] = None) -> bool:
    """Record file processing during trial.
    
    Args:
        files_count: Number of files processed
        hardware_id: Hardware ID (default: current device)
        
    Returns:
        True if recorded successfully, False otherwise
    """
    if hardware_id is None:
        hardware_id = get_hardware_id()
    
    try:
        session = get_session()
        try:
            trial = session.query(TrialInfo).filter_by(
                hardware_id=hardware_id
            ).first()
            
            if trial and trial.is_active:
                trial.increment_files_processed(files_count)
                session.commit()
                logger.debug(f"Recorded {files_count} files, total: {trial.files_processed}")
                return True
            
            return False
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Error recording trial usage: {e}")
        return False


def mark_trial_converted(hardware_id: Optional[str] = None) -> bool:
    """Mark a trial as converted to paid license.
    
    Args:
        hardware_id: Hardware ID (default: current device)
        
    Returns:
        True if marked successfully, False otherwise
    """
    if hardware_id is None:
        hardware_id = get_hardware_id()
    
    logger.info(f"Marking trial as converted: {hardware_id[:16]}...")
    
    try:
        session = get_session()
        try:
            trial = session.query(TrialInfo).filter_by(
                hardware_id=hardware_id
            ).first()
            
            if trial:
                trial.is_converted = True
                session.commit()
                logger.info("Trial marked as converted")
                return True
            
            return False
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Error marking trial converted: {e}")
        return False


def can_use_pro_features(hardware_id: Optional[str] = None) -> bool:
    """Check if a device can use Pro features (active trial or paid license).
    
    This is a convenience function that checks trial status.
    For full license checking, use validator.check_device_license().
    
    Args:
        hardware_id: Hardware ID (default: current device)
        
    Returns:
        True if Pro features are available, False otherwise
    """
    status = get_trial_status(hardware_id)
    return status.is_active


def get_trial_remaining_message(hardware_id: Optional[str] = None) -> str:
    """Get a human-readable message about trial status.
    
    Args:
        hardware_id: Hardware ID (default: current device)
        
    Returns:
        Message string describing trial status
    """
    status = get_trial_status(hardware_id)
    
    if status.is_available:
        return f"Start your {TRIAL_DURATION_DAYS}-day free trial!"
    
    if status.is_active:
        days = status.days_remaining
        if days == 0:
            return "Trial expires today!"
        elif days == 1:
            return "1 day left in your trial"
        else:
            return f"{days} days left in your trial"
    
    if status.is_expired:
        return "Your trial has expired. Upgrade to Pro for full access!"
    
    return "Trial converted to paid license"
