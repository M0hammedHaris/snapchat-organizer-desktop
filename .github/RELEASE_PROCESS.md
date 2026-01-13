# Release Process Guide

Complete step-by-step guide for creating new releases of Snapchat Organizer Desktop.

**Last Updated:** January 13, 2026  
**Maintainer:** GitHub Copilot  
**Version:** 1.0

---

## 📋 Pre-Release Checklist

Before starting the release process, ensure:

- [ ] All changes are committed and pushed to `aplha-release` branch
- [ ] Code review completed (if applicable)
- [ ] Tests passing (`pytest`)
- [ ] No uncommitted changes (`git status` is clean)
- [ ] Version number planned (semantic versioning: MAJOR.MINOR.PATCH-alpha)

---

## 🚀 Release Process (Step-by-Step)

### Step 1: Verify Git Status

```bash
cd /path/to/snapchat-organizer-desktop
git status
```

**Expected Result:**
```
On branch aplha-release
Your branch is up to date with 'origin/aplha-release'.
nothing to commit, working tree clean
```

### Step 2: Update README.md

Update the version number and download links at the top of `README.md`:

**Find and replace:**
```markdown
**Status:** ✅ MVP Complete - Alpha Ready for Testing  
**Version:** 1.0.1-alpha (Windows SmartScreen Fix)  
**Last Updated:** January 13, 2026

> **🎉 Latest:** v1.0.1-alpha released! Windows metadata + comprehensive SmartScreen bypass guide included.
```

**Replace with:**
```markdown
**Status:** ✅ MVP Complete - Alpha Ready for Testing  
**Version:** 1.0.2-alpha (Your Feature Summary)  
**Last Updated:** January 13, 2026

> **🎉 Latest:** v1.0.2-alpha released! Your feature summary here.
```

Also update the download link:
```markdown
**🔗 [👉 Go to Release Downloads](https://github.com/M0hammedHaris/snapchat-organizer-desktop/releases/tag/v1.0.2-alpha)**
```

### Step 3: Update PROGRESS.md

Update the version and status at the top:

```markdown
**Current Phase:** Alpha Release - Public Testing (v1.0.2-alpha)  
**Status:** 🚀 RELEASED v1.0.2-alpha - Your Feature Summary

## 🎯 Overall Progress: 100% Phase 1 Complete + Alpha Release v1.0.2! 🎉

### Phase 1: Foundation & MVP (Week 1-2) - 100% Complete ✅
### 🚀 v1.0.2-alpha - January 13, 2026 ✅ YOUR FEATURE SUMMARY
```

Add a new release section documenting all features and changes:

```markdown
**v1.0.2-alpha Release** (100%) ✅ RELEASED - January 13, 2026
- [x] Feature 1 description
- [x] Feature 2 description
- [x] Feature 3 description
- [x] GitHub PR created with release notes
- [x] Git tag v1.0.2-alpha created
- [x] Tag pushed to GitHub for automated builds
- **Features:**
  - Auto-detect system settings
  - Professional styling
  - Improved user experience
- **Release:** https://github.com/M0hammedHaris/snapchat-organizer-desktop/releases/tag/v1.0.2-alpha
- **Status:** Build should now succeed on all platforms
```

Update the release build section:

```markdown
### Alpha Release Build ✅
- **v1.0.2-alpha** - January 13, 2026 ⭐ CURRENT RELEASE (Your Feature Summary)
- **Released:** January 13, 2026
- **Tag:** v1.0.2-alpha
- **Commit:** abc1234 (docs: update to v1.0.2-alpha with your changes)
- **Download:** https://github.com/M0hammedHaris/snapchat-organizer-desktop/releases/tag/v1.0.2-alpha
```

Update the final timestamp:

```markdown
**Last Updated:** January 13, 2026 - HH:MM UTC  
**Updated By:** GitHub Copilot  
**Session Duration:** ~X hours (v1.0.2-alpha release with your features)
**Current Status:** 🚀 v1.0.2-alpha RELEASED - Your feature summary  
**v1.0.2-alpha Release:** January 13, 2026 ⭐  
**Download:** https://github.com/M0hammedHaris/snapchat-organizer-desktop/releases/tag/v1.0.2-alpha
```

