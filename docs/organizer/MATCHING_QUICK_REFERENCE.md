# Enhanced Matching Logic - Quick Reference

## What Changed?

### 🔧 Core Improvements
1. **Smarter Media ID Matching**: Handles `b_`, `b~`, and no-prefix variations
2. **Composite Scoring**: Replaces binary tiers with weighted scores (0-1 scale)
3. **Better Logging**: Tracks match quality and flags low-confidence matches
4. **Original Preservation**: Optional `.snapchat_original` sidecar files

### 📊 Scoring Formula
```
Total Score = (0.5 × Media_ID) + (0.3 × Time_Proximity) + 
              (0.1 × Same_Day) + (0.1 × Contact_Activity)

Match if Score ≥ Threshold (default: 0.6)
```

## How to Use

### UI Settings (organize_tab.py)

#### Time Window
- **Old**: "Timestamp threshold" (30-3600s)
- **New**: "Time window" (300-14400s)
- **Default**: 7200s (2 hours)
- **Purpose**: Gaussian decay parameter for time-based scoring

#### Match Threshold
- **New control**: "Match threshold" (40-95%)
- **Default**: 60%
- **Lower = more matches**: May include false positives
- **Higher = stricter**: May miss valid matches

#### Preserve Originals
- **New checkbox**: Creates `.snapchat_original` sidecar files
- **Default**: Enabled
- **Contents**: Original filename, match score, metadata

### Reading the Report

#### `matching_report.txt` Structure
```
1. LOW CONFIDENCE MATCHES (score < 0.8)
   ⚠️  Review these manually

2. SUCCESSFUL MATCHES
   ✓ High confidence matches

3. REJECTED/UNMATCHED
   ✗ Below threshold or no candidates
```

#### Example Entry
```
File: 2023-01-15_b_xyz123.mp4
  Contact: john_doe
  Score: 0.672 (LOW CONFIDENCE)
  Score Breakdown:
    • Media ID: 0.000 (weight: 0.5) ← No media ID match
    • Time diff: 0.847 (weight: 0.3) ← Close timestamp
    • Same day: 1.000 (weight: 0.1) ← Same date
    • Contact freq: 0.600 (weight: 0.1) ← Active contact
  Reason: Moderate timestamp (1200s) + Same day + High contact activity
  Candidates: 5 (2 rejected)
```

## Interpreting Scores

### Media ID Score
- **1.0**: Exact match (best)
- **0.7**: Fuzzy match (prefix/suffix overlap)
- **0.0**: No match (relies on other factors)

### Time Diff Score
- **>0.9**: <5 minutes (excellent)
- **0.7-0.9**: 5-30 minutes (good)
- **0.5-0.7**: 30-60 minutes (moderate)
- **<0.5**: >60 minutes (weak)

### Overall Score Ranges
- **≥0.8**: High confidence - trust these
- **0.6-0.8**: Low confidence - review recommended
- **<0.6**: Rejected - too uncertain

## Common Scenarios

### Scenario 1: Perfect Match
```
Score: 0.928
Breakdown:
  • Media ID: 1.000 (exact b~ABC123)
  • Time diff: 0.992 (60s)
  • Same day: 1.000
  • Contact freq: 0.300
```
**Action**: Trust this match

### Scenario 2: Time-Based Match
```
Score: 0.672
Breakdown:
  • Media ID: 0.000 (no ID in filename)
  • Time diff: 0.847 (1200s = 20 min)
  • Same day: 1.000
  • Contact freq: 0.600
```
**Action**: Review - no media ID confirmation

### Scenario 3: Rejected
```
Score: 0.523 (threshold: 0.600)
Breakdown:
  • Media ID: 0.000
  • Time diff: 0.432 (3600s = 1 hour)
  • Same day: 1.000
  • Contact freq: 0.100
```
**Action**: Sent to `_Unmatched/` folder

## Tuning Tips

