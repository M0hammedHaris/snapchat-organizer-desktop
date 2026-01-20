---
inclusion: always
---

# Project Structure & Architecture Guide

## Critical Directory Structure

When working with this codebase, ALWAYS respect this structure:

```
src/
├── main.py                    # Entry point - DO NOT modify without review
├── gui/                       # PySide6 UI components ONLY
│   ├── main_window.py         # Main tabbed interface
│   ├── *_tab.py              # Tab implementations (download, organize, tools)
│   ├── *_dialog.py           # Modal dialogs (settings, help)
│   └── progress_widget.py     # Reusable progress component
├── core/                      # Business logic - NO GUI code here
│   ├── downloader.py          # Memory download logic
│   ├── organizer.py           # Chat media organization
│   ├── tools_core.py          # Tools functionality
│   └── *_worker.py           # QThread workers for background tasks
├── utils/                     # Shared utilities
│   ├── config.py              # Constants & configuration (READ FIRST)
│   ├── logger.py              # Logging setup
│   └── theme.py               # UI theming
└── license/                   # License system (Phase 2 - minimal changes)
```

## Mandatory Architecture Rules

### 1. Strict Layer Separation
- **GUI layer** (`src/gui/`): PySide6 widgets, UI logic, user interactions
- **Core layer** (`src/core/`): Business logic, data processing, algorithms
- **Utils layer** (`src/utils/`): Shared utilities, configuration, logging
- **NEVER** import GUI components in core modules
- **NEVER** put business logic in GUI modules

### 2. Threading Requirements (CRITICAL)
- **Main thread**: GUI operations ONLY - never block with I/O or processing
- **Worker threads**: ALL file operations, network requests, heavy processing
- **Communication**: Use Qt signals/slots between threads - NEVER direct calls
- **Pattern**: Create `*_worker.py` files inheriting from `QObject`, use `moveToThread()`

### 3. Configuration Access
- **ALWAYS** read constants from `src/utils/config.py` first
- **NEVER** hardcode paths, limits, or feature flags
- Use `get_logger(__name__)` for all logging - NO print statements

## File Creation Rules

### New Python Files
- **GUI components**: Place in `src/gui/`, suffix with purpose (`*_tab.py`, `*_dialog.py`)
- **Business logic**: Place in `src/core/`, descriptive names (`*_processor.py`)
- **Background work**: Create `*_worker.py` in `src/core/` with QObject pattern
- **Utilities**: Add to `src/utils/` only if truly shared across modules

### Tests
- **Location**: `tests/` directory (NOT inside `src/`)
- **Naming**: `test_*.py` matching source structure
- **Structure**: Mirror `src/` hierarchy in `tests/`

### Documentation
- **Feature docs**: `docs/[feature_name]/` (lowercase, hyphens)
- **Project docs**: Root level (UPPERCASE.md)

## Import Patterns (Enforce Strictly)

```python
# Standard library first
from pathlib import Path
from typing import Optional, List

# Third-party second
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import QThread, Signal, QObject

# Internal imports last - use absolute imports from src/
from src.utils.config import APP_NAME, SUPPORTED_FORMATS
from src.utils.logger import get_logger
from src.core.organizer import MediaOrganizer
```

## Worker Thread Pattern (Use This Exactly)

```python
# In src/core/*_worker.py
class ProcessWorker(QObject):
    progress = Signal(int, str)  # percentage, message
    finished = Signal(dict)      # results
    error = Signal(str)          # error message
    
    def __init__(self, data):
        super().__init__()
        self.data = data
    
    @Slot()
    def process(self):
        try:
            # Do work here
            self.progress.emit(50, "Processing...")
            result = self.do_work()
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

# In GUI code
def start_processing(self):
    self.thread = QThread()
    self.worker = ProcessWorker(data)
    self.worker.moveToThread(self.thread)
    
    # Connect signals
    self.worker.progress.connect(self.update_progress)
    self.worker.finished.connect(self.on_finished)
    self.worker.error.connect(self.on_error)
    self.thread.started.connect(self.worker.process)
    
    self.thread.start()
```

## Configuration & State Management

- **User config**: `~/.snapchat-organizer/config.json`
- **Database**: `~/.snapchat-organizer/organizer.db` (SQLAlchemy)
- **Logs**: `~/.snapchat-organizer/logs/`
- **Cache**: `~/.snapchat-organizer/cache/`

Access paths through `src/utils/config.py` constants, never hardcode.

## Error Handling Strategy

1. **User errors**: Show QMessageBox with friendly message
2. **Recoverable errors**: Log warning, continue operation
3. **Critical errors**: Log exception, show dialog, graceful shutdown
4. **Always** use proper exception types, never bare `except:`