### Step 4: Commit Documentation Changes

```bash
git add README.md PROGRESS.md
git commit -m "docs(readme,progress): update to v1.0.2-alpha with feature summary"
```

### Step 5: Push Documentation Commits

```bash
git push origin aplha-release
```

**Expected Result:**
```
Enumerating objects: X, done.
...
To https://github.com/M0hammedHaris/snapchat-organizer-desktop.git
   abc1234..def5678  aplha-release -> aplha-release
```

### Step 6: Create GitHub PR with Release Notes (Using MCP)

Use the GitHub MCP tool to create a pull request documenting the release:

```
TOOL: mcp_github_github_create_pull_request

Parameters:
- owner: "M0hammedHaris"
- repo: "snapchat-organizer-desktop"
- title: "v1.0.2-alpha: Feature Summary"
- head: "aplha-release"
- base: "main"
- body: """
## v1.0.2-alpha Release: Feature Summary

**Release Date:** January 13, 2026

### What's New

#### 🎨 Feature 1
- Detailed description
- Implementation notes

#### 🎯 Feature 2
- Detailed description
- Implementation notes

### Backwards Compatibility
- ✅ All existing features work as before
- ✅ Settings fully compatible with v1.0.1

### Testing
- Tested on macOS with feature
- Verified functionality

### Downloads
- macOS: `Snapchat-Organizer-1.0.2-alpha.dmg`
- Windows: `Snapchat-Organizer-Windows.zip`
- Linux: `Snapchat-Organizer-Linux.tar.gz`

**Status:** Ready for immediate release! 🚀
"""
```

