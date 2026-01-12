# Matching Logic Fix - January 12, 2026

## Problem Identified

Initial run showed **only 4.3% match rate** (46/1080 files):
- 23 exact Media ID matches
- 0 fuzzy matches
- 0 time-based matches
- 1057 unmatched (97.7%)

## Root Cause

**Threshold too high (0.6)** for time-based matching:
- Without media ID, max possible score was ~0.5
- Even perfect time matches (0s difference) couldn't pass 0.6
- Time-based matching was mathematically impossible

## Fixes Applied

### 1. Lowered Default Threshold
- **Before**: 0.6 (60%)
- **After**: 0.45 (45%)
- **UI default**: Changed from 60% to 45%

### 2. Dynamic Weight Adjustment
When media ID is absent (common case), boost time-based factors:

```python
# No Media ID present
total_score = (
    0.5 * time_diff_score +      # 50% (was 30%)
    0.2 * same_day_score +       # 20% (was 10%)
    0.3 * contact_freq_score     # 30% (was 10%)
)

# Media ID present (original)
total_score = (
    0.5 * media_id_score +
    0.3 * time_diff_score +
    0.1 * same_day_score +
    0.1 * contact_freq_score
)
```

### 3. Tier Toggle Support
Added backwards compatibility for tier checkboxes:
- Tier 1 disabled → Skip media ID matches
- Tier 2 disabled → Skip single-contact matches
- Tier 3 disabled → Skip multi-contact timestamp matches

## Expected Results

### Score Examples (New System)

| Scenario | Time Diff | Old Score | New Score | Pass 0.45? |
|----------|-----------|-----------|-----------|------------|
| No ID + 5min close | 300s | 0.468 | **0.920** | ✓ YES |
| No ID + 30min moderate | 1800s | 0.384 | **0.739** | ✓ YES |
| No ID + 1hr far | 3600s | 0.302 | **0.563** | ✓ YES |
| No ID + 2hr edge | 7200s | 0.260 | **0.534** | ✓ YES |

### Projected Match Rate

With 0.45 threshold:
- **Exact Media ID**: ~23-30 files (similar)
- **Fuzzy Media ID**: ~50-80 files (NEW - was 0)
- **Time-based**: ~400-600 files (NEW - was 0)
- **Total matched**: ~473-710 files (**44-66% match rate**)
- **Unmatched**: ~370-607 files

### Quality Control

Matches with score 0.45-0.70 = **LOW CONFIDENCE**
- Expected: ~200-300 files
- Recommendation: Manual review via `matching_report.txt`
- Flag in sidecar files for user verification

## Testing Instructions

1. **Rerun organization** with updated code
2. **Check statistics**:
   - Total matched should be ~450-700 (42-65%)
   - Low confidence should be ~200-300
3. **Review report**: Check `matching_report.txt` LOW CONFIDENCE section
4. **Verify samples**: Manually check 10 random low-confidence matches
5. **Tune if needed**:
   - Too many false positives? Raise to 0.50
   - Still too few matches? Lower to 0.40

## Files Modified

- `src/core/organizer.py`: Threshold, dynamic weights, tier toggles
- `src/core/organize_worker.py`: Updated default threshold
- `src/gui/organize_tab.py`: UI default changed to 45%

## Validation

Run `score_simulation.py` to see theoretical scores for various scenarios.

---

**Next Step**: Rerun the organizer and check if match rate improves to 40-65% range.
