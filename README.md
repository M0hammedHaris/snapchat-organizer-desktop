# 📸 Snapchat Organizer Desktop

> Professional desktop application for downloading and organizing Snapchat memories locally with overlay compositing, GPS metadata preservation, and timezone conversion.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![PySide6](https://img.shields.io/badge/GUI-PySide6-green.svg)](https://doc.qt.io/qtforpython-6/)
[![License: Proprietary](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)

---

## 🎯 Project Overview

**Status:** 🚧 MVP Development - Week 1 (~65% Complete)  
**Version:** 1.0.0-alpha  
**Repository:** https://github.com/M0hammedHaris/snapchat-organizer-desktop  
**License:** Proprietary - All Rights Reserved

### What It Does

Snapchat Organizer Desktop is an all-in-one solution that:

1. **Downloads memories** directly from Snapchat HTML exports
2. **Organizes chat media** by contact and date with 3-tier matching strategy
3. **Composites overlays** to recreate the original Snapchat look (stickers, text, filters)
4. **Preserves GPS metadata** with automatic timezone conversion
5. **Removes duplicates** with 99%+ accuracy
6. **Provides analytics** on your Snapchat usage patterns

### Key Features

✅ **User-friendly tabbed GUI** - No command-line knowledge required  
✅ **Progress tracking** - Real-time progress bars with ETA  
✅ **Resume capability** - Continue interrupted downloads/processing  
✅ **Smart matching** - Media ID → Single contact → Timestamp proximity  
✅ **100% private** - All processing happens locally, nothing uploaded  
✅ **Cross-platform** - Works on macOS, Windows, and Linux  

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

### Installation

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

---

## 📋 Development Roadmap

### MVP Features (Week 1-2) ✅ In Progress

- [x] Project structure setup
- [x] GitHub repository creation
- [x] Python environment configuration
- [x] Requirements.txt with dependencies
- [x] Copilot instructions and guidelines
- [ ] Main window with tabbed interface
- [ ] Download tab UI
- [ ] Organize tab UI
- [ ] Tools tab UI
- [ ] Progress widget (reusable)
- [ ] Background processing threads
- [ ] License dialog (trial mode)

### Phase 2 (Week 3) 🔜 Planned

- [ ] License key generation system
- [ ] Hardware fingerprinting
- [ ] Lemonsqueezy integration
- [ ] 7-day trial implementation
- [ ] SQLite database for licenses
- [ ] Device management UI

### Phase 3 (Week 4-5) 📅 Upcoming

- [ ] macOS app signing & notarization
- [ ] Windows code signing
- [ ] Bundle FFmpeg + ExifTool
- [ ] Auto-update system
- [ ] Crash reporting (Sentry)
- [ ] Comprehensive testing

### Phase 4+ (Week 6+) 🔮 Future

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
- Powered by [SQLAlchemy](https://www.sqlalchemy.org/) and [Pillow](https://pillow.readthedocs.io/)

---

**Last Updated:** January 12, 2026  
**Maintained by:** [@M0hammedHaris](https://github.com/M0hammedHaris)
