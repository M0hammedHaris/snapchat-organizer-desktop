#!/usr/bin/env python3
"""Test script for license system functionality."""

import sys
import os
import tempfile
import shutil
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest


class TestKeyGenerator:
    """Tests for license key generation and validation."""

    def test_generate_license_key_format(self):
        """Test that generated keys have correct format."""
        from src.license.key_generator import generate_license_key, KEY_PATTERN
        
        key = generate_license_key()
        assert KEY_PATTERN.match(key), f"Key '{key}' does not match expected pattern"
        assert len(key) == 29, f"Key length should be 29 (25 chars + 4 dashes), got {len(key)}"

    def test_generate_license_key_tiers(self):
        """Test that keys are generated with correct tier prefixes."""
        from src.license.key_generator import generate_license_key
        
        free_key = generate_license_key(tier="free")
        assert free_key.startswith("FREE0-"), f"Free key should start with FREE0-, got {free_key[:6]}"
        
        pro_key = generate_license_key(tier="pro")
        assert pro_key.startswith("PRO26-"), f"Pro key should start with PRO26-, got {pro_key[:6]}"
        
        premium_key = generate_license_key(tier="premium")
        assert premium_key.startswith("PREM0-"), f"Premium key should start with PREM0-, got {premium_key[:6]}"

    def test_validate_key_format(self):
        """Test key format validation."""
        from src.license.key_generator import validate_license_key_format
        
        # Valid formats (5 characters per segment)
        assert validate_license_key_format("AAAAA-BBBBB-CCCCC-DDDDD-EEEEE")
        assert validate_license_key_format("12345-67890-12345-67890-12345")
        assert validate_license_key_format("PRO26-ABCDE-FGHIJ-KLMNO-PQ123")
        # Lowercase is normalized to uppercase
        assert validate_license_key_format("aaaaa-bbbbb-ccccc-ddddd-eeeee")
        
        # Invalid formats
        assert not validate_license_key_format("")
        assert not validate_license_key_format("invalid")
        assert not validate_license_key_format("AAAA-BBBB-CCCC")
        assert not validate_license_key_format("AAAA-BBBB-CCCC-DDDD-EEEE")  # 4-char segments

    def test_validate_key_checksum(self):
        """Test key checksum validation."""
        from src.license.key_generator import generate_license_key, validate_license_key_checksum
        
        # Generated keys should have valid checksums
        for _ in range(10):
            key = generate_license_key()
            assert validate_license_key_checksum(key), f"Generated key {key} should have valid checksum"
        
        # Modified keys should have invalid checksums
        key = generate_license_key()
        modified = key[:-1] + ("A" if key[-1] != "A" else "B")
        assert not validate_license_key_checksum(modified), "Modified key should have invalid checksum"

    def test_parse_license_key(self):
        """Test license key parsing."""
        from src.license.key_generator import generate_license_key, parse_license_key
        
        # Valid key
        key = generate_license_key(tier="pro")
        is_valid, tier, normalized = parse_license_key(key)
        assert is_valid, "Valid key should be parsed successfully"
        assert tier == "pro", f"Tier should be 'pro', got '{tier}'"
        assert normalized == key, "Normalized key should match original"
        
        # Invalid key
        is_valid, tier, normalized = parse_license_key("INVALID-KEY")
        assert not is_valid, "Invalid key should not be parsed"
        assert tier is None
        assert normalized is None

    def test_normalize_license_key(self):
        """Test license key normalization."""
        from src.license.key_generator import normalize_license_key
        
        # With spaces (5-char segments)
        assert normalize_license_key("aaaaa bbbbb ccccc ddddd eeeee") == "AAAAA-BBBBB-CCCCC-DDDDD-EEEEE"
        
        # With different separators
        assert normalize_license_key("aaaaa.bbbbb.ccccc.ddddd.eeeee") == "AAAAA-BBBBB-CCCCC-DDDDD-EEEEE"
        
        # Mixed case
        assert normalize_license_key("AaAaA-BbBbB-CcCcC-DdDdD-EeEeE") == "AAAAA-BBBBB-CCCCC-DDDDD-EEEEE"

    def test_batch_key_generation(self):
        """Test batch key generation."""
        from src.license.key_generator import generate_batch_keys, validate_license_key_checksum
        
        keys = generate_batch_keys("pro", 5)
        assert len(keys) == 5, f"Should generate 5 keys, got {len(keys)}"
        
        # All keys should be unique
        assert len(set(keys)) == 5, "All generated keys should be unique"
        
        # All keys should be valid
        for key in keys:
            assert validate_license_key_checksum(key), f"Batch key {key} should be valid"


