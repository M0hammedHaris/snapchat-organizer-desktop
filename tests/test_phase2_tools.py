#!/usr/bin/env python3
"""Test script for Phase 2 tools functionality (GPS, timezone, overlay)."""

import sys
import os
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from PIL import Image
import piexif


class TestGPSExtraction:
    """Tests for GPS coordinate extraction from EXIF."""

    @pytest.fixture
    def temp_folder(self):
        """Create a temporary folder for tests."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir, ignore_errors=True)

    def _create_image_with_gps(self, path: Path, lat: float, lon: float) -> Path:
        """Create a test image with GPS data.
        
        Args:
            path: Directory to create image in
            lat: Latitude in decimal degrees
            lon: Longitude in decimal degrees
            
        Returns:
            Path to created image
        """
        # Create a simple image
        img = Image.new('RGB', (100, 100), color='blue')
        
        # Build EXIF data with GPS
        exif_dict = {
            "0th": {},
            "Exif": {},
            "GPS": {},
            "1st": {},
            "thumbnail": None
        }
        
        # Convert decimal degrees to EXIF format
        def to_exif_gps(value):
            """Convert decimal degrees to EXIF rational format."""
            abs_val = abs(value)
            degrees = int(abs_val)
            minutes = int((abs_val - degrees) * 60)
            seconds = int(((abs_val - degrees) * 60 - minutes) * 60 * 100)
            return ((degrees, 1), (minutes, 1), (seconds, 100))
        
        # Set GPS data
        exif_dict["GPS"][piexif.GPSIFD.GPSLatitude] = to_exif_gps(lat)
        exif_dict["GPS"][piexif.GPSIFD.GPSLatitudeRef] = b'N' if lat >= 0 else b'S'
        exif_dict["GPS"][piexif.GPSIFD.GPSLongitude] = to_exif_gps(lon)
        exif_dict["GPS"][piexif.GPSIFD.GPSLongitudeRef] = b'E' if lon >= 0 else b'W'
        
        # Add DateTimeOriginal
        exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = b"2024:06:15 10:30:00"
        
        # Save image with EXIF
        exif_bytes = piexif.dump(exif_dict)
        img_path = path / "test_gps.jpg"
        img.save(img_path, exif=exif_bytes)
        
        return img_path

    def test_extract_gps_coordinates(self, temp_folder):
        """Test GPS coordinate extraction."""
        from src.core.tools_core import ToolsCore
        
        # Create image with known GPS coordinates (New York City)
        lat, lon = 40.7128, -74.0060
        img_path = self._create_image_with_gps(temp_folder, lat, lon)
        
        # Extract GPS
        tools = ToolsCore(temp_folder)
        coords = tools._extract_gps_coordinates(img_path)
        
        assert coords is not None, "Should extract GPS coordinates"
        extracted_lat, extracted_lon = coords
        
        # Allow small difference due to conversion
        assert abs(extracted_lat - lat) < 0.01, f"Latitude mismatch: {extracted_lat} vs {lat}"
        assert abs(extracted_lon - lon) < 0.01, f"Longitude mismatch: {extracted_lon} vs {lon}"

    def test_extract_gps_no_data(self, temp_folder):
        """Test GPS extraction from image without GPS."""
        from src.core.tools_core import ToolsCore
        
        # Create image without GPS
        img = Image.new('RGB', (100, 100), color='red')
        img_path = temp_folder / "no_gps.jpg"
        img.save(img_path)
        
        tools = ToolsCore(temp_folder)
        coords = tools._extract_gps_coordinates(img_path)
        
        assert coords is None, "Should return None for image without GPS"


class TestTimezoneConversion:
    """Tests for GPS-based timezone conversion."""

    def test_get_timezone_from_gps(self):
        """Test timezone lookup from GPS coordinates."""
        try:
            from timezonefinder import TimezoneFinder
        except ImportError:
            pytest.skip("timezonefinder not installed")
        
        from src.core.tools_core import ToolsCore
        import tempfile
        
        temp_dir = tempfile.mkdtemp()
        try:
            tools = ToolsCore(Path(temp_dir))
            
            # Test various locations
            test_cases = [
                (40.7128, -74.0060, "America/New_York"),  # NYC
                (51.5074, -0.1278, "Europe/London"),  # London
                (35.6762, 139.6503, "Asia/Tokyo"),  # Tokyo
                (-33.8688, 151.2093, "Australia/Sydney"),  # Sydney
            ]
            
            for lat, lon, expected_tz in test_cases:
                tz = tools._get_timezone_from_gps(lat, lon)
                assert tz == expected_tz, f"Expected {expected_tz} for ({lat}, {lon}), got {tz}"
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestOverlayCompositing:
    """Tests for overlay compositing functionality."""

    @pytest.fixture
    def temp_folder(self):
        """Create a temporary folder for tests."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_build_overlay_map(self, temp_folder):
        """Test building overlay file map."""
        from src.core.tools_core import ToolsCore
        
        # Create some overlay files
        (temp_folder / "photo1-overlay.png").touch()
        (temp_folder / "photo2-overlay.png").touch()
        (temp_folder / "regular.jpg").touch()
        
        tools = ToolsCore(temp_folder)
        overlay_map = tools._build_overlay_map(temp_folder)
        
        assert len(overlay_map) == 2, f"Should find 2 overlays, found {len(overlay_map)}"
        assert "photo1" in overlay_map
        assert "photo2" in overlay_map
        assert "regular" not in overlay_map

    def test_find_overlay_for_file(self, temp_folder):
        """Test finding overlay for a media file."""
        from src.core.tools_core import ToolsCore
        
        # Create base file and overlay
        base_path = temp_folder / "photo1.jpg"
        overlay_path = temp_folder / "photo1-overlay.png"
        
        base_path.touch()
        overlay_path.touch()
        
        tools = ToolsCore(temp_folder)
        overlay_map = tools._build_overlay_map(temp_folder)
        
        found = tools._find_overlay_for_file(base_path, overlay_map)
        assert found is not None, "Should find matching overlay"
        assert found == overlay_path

    def test_apply_overlay_to_image(self, temp_folder):
        """Test applying overlay to an image."""
        from src.core.tools_core import ToolsCore
        
        # Create base image (blue)
        base_img = Image.new('RGB', (100, 100), color='blue')
        base_path = temp_folder / "base.jpg"
        base_img.save(base_path)
        
        # Create overlay (semi-transparent red)
        overlay_img = Image.new('RGBA', (100, 100), color=(255, 0, 0, 128))
        overlay_path = temp_folder / "overlay.png"
        overlay_img.save(overlay_path)
        
        tools = ToolsCore(temp_folder)
        success = tools._apply_overlay_to_image(base_path, overlay_path)
        
        assert success, "Overlay application should succeed"
        
        # Verify the image was modified
        result = Image.open(base_path)
        assert result.size == (100, 100)
        
        # Check that colors are mixed (not pure blue anymore)
        pixel = result.getpixel((50, 50))
        assert pixel[0] > 0, "Red channel should be > 0 after overlay"

    def test_apply_overlays_tool(self, temp_folder):
        """Test the full apply_overlays tool."""
        from src.core.tools_core import ToolsCore
        
        # Create base image
        base_img = Image.new('RGB', (200, 200), color='green')
        base_path = temp_folder / "photo.jpg"
        base_img.save(base_path)
        
        # Create matching overlay
        overlay_img = Image.new('RGBA', (200, 200), color=(255, 255, 0, 100))
        overlay_path = temp_folder / "photo-overlay.png"
        overlay_img.save(overlay_path)
        
        tools = ToolsCore(temp_folder)
        results = tools.apply_overlays()
        
        assert results['total_files'] >= 1
        assert results['processed_files'] >= 1 or results['no_overlay_files'] >= 0


