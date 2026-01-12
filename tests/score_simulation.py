#!/usr/bin/env python3
"""Quick score simulation to understand matching behavior."""

import math

def simulate_scores():
    """Simulate various matching scenarios."""
    
    print("=" * 80)
    print("SCORE SIMULATION - Understanding Match Thresholds")
    print("=" * 80)
    
    scenarios = [
        {
            "name": "Perfect Media ID + Close Time (60s)",
            "media_id": 1.0,
            "time_diff_seconds": 60,
            "same_day": 1.0,
            "contact_freq": 0.3,
        },
        {
            "name": "Exact Media ID + Moderate Time (30min)",
            "media_id": 1.0,
            "time_diff_seconds": 1800,
            "same_day": 1.0,
            "contact_freq": 0.3,
        },
        {
            "name": "No Media ID + Perfect Time (0s) + High Activity",
            "media_id": 0.0,
            "time_diff_seconds": 0,
            "same_day": 1.0,
            "contact_freq": 1.0,
        },
        {
            "name": "No Media ID + Close Time (5min) + High Activity",
            "media_id": 0.0,
            "time_diff_seconds": 300,
            "same_day": 1.0,
            "contact_freq": 0.8,
        },
        {
            "name": "No Media ID + Moderate Time (30min) + Moderate Activity",
            "media_id": 0.0,
            "time_diff_seconds": 1800,
            "same_day": 1.0,
            "contact_freq": 0.5,
        },
        {
            "name": "No Media ID + Far Time (1hr) + Low Activity",
            "media_id": 0.0,
            "time_diff_seconds": 3600,
            "same_day": 1.0,
            "contact_freq": 0.2,
        },
        {
            "name": "No Media ID + Very Far (2hr) + Single Contact",
            "media_id": 0.0,
            "time_diff_seconds": 7200,
            "same_day": 1.0,
            "contact_freq": 0.5,
        },
        {
            "name": "Fuzzy Media ID (0.7) + Moderate Time",
            "media_id": 0.7,
            "time_diff_seconds": 1800,
            "same_day": 1.0,
            "contact_freq": 0.4,
        },
    ]
    
    for scenario in scenarios:
        media_id = scenario["media_id"]
        time_seconds = scenario["time_diff_seconds"]
        same_day = scenario["same_day"]
        contact_freq = scenario["contact_freq"]
        
        # Calculate time diff score (Gaussian decay over 7200s window)
        time_diff_score = math.exp(-time_seconds / 7200)
        
        # Calculate with original weights
        score_original = (
            0.5 * media_id +
            0.3 * time_diff_score +
            0.1 * same_day +
            0.1 * contact_freq
        )
        
        # Calculate with dynamic weights (no media ID)
        if media_id == 0.0:
            score_dynamic = (
                0.5 * time_diff_score +
                0.2 * same_day +
                0.3 * contact_freq
            )
        else:
            score_dynamic = score_original
        
        print(f"\n{scenario['name']}")
        print(f"  Inputs: media_id={media_id:.1f}, time={time_seconds}s, "
              f"same_day={same_day:.1f}, freq={contact_freq:.1f}")
        print(f"  Time diff score: {time_diff_score:.3f}")
        print(f"  Total (original weights): {score_original:.3f}")
        print(f"  Total (dynamic weights): {score_dynamic:.3f}")
        print(f"  Pass 0.45 threshold? {score_dynamic:.3f} >= 0.45: {'✓ YES' if score_dynamic >= 0.45 else '✗ NO'}")
        print(f"  Pass 0.60 threshold? {score_dynamic:.3f} >= 0.60: {'✓ YES' if score_dynamic >= 0.60 else '✗ NO'}")
    
    print("\n" + "=" * 80)
    print("RECOMMENDATION: Use 0.45 threshold for balanced matching")
    print("- Allows time-based matches when close proximity")
    print("- Still filters out weak/distant matches")
    print("- Review LOW CONFIDENCE (<0.7) matches manually")
    print("=" * 80)

if __name__ == "__main__":
    simulate_scores()
