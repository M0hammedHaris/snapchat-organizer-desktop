---
trigger: always_on
---

# Snapchat Organizer Desktop - Agent Instructions

## Project Overview
**Snapchat Organizer Desktop** - Cross-platform Python/PySide6 desktop app for organizing Snapchat media exports.

**License**: Proprietary (closed-source) - © 2026 Mohammed Haris

**Tech Stack**: Python 3.11+, PySide6, SQLAlchemy, Pillow, SQLite

**Key Features**: Parse Snapchat JSON exports, organize by person/conversation, apply EXIF metadata, remove duplicates, modern GUI

---

## 🧠 Memory Management - CRITICAL

### Always Read PROGRESS.md First
- Check completion status, current phase, known issues
- Identify next steps from "IN PROGRESS" section
- Review "Next Session Goals"

### Always Update PROGRESS.md After Changes
- Mark tasks completed with [x]
- Update progress percentages
- Record git commit SHAs
- Note blockers/issues

---

## Python Guidelines (PEP 8)

**Code Style**:
- Line length: 88 chars (Black)
- Indentation: 4 spaces
- Naming: `snake_case` (functions/vars), `PascalCase` (classes), `UPPER_CASE` (constants)
- Private: prefix with `_`

**Always Use**:
- Type hints for all functions
- Google-style docstrings
- Logging (not print)
- Context managers for files/DB
- Specific exception handling

**Import Order**: stdlib → third-party → local

```python
from pathlib import Path
from typing import Optional, Dict

def process_files(input_dir: Path, output_dir: Path) -> Dict[str, int]:
    """Process media files.
    
    Args:
        input_dir: Source directory
        output_dir: Destination directory
        
    Returns:
        Processing statistics
    """
    pass
```

---

## PySide6 Best Practices

**Signals/Slots**:
- Define signals as class attributes
- Use for thread-safe communication
- Never update GUI from background threads

**Threading**:
- Use QThread + moveToThread() for background work
- Emit signals to update GUI from workers

```python
from PySide6.QtCore import QObject, Signal, Slot, QThread

class Worker(QObject):
    progress = Signal(int, str)
    finished = Signal()
    
    @Slot()
    def process(self):
        # Work here
        self.progress.emit(50, "Processing...")
        self.finished.emit()
```

**Layouts**: Always use layouts (QVBoxLayout, QHBoxLayout, QGridLayout) - never fixed positioning

---

### Directory Structure
```
snapchat-organizer-desktop/
├── src/                    # Source code
│   ├── models/            # SQLAlchemy models
│   ├── ui/                # PySide6 UI components
│   ├── workers/           # Background workers
│   ├── utils/             # Utility functions
│   └── main.py            # Application entry point
├── tests/                 # Test suite (ALL test files go here: test_*.py)
│   ├── test_models/       # Model tests
│   ├── test_ui/           # UI component tests
│   └── integration/       # Integration tests
├── resources/             # Icons, images, stylesheets
├── docs/                  # Documentation (organized by feature)
│   ├── organizer/         # Organizer feature documentation
│   ├── downloader/        # Downloader feature documentation
│   └── BUILD-INSTRUCTIONS.md
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
└── LICENSE               # License file
```

**Rules**:
- ✅ Tests in `tests/` matching `src/` structure
- ✅ Docs in `docs/[feature_name]/`
- ❌ Never create tests in `src/`
- ❌ Never create docs in project root

---

## Error Handling

**Levels**:
1. User-facing: Friendly QMessageBox dialog
2. Recoverable: Log warning, continue
3. Critical: Log error, show dialog, graceful exit

```python
import logging
logger = logging.getLogger(__name__)

try:
    # Process
    logger.info("Success")
except FileNotFoundError as e:
    logger.error(f"File not found: {e}")
    # Show user dialog
except Exception as e:
    logger.exception(f"Unexpected error: {e}")
```

---

## Git Commits (Conventional)

Format: `<type>(<scope>): <subject>`

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Examples:
```
feat(download-tab): add progress tracking
fix(organizer): handle missing JSON fields
docs(readme): update installation steps
```

---

## Key Files

- `PROGRESS.md`: Project state tracking (read/update always)
- `src/main.py`: App entry point
- `src/gui/main_window.py`: Main window with tabs
- `src/core/`: Download, organize, tools logic
- `requirements.txt`: Dependencies

---

## Development Workflow

1. Read PROGRESS.md
2. Create branch: `git checkout -b feat/name`
3. Implement with type hints + docstrings
4. Test with pytest
5. Format: `black src/ tests/`
6. Lint: `flake8 src/ tests/`
7. Update PROGRESS.md
8. Commit with conventional format
9. Push

---

## Configuration

- User prefs: `~/.config/snapchat-organizer/config.json`
- Database: `~/.local/share/snapchat-organizer/snapchat.db`
- Dev secrets: `.env` (never commit)

---

## Testing with pytest

```python
import pytest
from pathlib import Path

@pytest.fixture
def sample_file(tmp_path):
    return tmp_path / "test.jpg"

def test_process_success(sample_file):
    result = process(sample_file)
    assert result['status'] == 'success'
```

---

## Performance

- Use generators for large datasets
- Batch DB operations
- Cache expensive computations
- Profile before optimizing

---

## Resources

- PySide6: https://doc.qt.io/qtforpython-6/
- SQLAlchemy: https://docs.sqlalchemy.org/
- Pillow: https://pillow.readthedocs.io/

---

## Quick Checklist

Before committing:
- [ ] Type hints + docstrings
- [ ] Error handling
- [ ] Logging (no print)
- [ ] Tests in `tests/`
- [ ] Black formatting
- [ ] Updated PROGRESS.md
- [ ] Conventional commit message

---

**Last Updated**: January 13, 2026