### Too Many False Positives?
✅ Increase match threshold: 60% → 65% or 70%  
✅ Reduce time window: 7200s → 3600s

### Too Many Unmatched?
✅ Decrease match threshold: 60% → 55% or 50%  
✅ Increase time window: 7200s → 10800s

### Low Confidence Matches Accurate?
✅ Lower the "high confidence" cutoff from 0.8 to 0.7  
✅ Adjust score weights in code (see below)

## Advanced: Modifying Score Weights

Edit `src/core/organizer.py`, method `_compute_match_score()`:

```python
# Current weights
total_score = (
    0.5 * media_id_score +      # 50% media ID
    0.3 * time_diff_score +      # 30% timestamp
    0.1 * same_day_score +       # 10% date
    0.1 * contact_freq_score     # 10% activity
)

# Example: Prioritize media ID more
total_score = (
    0.6 * media_id_score +      # 60% media ID
    0.25 * time_diff_score +     # 25% timestamp
    0.1 * same_day_score +       # 10% date
    0.05 * contact_freq_score    # 5% activity
)
```

## File Naming

### New Format
`20230115_120530_a3f5e2_4b8c1d9a.mp4`
- `20230115_120530`: Timestamp from JSON metadata
- `a3f5e2`: Contact hash (first 6 chars of MD5)
- `4b8c1d9a`: Media ID hash (first 8 chars)

### Benefits
- Sortable by date/time
- No collisions (hash-based)
- Traceable via sidecar file

### Sidecar File (`.snapchat_original`)
```
Original filename: 2023-01-15_b_Abc123XYZ.mp4
Match score: 0.928
Contact: john_doe
Timestamp: 2023-01-15 12:05:30 UTC
Is sender: false
Is saved: true
Media ID: b~Abc123XYZ...
```

## Statistics Breakdown

### Old UI
```
Tier 1 (Media ID): 347
Tier 2 (Single Contact): 483
Tier 3 (Timestamp): 79
```

### New UI
```
Match Type Breakdown:
  • Exact Media ID: 350
  • Fuzzy Media ID: 85
  • Time-based: 195

Quality Metrics:
  • Low confidence: 42 (score < 0.8)
```

## Troubleshooting

### "Too many low confidence matches"
1. Check `matching_report.txt` LOW CONFIDENCE section
2. Look for patterns (e.g., all from one contact)
3. Consider raising threshold to 65-70%

### "High unmatched rate (>40%)"
1. Check `matching_report.txt` REJECTED section
2. Look at rejected scores (how close to threshold?)
3. Consider lowering threshold to 55%
4. Check if media IDs are missing in filenames

### "Mismatched files (wrong contact)"
1. Review LOW CONFIDENCE matches first
2. Check sidecar files for match scores
3. Increase threshold for stricter matching
4. Report patterns for weight adjustment

## Testing Your Configuration

1. **Small test first**: Organize 50-100 files
2. **Review report**: Check LOW CONFIDENCE section
3. **Verify samples**: Manually check 10 random files
4. **Tune settings**: Adjust threshold based on accuracy
5. **Full run**: Process entire dataset

## Performance Expectations

### Speed
- ~1500 files: 30-60 seconds
- ~5000 files: 2-3 minutes
- ~10000 files: 4-6 minutes

### Accuracy Goals
- **Exact Media ID**: 95%+ precision
- **Fuzzy Media ID**: 85%+ precision
- **Time-based**: 70%+ precision (review recommended)

## Support

### Check These First
1. `matching_report.txt` - detailed match explanations
2. `.snapchat_original` files - match metadata
3. Application logs - error messages

### Report Issues With
- Match scores from report
- Sample filenames (anonymized)
- Expected vs actual contact
- Your threshold settings

---

**Quick Start**: Use defaults (7200s window, 60% threshold, preserve originals ON) → Review LOW CONFIDENCE section → Adjust threshold if needed.
