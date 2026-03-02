# Beta Testing Guide - Snapchat Organizer Desktop

**Version:** 1.0.0-beta.1  
**Last Updated:** February 2026  
**Copyright:** © 2026 Mohammed Haris. All rights reserved.

---

## Table of Contents

1. [What Is This App?](#what-is-this-app)
2. [Installation](#installation)
3. [First Launch & Onboarding](#first-launch--onboarding)
4. [License & Tiers](#license--tiers)
5. [Feature Walkthrough](#feature-walkthrough)
   - [Download Memories](#download-memories-tab)
   - [Organize Chat Media](#organize-chat-media-tab)
   - [Tools](#tools-tab)
6. [Settings](#settings)
7. [Troubleshooting](#troubleshooting)
8. [Testing Checklist](#testing-checklist)
9. [Reporting Bugs](#reporting-bugs)

---

## What Is This App?

Snapchat Organizer Desktop helps you organize and manage your Snapchat data exports. It can:

- **Download memories** from Snapchat HTML exports (memories_history.html)
- **Organize chat media** by person/conversation using intelligent 3-tier matching
- **Remove duplicate files** using SHA256 hash comparison
- **Verify file integrity** to find corrupted images/videos
- **Organize files by year** using EXIF metadata
- **Fix file timestamps** to match EXIF dates

All processing happens **locally on your computer** — nothing is uploaded.

---

## Installation

### macOS
1. Download `Snapchat-Organizer-macOS.dmg`
2. Open DMG → Drag to Applications
3. **Right-click** → **Open** (first time only, bypasses Gatekeeper)
4. See [macOS Installation Guide](MACOS_INSTALLATION_BETA.md) for details

### Windows
1. Download `Snapchat-Organizer-Windows.zip`
2. **Extract** the ZIP to `C:\SnapchatOrganizer\`
3. Run `SnapchatOrganizer.exe`
4. Click **"More info"** → **"Run anyway"** on SmartScreen (first time only)
5. See [Windows Installation Guide](WINDOWS_INSTALLATION_BETA.md) for details

### Linux
1. Download `Snapchat-Organizer-Linux.tar.gz`
2. Extract: `tar -xzf Snapchat-Organizer-Linux.tar.gz`
3. Run: `./Snapchat\ Organizer`
4. May need: `sudo apt install libxcb-xinerama0 libxcb-cursor0`

### Run from Source (Developers)
```bash
git clone https://github.com/M0hammedHaris/snapchat-organizer-desktop.git
cd snapchat-organizer-desktop
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

---

## First Launch & Onboarding

On first launch, you'll see:

1. **Onboarding Carousel** — A guided tour of the app's features. Swipe through the slides and click "Get Started" to proceed.

2. **License Dialog** — You can:
   - **Register** a free account (email + password)
   - **Login** with an existing account
   - **Skip** to use the Free tier without an account

3. **Main Window** — Three tabs (Download, Organize, Tools) with the Download tab selected by default.

4. Press **F1** at any time for the built-in help system.

---

## License & Tiers

The beta introduces a subscription-based licensing system:

| Feature | Free | Pro | Premium |
|---------|------|-----|---------|
| Download Memories | 100/month | 1,000/month | Unlimited |
| Organize Chat Media | No | Yes | Yes |
| Organize by Year | Yes | Yes | Yes |
| Fix Timestamps | Yes | Yes | Yes |
| Remove Duplicates | No | Yes | Yes |
| Verify Files | No | Yes | Yes |
| Overlay Compositing | No | Yes | Yes |
| GPS/Timezone Tools | No | Yes | Yes |
| Max Devices | 1 | 2 | 3 |

**For beta testing**: All testers start on the Free tier. Contact the developer for Pro/Premium access during testing.

---

## Feature Walkthrough

### Download Memories Tab

Downloads your Snapchat memories from the HTML export file.

**How to get your Snapchat data:**
1. Open Snapchat → Settings → My Data
2. Submit data request
3. Wait for email (usually 24 hours)
4. Download the ZIP and extract it

**Using the Download tab:**
1. Click **"Select HTML File"** → Choose `memories_history.html`
2. Click **"Select Output Folder"** → Choose where to save downloads
3. Configure options:
   - **Download Delay**: Time between requests (default: 2 seconds)
   - **Apply GPS Metadata**: Embed location data in photos
   - **Apply Overlays**: Composite Snapchat overlays onto images
   - **Convert Timezone**: Adjust timestamps to local time
4. Click **"Start Download"**
5. Monitor progress in the progress bar

**Controls:**
- **Start**: Begin downloading
- **Pause/Resume**: Pause and resume at any time
- **Cancel**: Stop the download (can be resumed later)

### Organize Chat Media Tab

Organizes scattered chat media files by person/conversation.

**What you need:**
- A folder containing your exported chat media files
- The `chat_history.json` file from your Snapchat export

**Steps:**
1. Click **"Select Media Folder"** → Choose folder with chat media
2. Click **"Select JSON File"** → Choose `chat_history.json`
3. Click **"Select Output Folder"** → Choose destination
4. Configure matching settings:
   - **Time Window**: How close timestamps must match (default: 300 seconds)
   - **Minimum Score**: Confidence threshold for matching (0-100)
5. Click **"Start Organizing"**
6. Review the matching report when complete

**How 3-tier matching works:**
1. **Tier 1 — Media ID**: Direct filename match (highest confidence)
2. **Tier 2 — Contact Name**: Matches by sender/conversation name
3. **Tier 3 — Timestamp**: Gaussian decay scoring by temporal proximity

### Tools Tab

Quick utility tools for media management:

| Tool | Description | Free Tier |
|------|-------------|-----------|
| **Verify Files** | Check images for corruption using PIL | Pro+ |
| **Remove Duplicates** | SHA256 hash comparison | Pro+ |
| **Organize by Year** | Sort files by EXIF date | Yes |
| **Fix Timestamps** | Sync file dates to EXIF | Yes |
| **Convert Timezone** | GPS-based timezone conversion | Placeholder |
| **Apply Overlays** | Composite overlay images | Placeholder |

**Using a tool:**
1. Select the tool
2. Click **"Select Folder"** to choose target folder
3. Click **"Run"**
4. View results summary when complete

---

## Settings

Access via **Ctrl+,** (or **Cmd+,** on macOS) or the File menu.

### General Tab
- Default paths for input/output
- Theme preference (follows system by default)
- Behavior options

### Download Tab
- Default delay between requests
- Number of retries
- Request timeout
- Default checkboxes (GPS, overlay, timezone)

### Organize Tab
- Default time window for matching
- Minimum confidence score
- File operation mode (copy vs. move)

### About Tab
- Version information
- License status
- Copyright notice

All settings persist across sessions in `~/.snapchat-organizer/config.json`.

---

## Troubleshooting

### Common Issues

**App won't launch**
- macOS: Right-click → Open (Gatekeeper bypass)
- Windows: Extract ZIP first, then run .exe
- Linux: Install `libxcb-xinerama0` and `libxcb-cursor0`

**"Failed to load Python DLL" (Windows)**
- Extract the ZIP before running — don't run from inside the ZIP
- Use a path without spaces: `C:\SnapchatOrganizer\`

**Slow first launch**
- Normal for PyInstaller apps — subsequent launches are faster

**Download tab: "No memories found"**
- Make sure you selected `memories_history.html` (not the ZIP)
- The file must be from Snapchat's data export

**Organize tab: "No matches found"**
- Check that media files and `chat_history.json` are from the same export
- Try lowering the minimum score threshold
- Increase the time window

**Theme looks wrong**
- The app auto-detects your system theme (light/dark)
- Restart the app if theme doesn't update

---

## Testing Checklist

Please test the following and report any issues:

### Installation
- [ ] Download and install on your OS
- [ ] App launches successfully
- [ ] Onboarding carousel displays correctly
- [ ] License dialog appears (login/register/skip)

### Download Tab
- [ ] Select HTML file (memories_history.html)
- [ ] Select output folder
- [ ] Configure options (delay, GPS, overlay, timezone)
- [ ] Start download — progress bar updates
- [ ] Pause/resume works
- [ ] Cancel works
- [ ] Files download correctly

### Organize Tab
- [ ] Select media folder
- [ ] Select JSON file (chat_history.json)
- [ ] Select output folder
- [ ] Start organizing — progress updates
- [ ] Matching report displays
- [ ] Files organized correctly by person

### Tools Tab
- [ ] Verify Files tool runs and reports results
- [ ] Remove Duplicates finds and handles duplicates
- [ ] Organize by Year sorts files correctly
- [ ] Fix Timestamps syncs dates properly
- [ ] Feature gating works (locked tools show upgrade message)

### Settings
- [ ] Settings dialog opens (Ctrl+,)
- [ ] Changes persist after restart
- [ ] Restore Defaults works

### General
- [ ] Help dialog opens (F1)
- [ ] Light/dark theme works correctly
- [ ] No crashes during normal use
- [ ] App exits cleanly

---

## Reporting Bugs

When reporting a bug, please include:

1. **What happened** — Describe the problem
2. **Steps to reproduce** — How can we trigger the bug?
3. **Expected behavior** — What should have happened?
4. **Your setup** — OS, version, screen size
5. **Error messages** — Any error text or screenshots
6. **Log file** (optional) — Found at `~/.snapchat-organizer/logs/app.log`

**Report here:** [GitHub Issues](https://github.com/M0hammedHaris/snapchat-organizer-desktop/issues/new)

---

**Thank you for testing! Your feedback directly shapes the final product.**
