---
inclusion: always
---

# Development Conventions & Guidelines

## Critical Project Context

### ALWAYS Check PROGRESS.md First
- Read completion status, current phase, and known issues
- Identify next steps from "IN PROGRESS" section
- Review "Next Session Goals" before making changes

### ALWAYS Update PROGRESS.md After Changes
- Mark completed tasks with [x]
- Update progress percentages
- Record git commit SHAs for significant changes
- Document any blockers or issues encountered

## Python Code Standards

### Required Code Style (PEP 8 + Black)
- Line length: 88 characters maximum
- Indentation: 4 spaces (no tabs)
- Naming conventions:
  - Functions/variables: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_SNAKE_CASE`
  - Private members: prefix with `_`

### Mandatory Code Patterns
- **Type hints**: Required for all function parameters and return values
- **Docstrings**: Google-style docstrings for all public functions/classes
- **Logging**: Use `logging` module, never `print()` statements
- **Context managers**: Always use `with` statements for files/database connections
- **Specific exceptions**: Catch specific exception types, avoid bare `except:`

### Import Organization
Order: standard library → third-party → local imports

```python
from pathlib import Path
from typing import Optional, Dict

from PySide6.QtCore import QObject, Signal

from src.utils.logger import get_logger
```

## PySide6 GUI Architecture

### Threading Rules (CRITICAL)
- **Main thread**: GUI operations only
- **Background work**: Use QThread + moveToThread() pattern
- **Communication**: Use signals/slots for thread-safe updates
- **Never**: Update GUI directly from worker threads

### Required GUI Patterns
```python
class Worker(QObject):
    progress = Signal(int, str)  # Define signals as class attributes
    finished = Signal()
    
    @Slot()
    def process(self):
        # Emit progress updates
        self.progress.emit(50, "Processing...")
        self.finished.emit()
```

### Layout Requirements
- Always use Qt layouts (QVBoxLayout, QHBoxLayout, QGridLayout)
- Never use fixed positioning or manual geometry management

## File Organization (Strict Rules)

### Test Structure
- Tests MUST be in `tests/` directory
- Test files MUST follow `test_*.py` naming
- Test structure MUST mirror `src/` directory structure
- NEVER create test files inside `src/`

### Documentation Structure
- Feature docs go in `docs/[feature_name]/`
- NEVER create documentation files in project root
- Use lowercase with hyphens for doc filenames

## Error Handling Strategy

### Three-Tier Approach
1. **User-facing errors**: Show friendly QMessageBox dialogs
2. **Recoverable errors**: Log warning and continue execution
3. **Critical errors**: Log error, show dialog, graceful shutdown

### Required Error Handling Pattern
```python
import logging
logger = logging.getLogger(__name__)

try:
    # Operation
    logger.info("Operation completed successfully")
except FileNotFoundError as e:
    logger.error(f"Required file not found: {e}")
    # Show user-friendly dialog
except Exception as e:
    logger.exception(f"Unexpected error in operation: {e}")
    # Handle gracefully
```

## Configuration Management

### Standard Paths
- User preferences: `~/.config/snapchat-organizer/config.json`
- Application database: `~/.local/share/snapchat-organizer/snapchat.db`
- Development secrets: `.env` (never commit to git)

## Testing Requirements

### Test Structure with pytest
```python
import pytest
from pathlib import Path

@pytest.fixture
def sample_file(tmp_path):
    """Create test file fixture."""
    return tmp_path / "test.jpg"

def test_process_success(sample_file):
    """Test successful file processing."""
    result = process_file(sample_file)
    assert result['status'] == 'success'
```

## Performance Guidelines

- Use generators for processing large datasets
- Batch database operations when possible
- Cache expensive computations
- Profile before optimizing (measure first)

## Git Workflow

### Conventional Commits (Required)
Format: `<type>(<scope>): <subject>`

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Examples:
```
feat(download-tab): add progress tracking for memory downloads
fix(organizer): handle missing JSON fields in chat data
docs(readme): update installation steps for macOS
```

## Pre-Commit Checklist

Before any commit, ensure:
- [ ] Type hints added to all functions
- [ ] Proper error handling implemented
- [ ] Logging used instead of print statements
- [ ] Tests created in `tests/` directory
- [ ] Code formatted with Black
- [ ] PROGRESS.md updated with changes
- [ ] Conventional commit message format used