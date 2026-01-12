# Snapchat Organizer Desktop - Alpha Testing Guide

**Version:** 1.0.0-alpha  
**Last Updated:** January 12, 2026

Welcome to the alpha testing phase of **Snapchat Organizer Desktop**! Thank you for being an early tester. Your feedback will help shape this application into the best tool for organizing Snapchat memories and chat media.

---

## 📋 Table of Contents

1. [What is Snapchat Organizer Desktop?](#what-is-snapchat-organizer-desktop)
2. [Installation](#installation)
3. [Quick Start Guide](#quick-start-guide)
4. [Features Overview](#features-overview)
5. [How to Use Each Tab](#how-to-use-each-tab)
6. [Troubleshooting](#troubleshooting)
7. [Providing Feedback](#providing-feedback)
8. [Known Limitations](#known-limitations)

---

## What is Snapchat Organizer Desktop?

Snapchat Organizer Desktop is a cross-platform application that helps you:

✅ **Download** Snapchat memories from your data export  
✅ **Organize** chat media by person/conversation  
✅ **Clean up** duplicate files and verify image integrity  
✅ **Fix** timestamps and organize files by year  
✅ **Convert** timezones (coming soon)  
✅ **Apply** custom overlays (coming soon)

All processing is done **locally on your computer** - your data never leaves your device.

---

## Installation

### Prerequisites

- **Python 3.11 or higher** - [Download Python](https://www.python.org/downloads/)
- **macOS, Windows, or Linux** operating system
- **Internet connection** (for initial setup only)

### Step-by-Step Installation

1. **Download the application**
   ```bash
   # If you received a ZIP file, extract it
   # If you have Git access:
   git clone https://github.com/M0hammedHaris/snapchat-organizer-desktop.git
   cd snapchat-organizer-desktop
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv .venv
   ```

3. **Activate the virtual environment**
   
   **On macOS/Linux:**
   ```bash
   source .venv/bin/activate
   ```
   
   **On Windows:**
   ```bash
   .venv\Scripts\activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application**
   ```bash
   python src/main.py
   ```

That's it! The application should launch and show you a welcome screen.

---

## Quick Start Guide

### First Time Launch

When you first launch the application:

1. A **Help dialog** will automatically appear with step-by-step instructions
2. Read through the three tabs: **Download Data**, **Prepare Data**, and **Tips & Tricks**
3. The app defaults to the **Download** tab for easy access to memory downloads

### Getting Your Snapchat Data

Before using this app, you need to download your Snapchat data:

1. Open Snapchat on your phone
2. Go to **Settings** (gear icon) → **My Data**
3. Scroll down and tap **Submit Request**
4. Select **All data** or specific data types
5. Wait for Snapchat to email you (usually 1-3 days)
6. Download the ZIP file from the email link
7. Extract the ZIP file to a folder on your computer

---

## Features Overview

### 📥 Download Tab

Download Snapchat memories from your `memories_history.html` export file.

**Key Features:**
- Bulk download with configurable delay
- Resume interrupted downloads
- Optional GPS metadata embedding
- Optional overlay application
- Timezone conversion
- Filter by year (2015-2025)
- Real-time progress tracking

### 📂 Organize Tab

Organize Snapchat chat media by person/conversation.

**Key Features:**
- 3-tier matching algorithm (Memory → JSON → Sender Name)
- Smart timestamp-based matching (5-minute default window)
- Confidence score for each match
- Detailed statistics and matching report
- Copy or move files (your choice)

### 🛠️ Tools Tab

Utility tools for managing your Snapchat media.

**Available Tools:**
- **Verify Files** - Check for corrupted images
- **Remove Duplicates** - Find and remove duplicate files using SHA256 hashing
- **Organize by Year** - Automatically sort files into year-based folders
- **Fix Timestamps** - Sync file timestamps with EXIF data
- **Convert Timezone** - *(Coming in Phase 2)*
- **Apply Overlays** - *(Coming in Phase 2)*

### ⚙️ Settings

Configure application preferences:

- **General**: Default folders, behavior options
- **Download**: Retry settings, timeouts, default options
- **Organize**: Time window, minimum match score, file operations
- **About**: Version info, license, copyright

---

## How to Use Each Tab

### 📥 Download Tab - Step by Step

1. **Select HTML File**
   - Click "Browse..." next to "HTML File"
   - Navigate to your extracted Snapchat data folder
   - Select `memories_history.html`

2. **Choose Output Folder**
   - Click "Browse..." next to "Output Folder"
   - Select where you want downloaded memories saved

3. **Configure Options** (optional)
   - **Delay**: Time between downloads (default: 2 seconds)
   - **Apply GPS**: Embed location data if available
   - **Apply Overlays**: Add Snapchat-style overlays
   - **Convert Timezone**: Adjust timestamps to your timezone
   - **Year Filters**: Uncheck years you don't want to download

4. **Start Download**
   - Click the blue **"Start Download"** button
   - Watch progress in real-time
   - Use **"Pause"** or **"Cancel"** if needed

5. **Resume Support**
   - If download is interrupted, just restart it
   - The app will skip already downloaded files

**Tips:**
- Use a delay of 2-5 seconds to avoid overwhelming servers
- GPS and overlays significantly increase processing time
- Downloads can be resumed at any time

---

### 📂 Organize Tab - Step by Step

1. **Select Snapchat Export**
   - Click "Browse..." next to "Snapchat Export Folder"
   - Choose the folder containing `json/` and `html/` subfolders
   - The app will validate the folder structure

2. **Choose Output Folder**
   - Click "Browse..." next to "Output Folder"
   - Select where organized media should be saved

3. **Configure Matching Settings** (optional)
   - **Time Window**: Maximum time difference for matches (default: 300 seconds)
   - **Minimum Score**: Confidence threshold for matches (default: 50)
   - Adjust these for stricter or looser matching

4. **Start Organization**
   - Click the blue **"Start Organizing"** button
   - The app uses a 3-tier matching system:
     1. Memory metadata matching
     2. JSON chat history matching  
     3. Sender name fallback
   - Watch statistics update in real-time

5. **Review Results**
   - Check the statistics panel for:
     - Total files processed
     - Successfully matched files
     - Unmatched files
     - Files organized by person
   - A detailed matching report is saved in the output folder

**Tips:**
- Larger time windows find more matches but may have lower accuracy
- Higher minimum scores mean fewer but more confident matches
- Always review the matching report after organization

---

### 🛠️ Tools Tab - Step by Step

1. **Select Folder**
   - Click "Browse..." to select the folder containing your media files

2. **Choose a Tool** (click any button)

   **Verify Files:**
   - Scans all images for corruption
   - Reports damaged files with detailed error messages
   - Safe operation - doesn't modify files

   **Remove Duplicates:**
   - Uses SHA256 hashing to find identical files
   - Keeps one copy, moves duplicates to `_duplicates/` folder
   - Shows how much space was saved

   **Organize by Year:**
   - Extracts year from EXIF data or file modification date
   - Creates year-based folders (e.g., `2021/`, `2022/`)
   - Automatically moves files into appropriate folders

   **Fix Timestamps:**
   - Reads EXIF DateTimeOriginal from images
   - Sets file modification time to match EXIF date
   - Useful for proper chronological sorting

3. **Monitor Progress**
   - Watch the progress bar and file count
   - Read detailed statistics when complete
   - Use **"Cancel"** to stop long-running operations

**Tips:**
- Always backup your files before using destructive tools
- Run "Verify Files" first to identify corrupted media
- "Remove Duplicates" is safe - duplicates are moved, not deleted

---

## Troubleshooting

### Application Won't Start

**Problem:** Double-clicking doesn't launch the app

**Solutions:**
1. Make sure you're running from terminal with `python src/main.py`
2. Check Python version: `python --version` (must be 3.11+)
3. Verify virtual environment is activated (you should see `(.venv)` in terminal)
4. Reinstall dependencies: `pip install -r requirements.txt`

---

### "Invalid Snapchat Export" Error

**Problem:** Organize tab says export folder is invalid

**Solutions:**
1. Make sure the folder contains `json/` and/or `html/` subfolders
2. Check that `chat_history.json` exists in the `json/` folder
3. The folder should be the extracted ZIP from Snapchat, not the ZIP itself

---

### Downloads Are Very Slow

**Problem:** Download tab is taking too long

**Solutions:**
1. Increase the delay between requests (try 3-5 seconds)
2. Disable GPS embedding and overlays for faster downloads
3. Download specific years instead of all years
4. Check your internet connection speed
5. Snapchat's servers may be rate-limiting - pause and retry later

---

### Files Aren't Matching in Organize Tab

**Problem:** Low match count or many unmatched files

**Solutions:**
1. Increase the time window (try 600 seconds = 10 minutes)
2. Lower the minimum score (try 30-40 for more matches)
3. Make sure your Snapchat export includes `chat_history.json`
4. Check that media files have timestamps in their filenames

---

### Application Crashes or Freezes

**Problem:** App becomes unresponsive

**Solutions:**
1. Check logs in `~/.snapchat-organizer/logs/app.log`
2. Try processing smaller batches of files
3. Restart the application
4. Report the crash with logs (see Providing Feedback section)

---

## Providing Feedback

Your feedback is **crucial** for improving this application. Please report:

✅ **Bugs** - Crashes, errors, unexpected behavior  
✅ **Feature Requests** - What's missing or could be better  
✅ **Usability Issues** - Confusing UI, unclear instructions  
✅ **Performance Problems** - Slow operations, memory issues  
✅ **Success Stories** - What worked great for you!

### How to Report Issues

**Method 1: GitHub Issues** (Preferred)
1. Go to: [https://github.com/M0hammedHaris/snapchat-organizer-desktop/issues](https://github.com/M0hammedHaris/snapchat-organizer-desktop/issues)
2. Click **"New Issue"**
3. Provide:
   - Clear title describing the issue
   - Steps to reproduce the problem
   - Expected vs actual behavior
   - Screenshots (if applicable)
   - Log file: `~/.snapchat-organizer/logs/app.log`
   - Your OS and Python version

**Method 2: Direct Contact**
- Email: [Your Email]
- Include the same information as above

### What Makes a Good Bug Report?

**Bad Example:**
> "App doesn't work"

**Good Example:**
> "Download tab freezes when selecting a 20GB HTML file on macOS 14.1 with Python 3.11.5. 
> Error in log: [paste error]. Screenshot attached showing frozen progress bar."

---

## Known Limitations

This is an **alpha version**, so some limitations are expected:

### Current Limitations

1. **Timezone Conversion Tool** - Placeholder only (coming in Phase 2)
2. **Apply Overlays Tool** - Placeholder only (coming in Phase 2)
3. **Results Viewer** - No built-in viewer for organized files yet
4. **Large Files** - Very large exports (>100GB) may be slow
5. **Memory Usage** - Processing thousands of files can use significant RAM
6. **Undo Feature** - No undo for file operations (always backup!)

### Platform-Specific Notes

**macOS:**
- May need to allow app in System Preferences → Security & Privacy
- Works best on macOS 12 (Monterey) or later

**Windows:**
- Antivirus may flag the app (false positive)
- Use forward slashes in paths or double backslashes

**Linux:**
- Install Qt dependencies: `sudo apt install libxcb-xinerama0`
- Some distributions may need additional packages

---

## Testing Checklist

Please try to test these scenarios and report any issues:

### Download Tab
- [ ] Download memories from a real Snapchat HTML export
- [ ] Test pause/resume functionality
- [ ] Try different delay settings (1s, 2s, 5s)
- [ ] Test year filters (select only specific years)
- [ ] Cancel a download midway

### Organize Tab
- [ ] Organize real chat media with JSON and HTML
- [ ] Adjust time window and minimum score
- [ ] Verify matching report accuracy
- [ ] Try copy vs move file operations

### Tools Tab
- [ ] Run "Verify Files" on various image formats
- [ ] Use "Remove Duplicates" on a folder with known duplicates
- [ ] Test "Organize by Year" with files from multiple years
- [ ] Run "Fix Timestamps" on images with EXIF data

### Settings & UI
- [ ] Change settings and verify they persist after restart
- [ ] Test keyboard shortcuts (F1 for help, Ctrl+, for settings)
- [ ] Try resizing the window
- [ ] Test "Restore Defaults" in settings

### Edge Cases
- [ ] Very large files (>100MB)
- [ ] Folders with 1000+ files
- [ ] Corrupted or invalid input files
- [ ] Special characters in filenames or paths

---

## FAQ

### Q: Is my data sent anywhere?

**A:** No! All processing happens locally on your computer. No data is uploaded to any server.

---

### Q: Can I use this on multiple computers?

**A:** Yes! Just install the app on each computer. Settings are stored locally per machine.

---

### Q: What file formats are supported?

**A:** 
- **Images:** JPG, PNG, WEBP, GIF, HEIC
- **Videos:** MP4, MOV, AVI, MKV, WEBM

---

### Q: Will this work with other social media exports?

**A:** Currently only Snapchat is supported. Other platforms may be added in the future.

---

### Q: How long does organization take?

**A:** Depends on file count:
- 100 files: ~1-2 minutes
- 1,000 files: ~5-10 minutes
- 10,000 files: ~30-60 minutes

---

### Q: What happens to unmatched files?

**A:** They're placed in an `_unmatched/` folder in your output directory. You can manually organize these later.

---

## Next Steps

After testing:

1. ✅ Fill out the testing checklist above
2. ✅ Report any bugs or issues you find
3. ✅ Share feature requests and suggestions
4. ✅ Tell us what you loved!

---

## Contact & Support

- **Email:** [Your Email]
- **GitHub:** [https://github.com/M0hammedHaris/snapchat-organizer-desktop](https://github.com/M0hammedHaris/snapchat-organizer-desktop)
- **Issues:** [https://github.com/M0hammedHaris/snapchat-organizer-desktop/issues](https://github.com/M0hammedHaris/snapchat-organizer-desktop/issues)

---

## License

Snapchat Organizer Desktop is proprietary software.  
© 2026 Mohammed Haris. All Rights Reserved.

---

**Thank you for being an alpha tester! Your feedback will make this app amazing. 🚀**
