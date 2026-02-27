"""SQLAlchemy database models for license management.

This module defines the database schema for storing license information,
device registrations, and usage tracking.
"""

from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship, declarative_base, Session
from pathlib import Path

from ..utils.config import DB_PATH, TRIAL_DURATION_DAYS, TIER_FREE, TIER_PRO

Base = declarative_base()


class License(Base):
    """Represents a software license.
    
    Attributes:
        id: Primary key
        license_key: Unique license key string
        tier: License tier (free, pro, premium)
        email: Associated email address
        created_at: When the license was created
        expires_at: When the license expires (None for lifetime)
        is_active: Whether the license is currently active
        max_devices: Maximum number of devices allowed
        lemonsqueezy_id: External ID from Lemonsqueezy
    """
    
    __tablename__ = 'licenses'
    
    id = Column(Integer, primary_key=True)
    license_key = Column(String(64), unique=True, nullable=False, index=True)
    tier = Column(String(20), nullable=False, default=TIER_FREE)
    email = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)  # None = lifetime
    is_active = Column(Boolean, default=True)
    max_devices = Column(Integer, default=2)
    lemonsqueezy_id = Column(String(100), nullable=True, index=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    devices = relationship("Device", back_populates="license", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<License(key='{self.license_key[:8]}...', tier='{self.tier}', active={self.is_active})>"
    
    @property
    def is_expired(self) -> bool:
        """Check if the license has expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_valid(self) -> bool:
        """Check if the license is valid (active and not expired)."""
        return self.is_active and not self.is_expired
    
    @property
    def days_remaining(self) -> Optional[int]:
        """Get the number of days remaining on the license."""
        if self.expires_at is None:
            return None
        delta = self.expires_at - datetime.utcnow()
        return max(0, delta.days)
    
    @property
    def device_count(self) -> int:
        """Get the number of registered devices."""
        return len(self.devices)
    
    @property
    def can_add_device(self) -> bool:
        """Check if another device can be added."""
        return self.device_count < self.max_devices


class Device(Base):
    """Represents a device registration.
    
    Attributes:
        id: Primary key
        license_id: Foreign key to License
        hardware_id: Unique hardware identifier
        device_name: User-friendly device name
        platform: Operating system (Windows, macOS, Linux)
        registered_at: When the device was registered
        last_seen_at: Last time the device checked in
        is_active: Whether the device registration is active
    """
    
    __tablename__ = 'devices'
    
    id = Column(Integer, primary_key=True)
    license_id = Column(Integer, ForeignKey('licenses.id'), nullable=False)
    hardware_id = Column(String(128), nullable=False, index=True)
    device_name = Column(String(255), nullable=True)
    platform = Column(String(50), nullable=True)
    registered_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_seen_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    license = relationship("License", back_populates="devices")
    
    def __repr__(self):
        return f"<Device(name='{self.device_name}', platform='{self.platform}')>"
    
    def update_last_seen(self):
        """Update the last seen timestamp."""
        self.last_seen_at = datetime.utcnow()


class TrialInfo(Base):
    """Tracks trial usage for a device.
    
    Attributes:
        id: Primary key
        hardware_id: Unique hardware identifier
        trial_started_at: When the trial began
        trial_expires_at: When the trial expires
        files_processed: Number of files processed during trial
        is_converted: Whether the trial converted to a paid license
    """
    
    __tablename__ = 'trial_info'
    
    id = Column(Integer, primary_key=True)
    hardware_id = Column(String(128), unique=True, nullable=False, index=True)
    trial_started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    trial_expires_at = Column(DateTime, nullable=False)
    files_processed = Column(Integer, default=0)
    is_converted = Column(Boolean, default=False)
    
    def __init__(self, hardware_id: str):
        """Initialize trial info with expiration date.
        
        Args:
            hardware_id: Unique hardware identifier for the device
        """
        self.hardware_id = hardware_id
        self.trial_started_at = datetime.utcnow()
        self.trial_expires_at = self.trial_started_at + timedelta(days=TRIAL_DURATION_DAYS)
    
    def __repr__(self):
        return f"<TrialInfo(expires='{self.trial_expires_at}', converted={self.is_converted})>"
    
    @property
    def is_expired(self) -> bool:
        """Check if the trial has expired."""
        return datetime.utcnow() > self.trial_expires_at
    
    @property
    def is_active(self) -> bool:
        """Check if the trial is active (not expired and not converted)."""
        return not self.is_expired and not self.is_converted
    
    @property
    def days_remaining(self) -> int:
        """Get the number of days remaining in the trial."""
        if self.is_expired:
            return 0
        delta = self.trial_expires_at - datetime.utcnow()
        return max(0, delta.days)
    
    def increment_files_processed(self, count: int = 1):
        """Increment the files processed counter.
        
        Args:
            count: Number to add to the counter
        """
        self.files_processed += count


class UsageLog(Base):
    """Tracks feature usage for analytics.
    
    Attributes:
        id: Primary key
        hardware_id: Device hardware identifier
        feature: Feature name that was used
        timestamp: When the feature was used
        details: Additional usage details (JSON)
    """
    
    __tablename__ = 'usage_logs'
    
    id = Column(Integer, primary_key=True)
    hardware_id = Column(String(128), nullable=False, index=True)
    feature = Column(String(100), nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    details = Column(Text, nullable=True)  # JSON string
    
    def __repr__(self):
        return f"<UsageLog(feature='{self.feature}', timestamp='{self.timestamp}')>"


# Database engine and session management

_engine = None
_session_factory = None


def get_engine():
    """Get or create the database engine.
    
    Returns:
        SQLAlchemy engine instance
    """
    global _engine
    if _engine is None:
        # Ensure parent directory exists
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        _engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)
    return _engine


def init_database():
    """Initialize the database and create all tables.
    
    This should be called once when the application starts.
    """
    engine = get_engine()
    Base.metadata.create_all(engine)


def get_session() -> Session:
    """Get a new database session.
    
    Returns:
        SQLAlchemy session instance
        
    Note:
        Remember to close the session when done:
        session = get_session()
        try:
            # use session
        finally:
            session.close()
    """
    from sqlalchemy.orm import sessionmaker
    engine = get_engine()
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()
