# Project Structure

## Directory Organization

```
snapchat-organizer-desktop/
├── src/                           # Source code
│   ├── main.py                    # Application entry point
│   ├── gui/                       # UI components (PySide6)
│   │   ├── main_window.py         # Main window with tabs
│   │   ├── download_tab.py        # Download memories tab
│   │   ├── organize_tab.py        # Organize chat media tab
│   │   ├── tools_tab.py           # Quick tools tab
│   │   ├── progress_widget.py     # Reusable progress display
│   │   ├── settings_dialog.py     # Settings configuration
│   │   └── help_dialog.py         # Help system
│   ├── core/                      # Business logic
│   │   ├── downloader.py          # Memory downloader
│   │   ├── organizer.py           # Chat media organizer
│   │   ├── tools_core.py          # Tools functionality
│   │   └── *_worker.py            # QThread workers
│   ├── license/                   # License management (Phase 2)
│   └── utils/                     # Utilities
│       ├── config.py              # App configuration & constants
│       ├── logger.py              # Logging setup
│       └── theme.py               # Theme management
├── resources/                     # Static resources
│   ├── icons/                     # App icons (PNG format)
│   ├── images/                    # UI images
│   └── styles/                    # Qt stylesheets (QSS)
├── tests/                         # Unit tests
├── docs/                          # Documentation
├── scripts/                       # Build scripts
└── requirements.txt               # Python dependencies
```

## Architecture Patterns

### GUI Architecture
- **Main Window:** Tabbed interface with three primary tabs
- **Worker Threads:** All long-running operations use QThread workers
- **Progress Tracking:** Reusable progress widget for all operations
- **Settings:** Centralized configuration with persistent storage

### Core Logic Separation
- **GUI Layer:** PySide6 widgets in `src/gui/`
- **Business Logic:** Core functionality in `src/core/`
- **Workers:** Background processing in `*_worker.py` files
- **Utilities:** Shared utilities in `src/utils/`

### Configuration Management
- **Constants:** Defined in `src/utils/config.py`
- **Feature Flags:** Tier-based feature access control
- **Settings:** JSON-based user preferences
- **Paths:** Centralized path management

## File Naming Conventions

### Python Files
- **Modules:** `snake_case.py`
- **Classes:** `PascalCase` (e.g., `MainWindow`)
- **Functions:** `snake_case()`
- **Constants:** `UPPER_SNAKE_CASE`

### Resource Files
- **Icons:** `tab_*.png`, `icon.png`
- **Styles:** `light.qss`, `dark.qss`
- **Documentation:** `UPPER_CASE.md` for project docs, `lower_case.md` for feature docs

## Import Structure

### Path Setup
```python
# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
```

### Import Patterns
```python
# PySide6 imports
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QIcon

# Internal imports
from src.utils.config import APP_NAME, APP_VERSION
from src.utils.logger import get_logger
from src.core.downloader import MemoryDownloader
```

## Threading Model

- **Main Thread:** GUI operations only
- **Worker Threads:** All file I/O, network requests, and processing
- **Signals/Slots:** Communication between threads
- **Progress Updates:** Regular progress signals to update UI

## Configuration Files

- **Application Config:** `~/.snapchat-organizer/config.json`
- **Database:** `~/.snapchat-organizer/organizer.db`
- **Logs:** `~/.snapchat-organizer/logs/`
- **Cache:** `~/.snapchat-organizer/cache/`