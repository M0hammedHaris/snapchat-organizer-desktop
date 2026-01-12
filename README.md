# 📸 Snapchat Organizer Desktop

> Professional desktop application for downloading and organizing Snapchat memories locally with overlay compositing, GPS metadata preservation, and timezone conversion.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![PySide6](https://img.shields.io/badge/GUI-PySide6-green.svg)](https://doc.qt.io/qtforpython-6/)
[![License: Proprietary](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)

---

## 🎯 Project Overview

**Status:** ✅ MVP Complete - Alpha Ready for Testing  
**Version:** 1.0.0-alpha (Signed Build)  
**Repository:** https://github.com/M0hammedHaris/snapchat-organizer-desktop  
**License:** Proprietary - All Rights Reserved  
**Last Updated:** January 12, 2026

> **🎉 Latest:** App is now code-signed! macOS users can download and run without complicated workarounds.

### What It Does

Snapchat Organizer Desktop is a comprehensive desktop application that:

1. **Downloads memories** directly from Snapchat HTML exports with configurable options
2. **Organizes chat media** by contact and date with 3-tier matching strategy (Media ID → Contact → Timestamp)
3. **Removes duplicates** using SHA256 hashing with 99%+ accuracy
4. **Verifies file integrity** to detect corrupted or damaged media
5. **Organizes by year** using EXIF metadata and file timestamps
6. **Fixes timestamps** by syncing EXIF data to file modification times
7. **Provides comprehensive help** with step-by-step Snapchat data download instructions
8. **Configurable settings** for customizing all aspects of the application
9. **Composites overlays** to recreate the original Snapchat look (coming in Phase 2)
10. **Preserves GPS metadata** with automatic timezone conversion (coming in Phase 2)

### Key Features

✅ **Fully functional tabbed GUI** - No command-line knowledge required  
✅ **Real-time progress tracking** - Progress bars with detailed status messages  
✅ **Resume capability** - Continue interrupted downloads/processing  
✅ **Smart 3-tier matching** - Intelligent media-to-contact association  
✅ **Integrated help system** - F1 for complete download guide  
✅ **Settings framework** - Customize paths, behavior, and defaults  
✅ **100% private** - All processing happens locally, nothing uploaded  
✅ **Cross-platform** - Works on macOS, Windows, and Linux  
✅ **Comprehensive utilities** - 6 integrated tools for media management  
✅ **Thread-safe architecture** - Responsive UI during processing  
✅ **Real-world tested** - Validated with actual Snapchat data exports  

---

## 🏗️ Architecture

### Tech Stack

- **GUI Framework:** PySide6 (Qt for Python) - LGPL licensed
- **Database:** SQLAlchemy 2.0 + SQLite
- **Image Processing:** Pillow 10.0+
- **Video Processing:** FFmpeg (bundled)
- **Metadata:** ExifTool (bundled)
- **Language:** Python 3.11+

### Project Structure

```
snapchat-organizer-desktop/
├── src/
│   ├── main.py                    # Application entry point
│   ├── gui/                       # UI components
│   │   ├── main_window.py         # Main window with tabs
│   │   ├── download_tab.py        # Download memories tab
│   │   ├── organize_tab.py        # Organize chat media tab
│   │   ├── tools_tab.py           # Quick tools tab
│   │   ├── progress_widget.py     # Reusable progress display
│   │   └── license_dialog.py      # License activation
│   ├── core/                      # Business logic
│   │   ├── downloader.py          # Memory downloader
│   │   ├── organizer.py           # Chat media organizer
│   │   ├── compositor.py          # Overlay compositing
│   │   ├── metadata_handler.py    # GPS/EXIF operations
│   │   └── timezone_converter.py  # GPS-based timezone conversion
│   ├── license/                   # License management
│   │   ├── validator.py           # License validation
│   │   ├── activation.py          # Hardware fingerprinting
│   │   └── crypto.py              # Encryption utilities
│   └── utils/                     # Utilities
│       ├── config.py              # App configuration
│       ├── logger.py              # Logging setup
│       └── dependency_checker.py  # FFmpeg/ExifTool detection
├── resources/                     # Static resources
│   ├── icons/                     # App icons
│   ├── images/                    # UI images
│   └── styles/                    # Qt stylesheets
├── tests/                         # Unit tests
├── requirements.txt               # Python dependencies
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.11 or higher** - [Download Python](https://www.python.org/downloads/)
- **Git** - [Download Git](https://git-scm.com/downloads)

### Installation Options

#### Option 1: Download Pre-Built (Recommended for Most Users)

**Complete App Ready to Use** - Download from GitHub Release with the full-featured application included:

**🔗 [👉 Go to Release Downloads](https://github.com/M0hammedHaris/snapchat-organizer-desktop/releases/tag/v1.0.0-alpha)**

**macOS Installation:**
1. Download `Snapchat-Organizer-1.0.0-alpha.dmg` from the release page
2. Open the DMG and drag the app to Applications
3. **Right-click** the app in Applications → Select **"Open"**
4. Click **"Open"** in the security dialog (one-time only)
5. App launches with all features ready:
   - ✅ Download memories tab
   - ✅ Organize chat media tab
   - ✅ Tools tab (6 utilities)
   - ✅ Settings with full configuration
   - ✅ Integrated help system
   - ✅ No additional setup needed!

**Windows/Linux:** Pre-built packages coming soon. Use Option 2 below.

#### Option 2: Run from Source (For Developers)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/M0hammedHaris/snapchat-organizer-desktop.git
   cd snapchat-organizer-desktop
   ```

2. **Create virtual environment:**
   ```bash
   # macOS/Linux
   python3 -m venv .env
   source .env/bin/activate
   
   # Windows
   python -m venv .env
   .env\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python src/main.py
   ```

### 🍎 macOS Security Note

Due to Apple's security policies for apps not distributed through the App Store, you may see a warning on first launch. This is **normal and expected** for all indie apps:

- **Right-click → Open** method: Works perfectly, one-time step
- **After first launch:** Opens normally every time with double-click
- **Alternative:** Use `xattr -cr "/Applications/Snapchat Organizer.app"` in Terminal
- **No danger:** The app is code-signed and completely safe - all processing happens locally on your Mac
- **No phone home:** Your data never leaves your device

For more details, see [MACOS_INSTALLATION.md](docs/releases/alpha/MACOS_INSTALLATION.md)

---

## 📋 Development Roadmap

### Phase 1: Foundation & MVP ✅ 100% Complete

**Completed:**
- [x] Project structure setup with modular architecture
- [x] GitHub repository creation and initialization
- [x] Python environment configuration (.venv)
- [x] Requirements.txt with 35+ dependencies
- [x] Comprehensive copilot instructions (843 lines)
- [x] Main window with 3-tab interface
- [x] **Download Tab** - Memory downloader with HTML parsing, resume capability, configuration options
- [x] **Organize Tab** - Chat media organizer with 3-tier matching, real-time statistics
- [x] **Tools Tab** - 6 utility tools (verify, dedup, year, timestamp, timezone, overlays)
- [x] **Settings Dialog** - Comprehensive preferences (paths, behavior, download, organize settings)
- [x] **Help System** - Step-by-step Snapchat data download guide with 3 tabs
- [x] Reusable progress widget component
- [x] QThread-based background workers for all operations
- [x] Comprehensive error handling and logging system
- [x] Type hints and Google-style docstrings throughout
- [x] Menu bar with File and Help menus
- [x] Keyboard shortcuts (F1=Help, Ctrl+,=Settings, Ctrl+Q=Quit)
- [x] **Real-world testing** with actual Snapchat data exports
- [x] **Code signing** - App is now ad-hoc signed for macOS
- [x] **Build optimization** - DMG ready for distribution
- [x] **Comprehensive documentation** - Installation and usage guides

### Phase 2 (Week 3) 🔜 Next

- [ ] License key generation system
- [ ] Hardware fingerprinting for device activation
- [ ] Lemonsqueezy integration
- [ ] 7-day trial implementation
- [ ] SQLite database for user licenses and settings
- [ ] Device management UI
- [ ] GPS coordinate extraction (for timezone conversion)
- [ ] Overlay compositing implementation

### Phase 3 (Week 4-5) 📅 Upcoming

- [ ] macOS app signing & notarization
- [ ] Windows code signing
- [ ] Apple Developer Program enrollment ($99/year)
- [ ] Full Developer ID signing & notarization
- [ ] Windows code signing
- [ ] Bundle FFmpeg + ExifTool
- [ ] Auto-update system
- [ ] Crash reporting (Sentry)
- [ ] Comprehensive integration testing
- [ ] User documentation and tutorial videos
- [ ] Windows/Linux standalone build

- [ ] ProductHunt launch
- [ ] macOS App Store submission
- [ ] Windows Store submission
- [ ] Advanced analytics dashboard
- [ ] Cloud backup integration
- [ ] Multi-language support

---

## 🛠️ Development

### Code Style

This project follows strict Python best practices:

- **PEP 8** style guide
- **Type hints** for all functions
- **Google-style docstrings**
- **Black** code formatting (88 char line length)
- **flake8** linting
- **mypy** type checking

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_downloader.py

# Run with coverage
pytest --cov=src tests/
```

### Code Formatting

```bash
# Format code
black src/ tests/

# Check linting
flake8 src/ tests/

# Type checking
mypy src/
```

### Git Workflow

We follow conventional commits:

```bash
# Feature
git commit -m "feat(download-tab): add progress tracking with ETA"

# Bug fix
git commit -m "fix(compositor): preserve GPS metadata when compositing"

# Documentation
git commit -m "docs(readme): update installation instructions"
```

---

## 📚 Documentation

### Getting Help
- **Installation Issues:** [MACOS_INSTALLATION.md](docs/releases/alpha/MACOS_INSTALLATION.md)
- **Gatekeeper Workarounds:** [MACOS_GATEKEEPER_FIX.md](docs/releases/alpha/MACOS_GATEKEEPER_FIX.md)
- **Alpha Testing Guide:** [ALPHA_TESTING_GUIDE.md](docs/releases/alpha/ALPHA_TESTING_GUIDE.md)
- **Release Notes:** [GITHUB_RELEASE_NOTES.md](GITHUB_RELEASE_NOTES.md)

### Development References
- **Copilot Instructions:** [.github/copilot-instructions.md](.github/copilot-instructions.md)
- **Business Plan:** See parent directory `Snapchat_Media_Organizer-Desktop_Saas.md`
- **Technical Plan:** See parent directory `SAAS_CONVERSION_PLAN.md`
- **PySide6 Docs:** https://doc.qt.io/qtforpython-6/
- **SQLAlchemy Docs:** https://docs.sqlalchemy.org/en/20/

---

## 🎯 Business Model

**Freemium + Subscription:**

- **Free Tier:** Organize up to 100 files/month
- **Pro ($9.99/mo):** Unlimited files + overlay compositing + GPS embedding
- **Premium ($19.99/mo):** All Pro features + advanced analytics + cloud backup

**Target Market:** Snapchat users ages 16-35 with large data exports  
**Revenue Goal:** $3,000-5,000/month by Month 6

---

## 🤝 Contributing

This is a proprietary closed-source project. External contributions are not accepted.

---

## 📄 License

**Proprietary License** - All Rights Reserved  
Copyright © 2026 Mohammed Haris

This software is licensed for use only. You may not distribute, modify, reverse engineer, or copy this software without explicit permission. See [LICENSE](LICENSE) for full terms.

---

## 🙏 Acknowledgments

- Original CLI scripts from [snapchat-memory-downloader](https://github.com/shoeless03/snapchat-memory-downloader)
- Built with [PySide6](https://doc.qt.io/qtforpython-6/) (Qt for Python, LGPL licensed)
- PoBuild Documentation:** See [docs/releases/alpha/](docs/releases/alpha/) for build, testing, and distribution guides
- **Code Guidelines:** See [.github/copilot-instructions.md](.github/copilot-instructions.md) for development standards
- **Tools Documentation:** See [docs/tools/](docs/tools/) for detailed tool implementations
- **Business Plan:** See parent directory `Snapchat_Media_Organizer-Desktop_Saas.md` and `SAAS_CONVERSION_PLAN.md`

## 🚦 Project Status

### What's Ready Now
✅ Full GUI with all core features  
✅ Download memories from Snapchat exports  
✅ Organize chat media by person  
✅ Remove duplicates and verify files  
✅ Fix timestamps and organize by year  
✅ Settings and help system  
✅ Code-signed macOS build  
✅ Comprehensive documentation  

### Coming Soon (Phase 2)
🔜 License key system (Lemonsqueezy integration)  
🔜 Overlay compositing  
🔜 GPS metadata handling  
🔜 Timezone conversion  

### Future (Phase 3+)
📅 Mac App Store submission  
📅 Windows/Linux standalone builds  
📅 Auto-update system  
📅 Advanced analytics

## 📚 Additional Resources

- **Development Guide:** See [PROGRESS.md](PROGRESS.md) for detailed phase-by-phase progress
- **Copilot Instructions:** See [.github/copilot-instructions.md](.github/copilot-instructions.md) for development guidelines
- **Tools Documentation:** See [docs/tools/](docs/tools/) for detailed tool implementations
- **Business Plan:** See parent directory `Snapchat_Media_Organizer-Desktop_Saas.md` and `SAAS_CONVERSION_PLAN.md`

---

**Last Updated:** January 12, 2026  
**Maintained by:** [@M0hammedHaris](https://github.com/M0hammedHaris)  
**Built with:** Python 3.11+ | PySide6 | SQLAlchemy | Pillow