class TestDeviceFingerprinting:
    """Tests for device fingerprinting."""

    def test_get_hardware_id(self):
        """Test hardware ID generation."""
        from src.license.device import get_hardware_id
        
        hw_id = get_hardware_id()
        assert hw_id is not None
        assert len(hw_id) == 64, f"Hardware ID should be 64 chars (SHA-256), got {len(hw_id)}"
        assert all(c in '0123456789abcdef' for c in hw_id), "Hardware ID should be hex"
        
        # Same ID should be generated each time
        hw_id2 = get_hardware_id()
        assert hw_id == hw_id2, "Hardware ID should be consistent"

    def test_get_device_name(self):
        """Test device name generation."""
        from src.license.device import get_device_name
        
        name = get_device_name()
        assert name is not None
        assert len(name) > 0
        assert "(" in name and ")" in name, "Device name should include platform in parentheses"

    def test_get_platform_name(self):
        """Test platform name detection."""
        from src.license.device import get_platform_name
        import platform
        
        plat_name = get_platform_name()
        assert plat_name is not None
        
        # Should contain something about the system
        system = platform.system()
        if system == "Darwin":
            assert "macOS" in plat_name
        elif system == "Windows":
            assert "Windows" in plat_name
        elif system == "Linux":
            # On Linux, it might say "Ubuntu", "Debian", "Linux", etc.
            assert len(plat_name) > 0, "Platform name should not be empty"

    def test_get_device_info(self):
        """Test device info retrieval."""
        from src.license.device import get_device_info
        
        info = get_device_info()
        assert "hardware_id" in info
        assert "device_name" in info
        assert "platform" in info
        assert "hostname" in info
        assert "system" in info


class TestTrialSystem:
    """Tests for trial management."""

    @pytest.fixture
    def temp_db_dir(self):
        """Create a temporary directory for test database."""
        temp_dir = tempfile.mkdtemp()
        
        # Patch the DB_PATH and reset engine
        import src.license.models as models
        original_db_path = models.DB_PATH
        original_engine = models._engine
        
        models.DB_PATH = Path(temp_dir) / "test_organizer.db"
        models._engine = None  # Reset engine to use new path
        
        yield temp_dir
        
        # Cleanup
        models.DB_PATH = original_db_path
        models._engine = original_engine
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_trial_status_new_device(self, temp_db_dir):
        """Test trial status for a new device."""
        from src.license.models import init_database
        from src.license.trial import get_trial_status
        
        init_database()
        
        status = get_trial_status()
        assert status.is_available, "Trial should be available for new device"
        assert not status.is_active, "Trial should not be active before starting"
        assert not status.is_expired, "Trial should not be expired for new device"

    def test_start_trial(self, temp_db_dir):
        """Test starting a trial."""
        from src.license.models import init_database
        from src.license.trial import start_trial, get_trial_status
        from src.utils.config import TRIAL_DURATION_DAYS
        
        init_database()
        
        # Start trial
        status = start_trial()
        assert status.is_active, "Trial should be active after starting"
        # Allow for off-by-one due to date calculation timing
        assert status.days_remaining >= TRIAL_DURATION_DAYS - 1, f"Should have at least {TRIAL_DURATION_DAYS - 1} days"
        
        # Check status again
        status2 = get_trial_status()
        assert status2.is_active
        assert not status2.is_available, "Trial should not be available after starting"

    def test_trial_usage_tracking(self, temp_db_dir):
        """Test trial usage tracking."""
        from src.license.models import init_database
        from src.license.trial import start_trial, record_trial_usage, get_trial_status
        
        init_database()
        start_trial()
        
        # Record some usage
        record_trial_usage(10)
        status = get_trial_status()
        assert status.files_processed == 10, "Should track 10 files processed"
        
        # Record more usage
        record_trial_usage(5)
        status = get_trial_status()
        assert status.files_processed == 15, "Should track 15 files total"


