#!/usr/bin/env python3
"""Test script for first-run detection functionality."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from utils.config import (
    is_first_run,
    mark_first_run_complete,
    should_show_help_on_startup,
    set_show_help_on_startup,
    FIRST_RUN_MARKER,
    CONFIG_FILE,
)


def test_first_run():
    """Test the first-run detection system."""
    print("=== First-Run Detection Test ===\n")
    
    # Clean slate
    if FIRST_RUN_MARKER.exists():
        FIRST_RUN_MARKER.unlink()
        print("✓ Removed existing first-run marker")
    
    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()
        print("✓ Removed existing config file")
    
    print()
    
    # Test 1: First run detection
    print("Test 1: First Run Detection")
    print(f"  is_first_run(): {is_first_run()}")
    print(f"  should_show_help_on_startup(): {should_show_help_on_startup()}")
    assert is_first_run() == True, "Should be first run"
    assert should_show_help_on_startup() == True, "Should show help on first run"
    print("  ✅ PASS\n")
    
    # Test 2: Mark first run complete
    print("Test 2: Mark First Run Complete")
    mark_first_run_complete()
    print(f"  Marker file exists: {FIRST_RUN_MARKER.exists()}")
    print(f"  is_first_run(): {is_first_run()}")
    assert FIRST_RUN_MARKER.exists(), "Marker file should exist"
    assert is_first_run() == False, "Should no longer be first run"
    print("  ✅ PASS\n")
    
    # Test 3: Default behavior after first run
    print("Test 3: Default Behavior After First Run")
    print(f"  should_show_help_on_startup(): {should_show_help_on_startup()}")
    assert should_show_help_on_startup() == False, "Should not show help by default after first run"
    print("  ✅ PASS\n")
    
    # Test 4: User opts to show help again
    print("Test 4: User Opts to Show Help Again")
    set_show_help_on_startup(True)
    print(f"  Config file exists: {CONFIG_FILE.exists()}")
    print(f"  should_show_help_on_startup(): {should_show_help_on_startup()}")
    assert CONFIG_FILE.exists(), "Config file should exist"
    assert should_show_help_on_startup() == True, "Should show help when enabled in config"
    print("  ✅ PASS\n")
    
    # Test 5: User opts not to show help
    print("Test 5: User Opts Not to Show Help")
    set_show_help_on_startup(False)
    print(f"  should_show_help_on_startup(): {should_show_help_on_startup()}")
    assert should_show_help_on_startup() == False, "Should not show help when disabled"
    print("  ✅ PASS\n")
    
    print("=== All Tests Passed! ✅ ===")
    print(f"\nFiles created:")
    print(f"  • {FIRST_RUN_MARKER}")
    print(f"  • {CONFIG_FILE}")


if __name__ == "__main__":
    try:
        test_first_run()
    except Exception as e:
        print(f"\n❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
