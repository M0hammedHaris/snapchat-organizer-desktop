---
inclusion: always
---

# Technology Stack & Development Guidelines

## Core Technology Requirements

**CRITICAL**: This is a Python desktop application. Always use these exact technologies:

- **Language**: Python 3.11+ (REQUIRED - do not suggest other languages)
- **GUI Framework**: PySide6 (Qt for Python) - LGPL licensed (REQUIRED - do not suggest alternatives)
- **Database**: SQLAlchemy 2.0 + SQLite for local storage
- **Image Processing**: Pillow 10.0+ for image manipulation
- **Video Processing**: FFmpeg (bundled with app)
- **Metadata**: ExifTool (bundled with app)

## Essential Dependencies (Use These Exact Versions)

### Core Application Stack
- `PySide6>=6.6.0` - Desktop GUI framework (Qt widgets, signals/slots)
- `sqlalchemy>=2.0.0` - ORM for SQLite (license system, settings, history)

### Media Processing Stack
- `Pillow>=10.0.0` - Image manipulation and overlay compositing
- `piexif>=1.1.3` - EXIF metadata reading/writing

### Data Processing Stack
- `requests>=2.31.0` - HTTP requests for memory downloads
- `beautifulsoup4>=4.12.0` - HTML parsing for memories_history.html
- `lxml>=4.9.0` - Fast XML/HTML parser (preferred over html.parser)

### Utility Stack
- `cryptography>=41.0.0` - AES encryption for license storage
- `timezonefinder>=6.0.0` - GPS coordinate to timezone conversion
- `pytz>=2023.3` - Timezone database and handling

## Development Workflow Commands

### Environment Setup (ALWAYS Use Virtual Environment)
```bash
# Create and activate virtual environment
python3 -m venv .env
source .env/bin/activate  # macOS/Linux
# .env\Scripts\activate   # Windows

# Install all dependencies
pip install -r requirements.txt

# Run the application
python src/main.py
```

### Code Quality Tools (Run Before Commits)
```bash
# Format code (REQUIRED before commits)
black src/ tests/

# Check code style and errors
flake8 src/ tests/

# Type checking (REQUIRED for new code)
mypy src/

# Run test suite
pytest tests/
pytest --cov=src tests/  # with coverage report
```

### Build & Distribution
```bash
# Build macOS executable
./scripts/build_macos.sh

# Manual PyInstaller build (cross-platform)
pyinstaller snapchat-organizer.spec --clean --noconfirm

# Code signing for macOS distribution
codesign --force --deep --sign - "dist/Snapchat Organizer.app"
```

## External Tool Dependencies

**IMPORTANT**: These tools are bundled with the application and auto-detected at runtime:

- **FFmpeg**: Video overlay compositing and processing
- **ExifTool**: GPS/EXIF metadata extraction and manipulation

Do not assume these are installed on user systems - the app handles detection and bundling.

## AI Assistant Guidelines

### When Writing Code
1. **Always use PySide6** for GUI components (QWidget, QVBoxLayout, etc.)
2. **Use SQLAlchemy 2.0 syntax** for database operations
3. **Import from exact package names** listed above
4. **Follow the threading patterns** defined in structure.md
5. **Use type hints** for all function parameters and returns

### When Suggesting Dependencies
- **NEVER suggest alternatives** to the core stack (React, Electron, etc.)
- **ALWAYS check requirements.txt** before adding new dependencies
- **Prefer built-in Python libraries** when possible
- **Use exact version constraints** from the lists above

### When Running Commands
- **Always activate virtual environment** first
- **Use the exact commands** listed in this document
- **Run code quality tools** before suggesting commits
- **Test on the target platform** (macOS primary, Windows secondary)

## Platform Support Priority

1. **Primary**: macOS (development and primary target)
2. **Secondary**: Windows (tested and supported)
3. **Tertiary**: Linux (basic compatibility)

Focus development and testing efforts on macOS first, then Windows compatibility.