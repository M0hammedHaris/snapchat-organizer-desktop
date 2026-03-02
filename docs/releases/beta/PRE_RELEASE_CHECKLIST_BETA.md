# Pre-Release Checklist - Beta 1.0.0-beta.1

**Date:** February 2026  
**Release Tag:** v1.0.0-beta.1

---

## Version Numbers

- [ ] `src/main.py` → `_APP_VERSION = "1.0.0-beta.1"`
- [ ] `src/utils/config.py` → `APP_VERSION = "1.0.0-beta.1"`
- [ ] `file_version_info.txt` → `ProductVersion = 1.0.0-beta.1`
- [ ] `snapchat-organizer.spec` → Info.plist `CFBundleVersion = 1.0.0-beta.1`
- [ ] Build scripts reference beta version

## Code Quality

- [ ] No `print()` statements in production code (use `logging`)
- [ ] No hardcoded secrets, API keys, or credentials in source
- [ ] All public functions have type hints and docstrings
- [ ] No commented-out code blocks
- [ ] No debug/development flags left enabled
- [ ] Sentry DSN is correct for production environment

## Security Checks

- [ ] Sentry DSN does not leak sensitive user data
- [ ] License API client uses HTTPS only
- [ ] No plaintext passwords stored on disk
- [ ] File permissions are restricted on sensitive paths (~/.snapchat-organizer/)
- [ ] Input validation on all user-facing fields (file paths, URLs)
- [ ] No shell=True in subprocess calls

## Feature Verification

- [ ] Onboarding carousel displays on first launch
- [ ] License dialog: login, register, skip all work
- [ ] Download tab: file selection, progress, cancel/resume
- [ ] Organize tab: folder selection, JSON selection, matching
- [ ] Tools tab: all 4 active tools functional
- [ ] Tools tab: placeholder tools show appropriate message
- [ ] Feature gating: Free tier restricted correctly
- [ ] Settings dialog: load, save, restore defaults
- [ ] Help dialog: F1 shortcut works
- [ ] Light/dark theme detection and switching
- [ ] App exits cleanly (no zombie processes)

## Build Verification

- [ ] `pyinstaller snapchat-organizer.spec --clean --noconfirm` builds cleanly
- [ ] macOS: .app bundle launches, ad-hoc signing works
- [ ] Windows: .exe launches, version info in Properties
- [ ] Linux: tarball extracts and runs
- [ ] No missing DLLs or dependencies in build

## Documentation

- [ ] `docs/releases/beta/README_BETA.md` — Quick start guide
- [ ] `docs/releases/beta/BETA_TESTING_GUIDE.md` — Complete walkthrough
- [ ] `docs/releases/beta/MACOS_INSTALLATION_BETA.md` — macOS guide
- [ ] `docs/releases/beta/WINDOWS_INSTALLATION_BETA.md` — Windows guide
- [ ] `docs/releases/beta/BETA_RELEASE_NOTES.md` — What's new
- [ ] `README.md` updated with beta references
- [ ] `PROGRESS.md` updated with beta status

## GitHub Release

- [ ] Create git tag: `git tag v1.0.0-beta.1 -m "Beta Release 1"`
- [ ] Push tag: `git push origin v1.0.0-beta.1`
- [ ] GitHub Actions workflow triggers and completes
- [ ] All 3 platform builds succeed (macOS, Windows, Linux)
- [ ] Release page created with correct notes
- [ ] Download links work for all platforms

## Post-Release

- [ ] Verify download and install on macOS
- [ ] Verify download and install on Windows
- [ ] Share release link with beta testers
- [ ] Monitor Sentry for crash reports
- [ ] Monitor GitHub Issues for bug reports

---

## Release Commands

```bash
# 1. Commit all beta changes
git add -A
git commit -m "feat: prepare v1.0.0-beta.1 release

- Bump version to 1.0.0-beta.1
- Update build scripts and spec for beta
- Create beta release documentation
- Update README.md and PROGRESS.md
- Update GitHub Actions workflow for beta"

# 2. Create and push tag
git tag v1.0.0-beta.1 -m "Beta Release 1.0.0-beta.1"
git push origin main
git push origin v1.0.0-beta.1

# 3. Monitor build
# Visit: https://github.com/M0hammedHaris/snapchat-organizer-desktop/actions
```
