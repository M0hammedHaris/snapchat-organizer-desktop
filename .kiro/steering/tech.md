# Technology Stack

## Core Technologies

- **Language:** Python 3.11+
- **GUI Framework:** PySide6 (Qt for Python) - LGPL licensed
- **Database:** SQLAlchemy 2.0 + SQLite
- **Image Processing:** Pillow 10.0+
- **Video Processing:** FFmpeg (bundled)
- **Metadata:** ExifTool (bundled)

## Key Dependencies

### GUI & Application
- `PySide6>=6.6.0` - Desktop GUI framework
- `sqlalchemy>=2.0.0` - ORM for SQLite (license, settings, history)

### Media Processing
- `Pillow>=10.0.0` - Image manipulation for overlay compositing
- `piexif>=1.1.3` - EXIF metadata manipulation

### Networking & Parsing
- `requests>=2.31.0` - HTTP requests for downloading memories
- `beautifulsoup4>=4.12.0` - HTML parsing for memories_history.html
- `lxml>=4.9.0` - XML/HTML parser (faster than html.parser)

### Security & Utilities
- `cryptography>=41.0.0` - AES encryption for license storage
- `timezonefinder>=6.0.0` - GPS coordinate → timezone conversion
- `pytz>=2023.3` - Timezone database

## Build System

### Development Commands

```bash
# Setup virtual environment
python3 -m venv .env
source .env/bin/activate  # macOS/Linux
# .env\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Run application
python src/main.py
```

### Code Quality

```bash
# Format code
black src/ tests/

# Check linting
flake8 src/ tests/

# Type checking
mypy src/

# Run tests
pytest tests/
pytest --cov=src tests/  # with coverage
```

### Building Executables

```bash
# macOS build
./scripts/build_macos.sh

# Manual PyInstaller build
pyinstaller snapchat-organizer.spec --clean --noconfirm

# Code signing (macOS)
codesign --force --deep --sign - "dist/Snapchat Organizer.app"
```

## External Tools

- **FFmpeg** - Video overlay compositing (https://ffmpeg.org/)
- **ExifTool** - GPS/EXIF metadata handling (https://exiftool.org/)

These are auto-detected at runtime or bundled with the application.

## Development Environment

- **Python Version:** 3.11+ required
- **IDE:** Any Python IDE with PySide6 support
- **Platform:** Cross-platform (macOS, Windows, Linux)
- **Git Workflow:** Conventional commits with feature branches