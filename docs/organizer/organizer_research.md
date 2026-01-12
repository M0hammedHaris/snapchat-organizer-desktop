# Organizer — Short Research Brief

Purpose

- Provide a concise reference to guide research and experiments to improve the 3‑tier matching algorithm used by `OrganizerCore`.

Current state (summary)

- Matching strategy: Tier 1 (Media ID), Tier 2 (Single contact on date), Tier 3 (Timestamp proximity).
- Recent run: 157/826 files organized (19.0%). Breakdown: Tier1=22, Tier2=130, Tier3=5, Unmatched=669.
- Primary filename pattern: `YYYY-MM-DD_b~<base64-id>` (b~ base64 blob is the dominant identifier).

Key problems identified

- Media ID handling: earlier code truncated `b~` base64 strings (fixed to return full string). Ensure matching uses both prefixed (`b~...`) and non‑prefixed variants found in JSON.
- Timezone mismatch: JSON timestamps are UTC; file mtimes are local. Must normalize both to UTC before comparing (done).
- Thresholds & windowing: default threshold used by GUI was 300s; algorithm default is 3600s. Evaluate larger windows and adjacent‑day candidate sets.
- Over‑reliance on single heuristics: Tier 2 can produce many matches but is less precise; Tier 3 currently low yield.

Data patterns to collect

- Sample unmatched filenames and corresponding chat JSON entries (include `Created`, `Created(microseconds)`, `Media IDs`, `IsSender`, `IsSaved`).
- Distribution of file prefixes: `b~`, `media~`, `overlay~`, `thumbnail~`.
- Local vs JSON timestamp differences for a sample of matched and unmatched files.

Research & optimization directions

1. Robust Media ID matching
   - Normalize both sources: strip/append `b~` to compare both forms; match full base64 tokens.
   - Allow partial fuzzy matching (prefix/suffix) if full match not found, but score lower.
2. Use higher‑quality time features
   - Prefer `Created(microseconds)` when present (use as primary key if unique).
   - Convert file mtime to UTC; consider EXIF timestamps for photos as alternative timing source.
3. Probabilistic matching / scoring
   - Build a scoring function per candidate combining: media_id_score, time_diff_score, same_day_score, contact_frequency_score.
   - Pick highest scoring candidate above a confidence threshold; expose threshold to user and log low‑confidence matches for review.
4. Clustering & context heuristics
   - Group files by filename date and within a day cluster by mtime to match multi‑file sends.
   - Use conversation activity patterns (e.g., contact had many media entries near that time) to boost score.
5. Content‑based fallback (optional, medium term)
   - Use perceptual hashing (pHash) or small thumbnail matching to match content when metadata missing.
6. Instrumentation and feedback
   - Add structured logging for rejected candidates with reasons; collect examples for manual labeling and analysis.

Experiment plan & metrics

- Datasets: small held‑out sample (~200 files) with manual ground truth; then full run (800+ files).
- Metrics: Precision (correct matches / proposed matches), Recall (matched ground truth / total ground truth), false‑positive rate. Track match rate by tier and confidence buckets.
- A/B tests: baseline (current) vs. scoring model vs. scoring+content fallback.

Quick test harness suggestions

- Create `tests/data/sample_export/` with chat_history.json and ~200 media files.
- Script to run `OrganizerCore` with `create_debug_report=True` and produce `matching_report.txt` for analysis.

Next steps (recommended)

1. Run full organizer to collect unmatched samples (already done). Export 50–100 representative unmatched cases.
2. Implement scoring function and confidence threshold; log low‑confidence matches to `matching_report.txt`.
3. Evaluate on held‑out sample and iterate.

Useful files in repo

- `src/core/organizer.py` — current matching implementation and recent fixes
- `docs/organizer_research.md` — this brief
- `matching_report.txt` (output) — per‑run detailed decisions

Contact / notes

- If you want, I can (a) implement the scoring function and CI tests, or (b) build a small labeling tool to mark ground truth for unmatched files.