**Result:** GitHub PR is created (e.g., PR #8)

### Step 7: Create Git Tag

```bash
git tag v1.0.2-alpha
```

### Step 8: Push Tag to GitHub (Triggers Build)

```bash
git push origin v1.0.2-alpha
```

**Expected Result:**
```
To https://github.com/M0hammedHaris/snapchat-organizer-desktop.git
 * [new tag]         v1.0.2-alpha -> v1.0.2-alpha
```

### Step 9: Verify Tag Was Created

```bash
git tag -l | tail -5
```

**Expected Result:**
```
v1.0.0-alpha
v1.0.1-alpha
v1.0.2-alpha
```

### Step 10: Final Commit (Document Release)

```bash
git add PROGRESS.md
git commit -m "release: document v1.0.2-alpha release with feature summary"
git push origin aplha-release
```

---

## ✅ Verification Steps

After completing the release process, verify everything is correct:

### Check Git Log

```bash
git log --oneline -5
```

Should show your recent commits.

### Check Tags

```bash
git tag -l | sort -V | tail -3
```

Should show the new tag (v1.0.2-alpha).

### Check GitHub

Visit: https://github.com/M0hammedHaris/snapchat-organizer-desktop

- [ ] New PR #X exists with release notes
- [ ] New tag v1.0.2-alpha exists in releases tab
- [ ] GitHub Actions workflow triggered (check Actions tab)
- [ ] Builds running for macOS, Windows, Linux

---

## 🔧 Common Issues & Fixes

### Issue 1: PyInstaller Wildcard Patterns Error

**Error Message:**
```
ERROR: Unable to find '/home/runner/work/.../resources/icons/*.icns' when adding binary and data files.
```

**Fix:**
1. Edit `snapchat-organizer.spec`
2. Replace wildcard patterns in `datas`:
   ```python
   # ❌ WRONG
   datas=[
       ('resources/icons/*.png', 'resources/icons'),
       ('resources/icons/*.icns', 'resources/icons'),
   ]
   
   # ✅ CORRECT
   datas=[
       ('resources', 'resources'),
   ]
   ```
3. Re-tag the release:
   ```bash
   git tag -d v1.0.2-alpha
   git push origin :refs/tags/v1.0.2-alpha
   git tag v1.0.2-alpha
   git push origin v1.0.2-alpha
   ```

### Issue 2: Build Fails Due to Missing Dependency

**Check and fix:**
1. Review `requirements.txt`
2. Ensure all dependencies are listed
3. Test locally: `pip install -r requirements.txt`
4. Run the app: `python src/main.py`
5. If it works, push a commit and re-tag

### Issue 3: GitHub Actions Workflow Doesn't Run

**Check:**
1. Tag is spelled correctly (case-sensitive)
2. Tag was pushed: `git push origin v1.0.2-alpha`
3. Repository has `.github/workflows/build-release.yml`
4. Workflow is enabled in GitHub Actions settings

---

## 📝 Release Notes Template

Use this template when creating the GitHub PR release notes:

```markdown
## v1.0.X-alpha Release: Feature Title

**Release Date:** January 13, 2026

### What's New

#### 🎨 Feature Category 1
- Feature description
- Implementation details
- User benefits

#### 🎯 Feature Category 2
- Feature description
- Implementation details
- User benefits

### Bug Fixes
- [ ] Fixed issue #XX - description
- [ ] Fixed issue #YY - description

### Improvements
- [ ] Improved performance by X%
- [ ] Enhanced user experience
- [ ] Better error handling

### Dependencies
- [ ] Added dependency A (version)
- [ ] Updated dependency B (old → new)

### Backwards Compatibility
- ✅ All existing features work as before
- ✅ Settings/configuration fully compatible
- ⚠️ (List any breaking changes if any)

### Known Limitations (Phase 2+)
- Feature X (coming in Phase 2)
- Feature Y (coming in Phase 3)

### Testing
- Tested on macOS [version]
- Tested on Windows [version]
- Tested on Linux [version]
- All features verified working

### For Alpha Testers

**macOS Installation:**
- Right-click app → Open (one-time)
- Then double-click normally

**Windows Installation:**
- Click "More info" → "Run anyway" on SmartScreen (one-time)
- Then double-click normally

### Downloads
- macOS: `Snapchat-Organizer-1.0.2-alpha.dmg`
- Windows: `Snapchat-Organizer-Windows.zip`
- Linux: `Snapchat-Organizer-Linux.tar.gz`

**Status:** Ready for immediate release! 🚀
```

---

## 🎯 Release Flow Diagram

```
┌─────────────────────────────────────────────────┐
│ 1. Verify git status (working tree clean)      │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│ 2. Update README.md                             │
│    - Version number                             │
│    - Download links                             │
│    - Last updated date                          │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│ 3. Update PROGRESS.md                           │
│    - Current version                            │
│    - Release features                           │
│    - Download links                             │
│    - Timestamp                                  │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│ 4. Commit & Push                                │
│    git add README.md PROGRESS.md                │
│    git commit -m "docs: update to vX.X.X"      │
│    git push origin aplha-release                │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│ 5. Create GitHub PR (MCP)                       │
│    - Comprehensive release notes                │
│    - Feature descriptions                       │
│    - Download links                             │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│ 6. Create Git Tag                               │
│    git tag vX.X.X                               │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│ 7. Push Tag (Triggers GitHub Actions)           │
│    git push origin vX.X.X                       │
│    ✅ Automated build starts                    │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│ 8. Final Commit (Document Release)              │
│    git add PROGRESS.md                          │
│    git commit -m "release: document vX.X.X"    │
│    git push origin aplha-release                │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│ 9. Verify                                       │
│    - PR created on GitHub                       │
│    - Tag visible on GitHub                      │
│    - GitHub Actions running                     │
│    - All commits pushed                         │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│ ✅ RELEASE COMPLETE                             │
│ Installers available for:                       │
│ - macOS (.dmg)                                  │
│ - Windows (.zip)                                │
│ - Linux (.tar.gz)                               │
└─────────────────────────────────────────────────┘
```

---

## 🔗 Useful GitHub MCP Tools for Releases

### Create Pull Request
```
mcp_github_github_create_pull_request
- owner: repository owner
- repo: repository name
- title: PR title
- head: source branch (aplha-release)
- base: target branch (main)
- body: release notes in markdown
```

### Create/Update File
```
mcp_github_github_create_or_update_file
- owner: repository owner
- repo: repository name
- path: file path
- content: file content
- message: commit message
- branch: branch name (aplha-release)
```

### Merge Pull Request
```
mcp_github_github_merge_pull_request
- owner: repository owner
- repo: repository name
- pullNumber: PR number
- merge_method: "squash" or "merge"
```

---

## 📞 Troubleshooting

### Builds Not Running After Tagging

1. Check `.github/workflows/build-release.yml` exists
2. Verify GitHub Actions is enabled in repository settings
3. Check tag name matches workflow trigger pattern
4. Review GitHub Actions logs for errors

### Icons Not Bundled in Build

1. Check `snapchat-organizer.spec` datas section
2. Ensure `resources/` directory exists in project root
3. Verify icon files are in `resources/icons/`
4. Don't use wildcard patterns (e.g., `*.png`) in spec file
5. Use full directory paths instead: `('resources', 'resources')`

### Version Mismatch Between README and Tag

1. Always update README first
2. Then create tag with matching version
3. If mismatch exists, re-tag:
   ```bash
   git tag -d v1.0.2-alpha
   git push origin :refs/tags/v1.0.2-alpha
   git tag v1.0.2-alpha
   git push origin v1.0.2-alpha
   ```

---

## 📌 Quick Reference

### Full Release Command Sequence

```bash
# 1. Edit files
nano README.md          # Update version, links
nano PROGRESS.md        # Update version, features

# 2. Commit changes
git add README.md PROGRESS.md
git commit -m "docs: update to v1.0.2-alpha with feature summary"
git push origin aplha-release

# 3. Create GitHub PR (via MCP)
# [Use mcp_github_github_create_pull_request]

# 4. Create and push tag
git tag v1.0.2-alpha
git push origin v1.0.2-alpha

# 5. Final documentation commit
git add PROGRESS.md
git commit -m "release: document v1.0.2-alpha release with feature summary"
git push origin aplha-release

# 6. Verify
git log --oneline -5
git tag -l | tail -3
```

### Verify Release Success

```bash
# Check local commits
git log --oneline -10

# Check local tags
git tag -l | sort -V | tail -5

# Check remote status
git ls-remote origin | grep tags | tail -5
```

---

## 📚 Related Documentation

- **Copilot Instructions:** `.github/copilot-instructions.md`
- **Build Guide:** `docs/releases/alpha/BUILD_SUMMARY.md`
- **Alpha Testing:** `docs/releases/alpha/ALPHA_TESTING_GUIDE.md`
- **Windows Issues:** `docs/releases/alpha/WINDOWS_INSTALLATION.md`
- **macOS Issues:** `docs/releases/alpha/MACOS_INSTALLATION.md`

---

## ✨ Tips for Success

1. **Always verify git status is clean before starting**
   ```bash
   git status
   ```

2. **Test locally before releasing**
   ```bash
   python src/main.py
   pytest
   ```

3. **Double-check version numbers match across all files**
   - README.md
   - PROGRESS.md
   - Git tag
   - GitHub PR title

4. **Use consistent commit message format**
   ```
   type(scope): description
   
   Examples:
   - docs(readme): update version
   - release: document v1.0.2-alpha
   - fix(build): resolve PyInstaller issue
   ```

5. **Monitor GitHub Actions after tagging**
   - Watch the Actions tab for build progress
   - Check for failures and fix if needed
   - Builds should complete within 10-15 minutes

6. **Keep PROGRESS.md as source of truth**
   - Update after every significant change
   - Reference when planning Phase 2
   - Helps future agents understand context

---

**Last Updated:** January 13, 2026  
**Next Review:** After v1.0.3-alpha release  
**Maintainer:** GitHub Copilot