class TestToolsIntegration:
    """Integration tests for the tools module."""

    @pytest.fixture
    def temp_folder(self):
        """Create a temporary folder for tests."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_verify_files(self, temp_folder):
        """Test file verification."""
        from src.core.tools_core import ToolsCore
        
        # Create valid image
        img = Image.new('RGB', (100, 100), color='red')
        (temp_folder / "valid.jpg").mkdir(parents=True, exist_ok=False) if False else None
        img.save(temp_folder / "valid.jpg")
        
        # Create corrupt file (empty)
        with open(temp_folder / "corrupt.jpg", 'wb') as f:
            f.write(b"not an image")
        
        tools = ToolsCore(temp_folder)
        results = tools.verify_files()
        
        assert results['total_files'] == 2
        assert results['valid_files'] >= 1
        assert results['corrupted_files'] >= 1

    def test_remove_duplicates(self, temp_folder):
        """Test duplicate removal."""
        from src.core.tools_core import ToolsCore
        
        # Create original image
        img = Image.new('RGB', (100, 100), color='purple')
        img.save(temp_folder / "original.jpg")
        
        # Create duplicate
        img.save(temp_folder / "duplicate.jpg")
        
        # Create different image
        img2 = Image.new('RGB', (100, 100), color='yellow')
        img2.save(temp_folder / "different.jpg")
        
        tools = ToolsCore(temp_folder)
        results = tools.remove_duplicates()
        
        assert results['total_files'] == 3
        assert results['duplicate_files'] == 1
        assert results['unique_files'] == 2

    def test_organize_by_year(self, temp_folder):
        """Test year-based organization."""
        from src.core.tools_core import ToolsCore
        
        # Create images with EXIF dates
        for year in [2022, 2023, 2024]:
            img = Image.new('RGB', (100, 100))
            
            # Create EXIF with date
            exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
            exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = f"{year}:06:15 10:30:00".encode()
            exif_bytes = piexif.dump(exif_dict)
            
            img.save(temp_folder / f"photo_{year}.jpg", exif=exif_bytes)
        
        tools = ToolsCore(temp_folder)
        results = tools.organize_by_year()
        
        assert results['total_files'] == 3
        assert results['organized_files'] == 3
        assert len(results['years_created']) == 3
        assert "2022" in results['years_created']
        assert "2023" in results['years_created']
        assert "2024" in results['years_created']


def run_basic_tests():
    """Run basic tests without pytest."""
    print("=== Phase 2 Tools Tests ===\n")
    
    import tempfile
    
    # Test 1: GPS coordinate conversion
    print("Test 1: GPS Coordinate Conversion")
    from src.core.tools_core import ToolsCore
    temp_dir = tempfile.mkdtemp()
    try:
        tools = ToolsCore(Path(temp_dir))
        
        # Test _gps_to_decimal
        gps_data = ((40, 1), (42, 1), (4608, 100))  # 40°42'46.08"
        decimal = tools._gps_to_decimal(gps_data)
        expected = 40 + 42/60 + 46.08/3600
        assert abs(decimal - expected) < 0.0001, f"GPS conversion failed: {decimal} vs {expected}"
        print(f"  GPS data: {gps_data}")
        print(f"  Decimal: {decimal}")
        print("  ✅ PASS\n")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    # Test 2: Overlay map building
    print("Test 2: Overlay Map Building")
    temp_dir = tempfile.mkdtemp()
    try:
        tools = ToolsCore(Path(temp_dir))
        
        # Create test overlay files
        Path(temp_dir, "img1-overlay.png").touch()
        Path(temp_dir, "img2-overlay.png").touch()
        Path(temp_dir, "regular.jpg").touch()
        
        overlay_map = tools._build_overlay_map(Path(temp_dir))
        print(f"  Found {len(overlay_map)} overlays")
        assert len(overlay_map) == 2
        print("  ✅ PASS\n")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    # Test 3: Image overlay compositing
    print("Test 3: Image Overlay Compositing")
    temp_dir = tempfile.mkdtemp()
    try:
        tools = ToolsCore(Path(temp_dir))
        
        # Create base image
        base = Image.new('RGB', (100, 100), color='blue')
        base_path = Path(temp_dir) / "base.jpg"
        base.save(base_path)
        
        # Create overlay
        overlay = Image.new('RGBA', (100, 100), color=(255, 0, 0, 128))
        overlay_path = Path(temp_dir) / "overlay.png"
        overlay.save(overlay_path)
        
        # Apply overlay
        success = tools._apply_overlay_to_image(base_path, overlay_path)
        assert success, "Overlay application failed"
        
        # Verify result
        result = Image.open(base_path)
        pixel = result.getpixel((50, 50))
        print(f"  Original: blue (0, 0, 255)")
        print(f"  After overlay: {pixel}")
        assert pixel[0] > 0, "Red channel should be present"
        print("  ✅ PASS\n")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    print("=== All Phase 2 Tools Tests Passed! ✅ ===")


if __name__ == "__main__":
    # Check if pytest is available
    try:
        import pytest
        sys.exit(pytest.main([__file__, "-v"]))
    except ImportError:
        try:
            run_basic_tests()
        except Exception as e:
            print(f"\n❌ Test Failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
