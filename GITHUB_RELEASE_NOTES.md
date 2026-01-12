# Snapchat Organizer Desktop v1.0.0-alpha

Professional desktop app for organizing Snapchat memories and chat media.

---

## ✨ Latest Update (January 12, 2026)

- ✅ **Fixed:** macOS Gatekeeper warnings (app now code-signed)
- ✅ **Improved:** First-launch experience with better instructions
- ✅ **Added:** Comprehensive installation documentation

**macOS users:** If you still see a security warning, use the right-click method below. This is normal for apps not distributed through the App Store.

---

## 🍎 macOS Installation (Important!)

### Quick Start (3 Steps)
1. **Download** `Snapchat-Organizer-1.0.0-alpha.dmg` below
2. **Open** the DMG and drag app to Applications folder
3. **Right-click** the app in Applications → Choose **"Open"** → Click **"Open"**

That's it! The app will now run normally. ✅

### Alternative: Terminal Command
If the right-click method doesn't work, use this:
```bash
xattr -cr "/Applications/Snapchat Organizer.app"
```
Then double-click to open.

### Why This Extra Step?
The app is code-signed but not Apple notarized (requires $99/year Developer account). This is standard for indie/open-source apps. The app is completely safe and processes everything locally on your Mac.

**Detailed Guide:** [MACOS_INSTALLATION.md](https://github.com/M0hammedHaris/snapchat-organizer-desktop/blob/main/docs/releases/alpha/MACOS_INSTALLATION.md)

---

## 📦 Downloads

Choose the file for your operating system:

### macOS (Apple Silicon & Intel)
- **File:** Snapchat-Organizer-1.0.0-alpha.dmg
- **Size:** ~120 MB
- **Requirements:** macOS 11.0 (Big Sur) or later
- **Installation:** See instructions above ☝️

### Windows (Coming Soon)
- Windows build will be available in next release
- For now, run from source (see Development section)

### Linux (Coming Soon)
- Linux build will be available in next release
- For now, run from source (see Development section)

---

## ✨ Features

✅ **Download memories** from Snapchat HTML exports  
✅ **Organize chat media** by contact with intelligent 3-tier matching  
✅ **Remove duplicates** using SHA256 hashing (99%+ accuracy)  
✅ **Verify file integrity** to detect corrupted files  
✅ **Organize by year** using EXIF metadata  
✅ **Fix timestamps** by syncing EXIF to file modification times  
✅ **Integrated help system** with F1 shortcut  
✅ **100% private** - all processing happens locally

---

## 🚀 Quick Start

### First Time Users

1. **Get your Snapchat data:**
   - Open Snapchat app → Settings → My Data → Submit Request
   - Wait for email from Snapchat (usually 24 hours)
   - Download your data export (ZIP file)

2. **Launch the app:**
   - Press **F1** or click Help menu for detailed guide
   - Default tab is "Download" - ready to go!

3. **Download memories:**
   - Select your Snapchat HTML file
   - Choose output folder
   - Click "Start Download"

4. **Organize chat media:**
   - Switch to "Organize" tab
   - Select chat media folder + JSON file
   - Choose output folder
   - Click "Start Organizing"

**Full Testing Guide:** [ALPHA_TESTING_GUIDE.md](https://github.com/M0hammedHaris/snapchat-organizer-desktop/blob/main/docs/releases/alpha/ALPHA_TESTING_GUIDE.md)

---

## 🐛 Known Issues & Limitations

- **macOS:** Requires right-click → Open on first launch (security feature)
- **Settings:** Persistence works but settings dialog needs polish
- **Progress:** Some operations may not show ETA (coming in next release)
- **Windows/Linux:** Standalone builds not yet available

---

## 💬 Feedback & Bug Reports

This is an **alpha release** - your feedback is crucial!

**Found a bug?** [Create an issue](https://github.com/M0hammedHaris/snapchat-organizer-desktop/issues/new)

**Questions?** Check the [Discussions](https://github.com/M0hammedHaris/snapchat-organizer-desktop/discussions)

---

## 🛠️ Development (Run from Source)

If you prefer to run from source code:

```bash
# Clone repository
git clone https://github.com/M0hammedHaris/snapchat-organizer-desktop.git
cd snapchat-organizer-desktop

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
python src/main.py
```

**Requirements:** Python 3.11 or higher

---

## 📄 License

**Proprietary License** - All Rights Reserved  
Copyright © 2026 Mohammed Haris

This software is licensed for personal use. You may not distribute, modify, reverse engineer, or copy this software without explicit permission.

---

## 🙏 Acknowledgments

- Original CLI inspiration: [snapchat-memory-downloader](https://github.com/shoeless03/snapchat-memory-downloader)
- Built with [PySide6](https://doc.qt.io/qtforpython-6/) (Qt for Python)
- Powered by [SQLAlchemy](https://www.sqlalchemy.org/) and [Pillow](https://pillow.readthedocs.io/)

---

**Release Date:** January 12, 2026  
**Version:** 1.0.0-alpha  
**Build:** Signed (ad-hoc)  
**Status:** Alpha Testing

**Thank you for testing! 🚀**