class TestLicenseValidation:
    """Tests for license validation."""

    @pytest.fixture
    def temp_db_dir(self):
        """Create a temporary directory for test database."""
        temp_dir = tempfile.mkdtemp()
        
        # Patch the DB_PATH and reset engine
        import src.license.models as models
        original_db_path = models.DB_PATH
        original_engine = models._engine
        
        models.DB_PATH = Path(temp_dir) / "test_organizer.db"
        models._engine = None  # Reset engine to use new path
        
        yield temp_dir
        
        # Cleanup
        models.DB_PATH = original_db_path
        models._engine = original_engine
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_validate_invalid_key(self, temp_db_dir):
        """Test validation of invalid key."""
        from src.license.models import init_database
        from src.license.validator import validate_license, LicenseStatus
        
        init_database()
        
        result = validate_license("INVALID-KEY-FORMAT")
        assert result.status == LicenseStatus.INVALID_KEY

    def test_validate_nonexistent_key(self, temp_db_dir):
        """Test validation of valid format but nonexistent key."""
        from src.license.models import init_database
        from src.license.validator import validate_license, LicenseStatus
        from src.license.key_generator import generate_license_key
        
        init_database()
        
        key = generate_license_key()
        result = validate_license(key)
        assert result.status == LicenseStatus.NOT_FOUND

    def test_activate_license(self, temp_db_dir):
        """Test license activation."""
        from src.license.models import init_database
        from src.license.validator import activate_license, LicenseStatus
        from src.license.key_generator import generate_license_key
        
        init_database()
        
        key = generate_license_key(tier="pro")
        result = activate_license(key)
        assert result.status == LicenseStatus.VALID
        assert result.tier == "pro"

    def test_check_device_license_free(self, temp_db_dir):
        """Test checking device license for free tier."""
        from src.license.models import init_database
        from src.license.validator import check_device_license, LicenseStatus
        
        init_database()
        
        result = check_device_license()
        assert result.status == LicenseStatus.FREE_TIER


class TestLicenseManager:
    """Tests for the license manager."""

    @pytest.fixture
    def temp_db_dir(self):
        """Create a temporary directory for test database."""
        temp_dir = tempfile.mkdtemp()
        
        # Patch the DB_PATH and reset engine
        import src.license.models as models
        original_db_path = models.DB_PATH
        original_engine = models._engine
        
        models.DB_PATH = Path(temp_dir) / "test_organizer.db"
        models._engine = None  # Reset engine to use new path
        
        # Reset the singleton
        from src.license.manager import LicenseManager
        LicenseManager._instance = None
        
        yield temp_dir
        
        # Cleanup
        models.DB_PATH = original_db_path
        models._engine = original_engine
        LicenseManager._instance = None
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_initialize(self, temp_db_dir):
        """Test license manager initialization."""
        from src.license.manager import get_license_manager
        
        manager = get_license_manager()
        manager.initialize()
        
        assert manager.current_tier is not None

    def test_can_access_free_features(self, temp_db_dir):
        """Test free tier feature access."""
        from src.license.manager import get_license_manager
        
        manager = get_license_manager()
        manager.initialize()
        
        # Free features should be accessible
        assert manager.can_access("organize_chat_media")
        assert manager.can_access("organize_by_year")
        assert manager.can_access("fix_timestamps")
        
        # Pro features should not be accessible
        assert not manager.can_access("download_memories")
        assert not manager.can_access("overlay_compositing")

    def test_get_feature_access_map(self, temp_db_dir):
        """Test getting feature access map."""
        from src.license.manager import get_license_manager
        
        manager = get_license_manager()
        manager.initialize()
        
        features = manager.get_feature_access_map()
        assert isinstance(features, dict)
        assert "organize_chat_media" in features
        assert "download_memories" in features

    def test_get_license_info(self, temp_db_dir):
        """Test getting license info."""
        from src.license.manager import get_license_manager
        
        manager = get_license_manager()
        manager.initialize()
        
        info = manager.get_license_info()
        assert "status" in info
        assert "tier" in info
        assert "features" in info
        assert "device" in info


def run_basic_tests():
    """Run basic tests without pytest."""
    print("=== License System Tests ===\n")
    
    # Test key generation
    print("Test 1: Key Generation")
    from src.license.key_generator import generate_license_key, validate_license_key_checksum
    key = generate_license_key()
    print(f"  Generated key: {key}")
    assert validate_license_key_checksum(key), "Key should be valid"
    print("  ✅ PASS\n")
    
    # Test device fingerprinting
    print("Test 2: Device Fingerprinting")
    from src.license.device import get_hardware_id, get_device_name
    hw_id = get_hardware_id()
    device_name = get_device_name()
    print(f"  Hardware ID: {hw_id[:16]}...")
    print(f"  Device name: {device_name}")
    assert len(hw_id) == 64
    print("  ✅ PASS\n")
    
    # Test tier prefixes
    print("Test 3: Tier Prefixes")
    pro_key = generate_license_key(tier="pro")
    free_key = generate_license_key(tier="free")
    print(f"  Pro key: {pro_key}")
    print(f"  Free key: {free_key}")
    assert pro_key.startswith("PRO26-")
    assert free_key.startswith("FREE0-")
    print("  ✅ PASS\n")
    
    print("=== All Basic Tests Passed! ✅ ===")


if __name__ == "__main__":
    # Check if pytest is available
    try:
        import pytest
        # Run pytest
        sys.exit(pytest.main([__file__, "-v"]))
    except ImportError:
        # Run basic tests without pytest
        try:
            run_basic_tests()
        except Exception as e:
            print(f"\n❌ Test Failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
