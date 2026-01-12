#!/usr/bin/env python3
"""Test script for enhanced matching logic.

This script tests the new scoring-based matching system with:
- Media ID normalization
- Composite scoring
- Enhanced logging
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timezone

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
os.chdir(project_root)

# Now import from src
from src.core.organizer import OrganizerCore


def test_normalize_media_id():
    """Test media ID normalization."""
    print("\n=== Testing Media ID Normalization ===")
    
    organizer = OrganizerCore(
        export_path=Path("/tmp/test"),
        output_path=Path("/tmp/out"),
    )
    
    test_cases = [
        ("b~Abc123XYZ_-test", "abc123xyz_-test"),
        ("b_Abc123XYZ_-test", "abc123xyz_-test"),
        ("Abc123XYZ_-test0123456789", "abc123xyz_-test0123456789"),  # 26 chars - valid base64
        ("some text b~ABC123 more text", "abc123"),
        ("", ""),
        ("short", ""),  # Too short to be valid
    ]
    
    for input_id, expected in test_cases:
        result = organizer._normalize_media_id(input_id)
        status = "✓" if result == expected else "✗"
        print(f"{status} Input: '{input_id[:30]}...' → '{result}' (expected: '{expected}')")


def test_extract_media_id_from_filename():
    """Test extracting media ID from filename."""
    print("\n=== Testing Media ID Extraction from Filename ===")
    
    organizer = OrganizerCore(
        export_path=Path("/tmp/test"),
        output_path=Path("/tmp/out"),
    )
    
    test_cases = [
        ("2023-01-15_b_Abc123XYZ.mp4", "abc123xyz"),
        ("2023-01-15_b~Abc123XYZ.mp4", "abc123xyz"),
        ("2023-01-15_metadata~zip.unknown", ""),
        ("2023-01-15.jpg", ""),
    ]
    
    for filename, expected in test_cases:
        result = organizer._extract_media_id_from_filename(filename)
        status = "✓" if result == expected else "✗"
        print(f"{status} File: '{filename}' → '{result}' (expected: '{expected}')")


def test_compute_match_score():
    """Test composite match scoring."""
    print("\n=== Testing Composite Match Scoring ===")
    
    organizer = OrganizerCore(
        export_path=Path("/tmp/test"),
        output_path=Path("/tmp/out"),
        timestamp_threshold=7200,
    )
    
    # Mock candidate
    file_datetime = datetime(2023, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
    file_date = datetime(2023, 1, 15, 0, 0, 0, tzinfo=timezone.utc)
    
    # Test exact media ID match
    candidate_exact = {
        "contact": "testuser",
        "datetime": datetime(2023, 1, 15, 12, 1, 0, tzinfo=timezone.utc),
        "media_id_normalized": "abc123xyz",
    }
    
    organizer.contact_freq_map["testuser"] = [
        datetime(2023, 1, 15, 11, 0, 0, tzinfo=timezone.utc),
        datetime(2023, 1, 15, 12, 0, 0, tzinfo=timezone.utc),
        datetime(2023, 1, 15, 13, 0, 0, tzinfo=timezone.utc),
    ]
    
    score, breakdown = organizer._compute_match_score(
        file_media_id="abc123xyz",
        file_datetime=file_datetime,
        file_date=file_date,
        candidate_info=candidate_exact,
        all_candidates=[],
    )
    
    print(f"\nExact Media ID Match:")
    print(f"  Total Score: {score:.3f}")
    print(f"  Media ID Score: {breakdown['media_id_score']:.3f}")
    print(f"  Time Diff Score: {breakdown['time_diff_score']:.3f} ({breakdown['time_diff_seconds']}s)")
    print(f"  Same Day Score: {breakdown['same_day_score']:.3f}")
    print(f"  Contact Freq Score: {breakdown['contact_freq_score']:.3f}")
    
    # Test fuzzy media ID match
    score_fuzzy, breakdown_fuzzy = organizer._compute_match_score(
        file_media_id="abc123",
        file_datetime=file_datetime,
        file_date=file_date,
        candidate_info=candidate_exact,
        all_candidates=[],
    )
    
    print(f"\nFuzzy Media ID Match:")
    print(f"  Total Score: {score_fuzzy:.3f}")
    print(f"  Media ID Score: {breakdown_fuzzy['media_id_score']:.3f}")
    
    # Test time-based only
    candidate_time = {
        "contact": "testuser",
        "datetime": datetime(2023, 1, 15, 12, 5, 0, tzinfo=timezone.utc),
        "media_id_normalized": "",
    }
    
    score_time, breakdown_time = organizer._compute_match_score(
        file_media_id="",
        file_datetime=file_datetime,
        file_date=file_date,
        candidate_info=candidate_time,
        all_candidates=[],
    )
    
    print(f"\nTime-based Only Match:")
    print(f"  Total Score: {score_time:.3f}")
    print(f"  Media ID Score: {breakdown_time['media_id_score']:.3f}")
    print(f"  Time Diff Score: {breakdown_time['time_diff_score']:.3f} ({breakdown_time['time_diff_seconds']}s)")


def test_format_match_reason():
    """Test match reason formatting."""
    print("\n=== Testing Match Reason Formatting ===")
    
    organizer = OrganizerCore(
        export_path=Path("/tmp/test"),
        output_path=Path("/tmp/out"),
    )
    
    test_cases = [
        {
            "media_id_score": 1.0,
            "time_diff_score": 0.95,
            "time_diff_seconds": 60,
            "same_day_score": 1.0,
            "contact_freq_score": 0.8,
        },
        {
            "media_id_score": 0.7,
            "time_diff_score": 0.6,
            "time_diff_seconds": 1800,
            "same_day_score": 1.0,
            "contact_freq_score": 0.3,
        },
        {
            "media_id_score": 0.0,
            "time_diff_score": 0.8,
            "time_diff_seconds": 600,
            "same_day_score": 0.5,
            "contact_freq_score": 0.2,
        },
    ]
    
    for i, breakdown in enumerate(test_cases, 1):
        reason = organizer._format_match_reason(breakdown)
        print(f"\nCase {i}: {reason}")
        print(f"  Breakdown: media_id={breakdown['media_id_score']:.2f}, "
              f"time={breakdown['time_diff_seconds']}s")


def main():
    """Run all tests."""
    print("=" * 80)
    print("Enhanced Matching Logic Test Suite")
    print("=" * 80)
    
    test_normalize_media_id()
    test_extract_media_id_from_filename()
    test_compute_match_score()
    test_format_match_reason()
    
    print("\n" + "=" * 80)
    print("All tests completed!")
    print("=" * 80)


if __name__ == "__main__":
    main()
