# Copilot Instructions for Snapchat Organizer Desktop

## Project Overview

**Snapchat Organizer Desktop** is a cross-platform desktop application built with Python and PySide6 that organizes Snapchat media exports. The application processes Snapchat data exports, organizes media files by conversation/person, applies metadata (EXIF data, timestamps), removes duplicates, and provides a user-friendly GUI for managing the entire workflow.

**⚠️ LICENSE & INTELLECTUAL PROPERTY**
- **License**: Proprietary - All Rights Reserved (closed-source)
- **Copyright**: © 2026 Mohammed Haris
- This is a commercial product - all code and documentation are confidential
- Do not suggest open-source practices (e.g., MIT, GPL licenses)
- Future plans include licensing system and hardware activation

### Core Technologies
- **Python 3.11+**: Primary development language
- **PySide6**: Qt-based GUI framework (LGPL licensed, compatible with proprietary use)
- **SQLAlchemy**: ORM for database operations
- **Pillow (PIL)**: Image processing and EXIF manipulation
- **SQLite**: Local database for metadata and application state

### Key Features
- Parse Snapchat JSON exports (chat_history.json, snap_history.json, etc.)
- Organize media files by person/conversation
- Apply EXIF metadata and timestamps
- Duplicate detection and removal
- Modern, responsive GUI with progress tracking
- Cross-platform support (macOS, Windows, Linux)
- **Default to Download tab on app startup**

---

## 🧠 Memory Management Across Conversations

**CRITICAL**: To maintain context across multiple chat sessions and avoid token limit issues:

### Primary Memory File: PROGRESS.md
Always use `PROGRESS.md` as the single source of truth for project state. This file must be:

1. **Read at the start of EVERY conversation**
   - Check completion status of all tasks
   - Understand current phase and progress percentage
   - Review recent completions and known issues
   - Identify next steps

2. **Updated after EVERY significant change**
   - Mark tasks as completed with [x]
   - Update progress percentages
   - Add new code statistics (lines, modules)
   - Record git commit SHAs
   - Note any blockers or issues discovered

3. **Structure to maintain**:
   ```markdown
   ## 🎯 Overall Progress: XX%
   
   ### Phase 1: Foundation - XX% Complete
   #### ✅ COMPLETED
   - [x] Task with commit SHA
   
   #### 🚧 IN PROGRESS
   - Current task details
   
   #### 📋 PENDING
   - Future tasks
   
   ## 📊 Metrics
   - Code statistics
   - Dependencies
   - Git commits
   
   ## 🐛 Known Issues
   
   ## 🎯 Next Session Goals
   
   **Last Updated:** [Date]
   ```

### When to Update PROGRESS.md
- ✅ After completing any Phase 1-3 task
- ✅ After creating new modules or significant files
- ✅ After git commits to track progress
- ✅ When discovering bugs or issues
- ✅ After testing or reaching milestones
- ✅ At end of work session with "Next Session Goals"

### Benefits
- **Context persistence**: Any agent can pick up where you left off
- **Token efficiency**: Avoid re-summarizing entire project history
- **Progress tracking**: Clear visibility into completion status
- **Planning**: Next session goals guide immediate work
- **Accountability**: Track what works and what needs fixing

### Usage Example
```markdown
At start of conversation:
1. Read PROGRESS.md to understand current state
2. Identify current task from "IN PROGRESS" section
3. Check "Next Session Goals" for immediate priorities
4. Review "Known Issues" before implementing

During work:
1. Mark tasks completed with [x] as you finish them
2. Update progress percentages
3. Add new files/modules to code statistics

At end of session:
1. Update "Last Updated" date
2. Set clear "Next Session Goals"
3. Commit PROGRESS.md to git
```

---

## Python Development Guidelines

### Code Style (PEP 8)
- **Line length**: Maximum 88 characters (Black formatter standard)
- **Indentation**: 4 spaces (no tabs)
- **Naming conventions**:
  - `snake_case` for functions, variables, and modules
  - `PascalCase` for classes
  - `UPPER_CASE` for constants
  - Prefix private methods/attributes with single underscore (`_method_name`)
- **Imports**: Group in order: standard library, third-party, local imports. Alphabetize within groups.

```python
# Standard library
import os
import sys
from pathlib import Path

# Third-party
from PySide6.QtWidgets import QApplication
from sqlalchemy import create_engine

# Local
from src.models import SnapchatMedia
from src.utils import logger
```

### Type Hints
Always use type hints for function parameters and return values:

```python
from typing import Optional, List, Dict
from pathlib import Path

def process_media_files(
    input_dir: Path,
    output_dir: Path,
    recursive: bool = True
) -> Dict[str, int]:
    """Process media files from input to output directory.
    
    Args:
        input_dir: Source directory containing media files
        output_dir: Destination directory for organized files
        recursive: Whether to process subdirectories
        
    Returns:
        Dictionary with processing statistics (files_processed, errors, etc.)
    """
    pass
```

### Docstrings
Use Google-style docstrings for all public modules, classes, and functions:

```python
def parse_snapchat_json(
    json_path: Path,
    media_type: str
) -> List[Dict[str, any]]:
    """Parse Snapchat export JSON file.
    
    Reads and validates Snapchat JSON export files, extracting
    relevant metadata for media organization.
    
    Args:
        json_path: Path to the Snapchat JSON export file
        media_type: Type of media ('chat', 'snap', 'story')
        
    Returns:
        List of dictionaries containing parsed media metadata
        
    Raises:
        FileNotFoundError: If json_path does not exist
        JSONDecodeError: If file contains invalid JSON
        ValueError: If media_type is not recognized
        
    Example:
        >>> data = parse_snapchat_json(Path("chat_history.json"), "chat")
        >>> len(data)
        150
    """
    pass
```

### Error Handling
- **Be specific**: Catch specific exceptions, not bare `except:`
- **Log errors**: Always log exceptions with context
- **User feedback**: Show user-friendly error messages in GUI
- **Cleanup**: Use context managers or try/finally for resource cleanup

```python
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

def load_config(config_path: Path) -> Optional[Dict[str, any]]:
    """Load configuration from JSON file."""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        logger.info(f"Configuration loaded from {config_path}")
        return config
    except FileNotFoundError:
        logger.error(f"Config file not found: {config_path}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in config file: {e}")
        return None
    except Exception as e:
        logger.exception(f"Unexpected error loading config: {e}")
        return None
```

### Logging
- Use Python's `logging` module (not print statements)
- Configure logging levels appropriately:
  - `DEBUG`: Detailed diagnostic information
  - `INFO`: General informational messages
  - `WARNING`: Warning messages for recoverable issues
  - `ERROR`: Error messages for failures
  - `CRITICAL`: Critical errors causing application failure

```python
import logging

# Configure logger
logger = logging.getLogger(__name__)

def process_file(file_path: Path) -> bool:
    """Process a single file."""
    logger.debug(f"Starting to process {file_path}")
    
    if not file_path.exists():
        logger.warning(f"File does not exist: {file_path}")
        return False
        
    try:
        # Process file
        logger.info(f"Successfully processed {file_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to process {file_path}: {e}", exc_info=True)
        return False
```

### Import Organization
- Use absolute imports from project root
- Avoid circular imports
- Import only what you need
- Use `from module import specific_item` for clarity

---

## PySide6 Best Practices

### Signals and Slots
- Use signals for thread-safe communication
- Connect signals to slots using type-safe connections
- Define custom signals as class attributes

```python
from PySide6.QtCore import QObject, Signal, Slot

class Worker(QObject):
    """Background worker for long-running tasks."""
    
    # Define signals
    progress_updated = Signal(int)  # progress percentage
    task_completed = Signal(dict)   # result data
    error_occurred = Signal(str)    # error message
    
    @Slot()
    def run_task(self):
        """Execute the task."""
        try:
            for i in range(100):
                # Do work
                self.progress_updated.emit(i)
            
            result = {"status": "success"}
            self.task_completed.emit(result)
        except Exception as e:
            self.error_occurred.emit(str(e))
```

### Thread Safety
- **Never** update GUI directly from background threads
- Use signals to communicate from worker threads to main thread
- Use `QThread` and `moveToThread()` for background operations

```python
from PySide6.QtCore import QThread, QObject, Signal, Slot
from PySide6.QtWidgets import QMainWindow

class MediaProcessor(QObject):
    """Worker for processing media files."""
    
    progress = Signal(int, str)  # progress, status message
    finished = Signal()
    
    def __init__(self, files: List[Path]):
        super().__init__()
        self.files = files
        
    @Slot()
    def process(self):
        """Process all files."""
        for i, file in enumerate(self.files):
            # Process file
            progress_pct = int((i + 1) / len(self.files) * 100)
            self.progress.emit(progress_pct, f"Processing {file.name}")
        
        self.finished.emit()

class MainWindow(QMainWindow):
    """Main application window."""
    
    def start_processing(self, files: List[Path]):
        """Start processing files in background thread."""
        self.thread = QThread()
        self.worker = MediaProcessor(files)
        
        # Move worker to thread
        self.worker.moveToThread(self.thread)
        
        # Connect signals
        self.thread.started.connect(self.worker.process)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.on_processing_complete)
        
        # Start thread
        self.thread.start()
    
    @Slot(int, str)
    def update_progress(self, value: int, message: str):
        """Update progress bar (safe to call from main thread)."""
        self.progress_bar.setValue(value)
        self.status_label.setText(message)
```

### Layouts
- Always use layouts (never fixed positioning)
- Use appropriate layout types:
  - `QVBoxLayout`: Vertical stacking
  - `QHBoxLayout`: Horizontal arrangement
  - `QGridLayout`: Grid arrangement
  - `QFormLayout`: Form-style (label-field pairs)
- Set proper spacing and margins

```python
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton

class ConfigPanel(QWidget):
    """Configuration panel widget."""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface."""
        # Main vertical layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        # Button row
        button_layout = QHBoxLayout()
        button_layout.addWidget(QPushButton("Import"))
        button_layout.addWidget(QPushButton("Export"))
        button_layout.addStretch()  # Push buttons to left
        
        layout.addLayout(button_layout)
```

### Resource Management
- Use Qt resource system (.qrc files) for icons, images, stylesheets
- Clean up resources in `closeEvent()` or use context managers
- Properly delete widgets and disconnect signals when done

---

## SQLAlchemy Best Practices

### Declarative Models
- Use declarative base for all models
- Define relationships clearly
- Use appropriate column types and constraints

```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class MediaFile(Base):
    """Represents a Snapchat media file."""
    
    __tablename__ = 'media_files'
    
    id = Column(Integer, primary_key=True)
    filename = Column(String, nullable=False, index=True)
    file_path = Column(String, nullable=False, unique=True)
    file_hash = Column(String(64), nullable=False, index=True)
    media_type = Column(String, nullable=False)  # 'image', 'video'
    created_at = Column(DateTime, nullable=False)
    processed = Column(Boolean, default=False)
    
    # Relationships
    conversation_id = Column(Integer, ForeignKey('conversations.id'))
    conversation = relationship("Conversation", back_populates="media_files")
    
    def __repr__(self):
        return f"<MediaFile(filename='{self.filename}', type='{self.media_type}')>"

class Conversation(Base):
    """Represents a Snapchat conversation."""
    
    __tablename__ = 'conversations'
    
    id = Column(Integer, primary_key=True)
    person_name = Column(String, nullable=False, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    media_files = relationship("MediaFile", back_populates="conversation")
```

### Session Management
- Use context managers for session lifecycle
- Commit transactions explicitly
- Handle rollback on errors

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator

class DatabaseManager:
    """Manages database connections and sessions."""
    
    def __init__(self, db_path: Path):
        self.engine = create_engine(f'sqlite:///{db_path}')
        self.SessionLocal = sessionmaker(bind=self.engine)
        
    def create_tables(self):
        """Create all tables."""
        Base.metadata.create_all(self.engine)
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Provide a transactional scope for database operations."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

# Usage
db = DatabaseManager(Path("snapchat.db"))

with db.get_session() as session:
    media = MediaFile(
        filename="photo.jpg",
        file_path="/path/to/photo.jpg",
        file_hash="abc123",
        media_type="image",
        created_at=datetime.now()
    )
    session.add(media)
    # Automatically commits on successful exit
```

### Migrations
- Use Alembic for database migrations
- Never modify existing migrations
- Test migrations both upgrade and downgrade

---

## Pillow (PIL) Best Practices

### Context Managers
Always use context managers when working with images:

```python
from PIL import Image
from pathlib import Path

def process_image(image_path: Path, output_path: Path):
    """Process and save image."""
    with Image.open(image_path) as img:
        # Process image
        img = img.resize((800, 600))
        img.save(output_path, quality=95)
```

### EXIF Preservation
- Preserve EXIF data when modifying images
- Use `piexif` for advanced EXIF manipulation
- Handle missing EXIF gracefully

```python
from PIL import Image
import piexif
from datetime import datetime
from pathlib import Path

def apply_exif_metadata(
    image_path: Path,
    date_taken: datetime,
    description: str = None
) -> None:
    """Apply EXIF metadata to image.
    
    Args:
        image_path: Path to the image file
        date_taken: Timestamp when photo was taken
        description: Optional image description
    """
    try:
        # Load image
        img = Image.open(image_path)
        
        # Get existing EXIF or create new
        try:
            exif_dict = piexif.load(img.info.get('exif', b''))
        except Exception:
            exif_dict = {"0th": {}, "Exif": {}, "GPS": {}}
        
        # Set DateTimeOriginal
        date_str = date_taken.strftime("%Y:%m:%d %H:%M:%S")
        exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = date_str.encode()
        exif_dict["0th"][piexif.ImageIFD.DateTime] = date_str.encode()
        
        # Set description if provided
        if description:
            exif_dict["0th"][piexif.ImageIFD.ImageDescription] = description.encode()
        
        # Save with updated EXIF
        exif_bytes = piexif.dump(exif_dict)
        img.save(image_path, exif=exif_bytes)
        
    except Exception as e:
        logger.error(f"Failed to apply EXIF to {image_path}: {e}")
```

---

## MCP Tool Usage Guidelines

### GitHub MCP Server
Use GitHub MCP tools for repository operations:

- **create_or_update_file**: Push individual files to repository
- **push_files**: Push multiple files in a single commit
- **create_pull_request**: Create PRs for new features
- **list_issues**: Check existing issues
- **create_repository**: Initialize new repos

```python
# Example: When user requests to upload file to GitHub
# Use: mcp_github_github_create_or_update_file
# Parameters: owner, repo, path, content, message, branch
```

### Context7 MCP (Upstash)
Use for retrieving up-to-date documentation:

1. **resolve-library-id**: First, resolve the library name to Context7 ID
2. **query-docs**: Then query documentation with specific questions

```python
# Example workflow:
# 1. resolve-library-id: libraryName="PySide6", query="Qt signals and slots"
# 2. query-docs: libraryId="/qt/pyside6", query="How to create custom signals"
```

### Python Environment Tools
- **configure_python_environment**: Set up Python environment before any operations
- **get_python_environment_details**: Check installed packages and versions
- **install_python_packages**: Install required dependencies

**Always call `configure_python_environment` before running Python code or installing packages.**

---

## Project-Specific Conventions

### File Naming
- Python modules: `snake_case.py`
- Classes: `PascalCase` within files
- Test files: `test_*.py`
- Configuration: `config.json`, `.env`

### Directory Structure
```
snapchat-organizer-desktop/
├── src/                    # Source code
│   ├── models/            # SQLAlchemy models
│   ├── ui/                # PySide6 UI components
│   ├── workers/           # Background workers
│   ├── utils/             # Utility functions
│   └── main.py            # Application entry point
├── tests/                 # Test suite
├── resources/             # Icons, images, stylesheets
├── docs/                  # Documentation
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
└── LICENSE               # License file
```

### Configuration Files
- Store user preferences in `~/.config/snapchat-organizer/config.json`
- Use `.env` for development secrets (never commit)
- Database location: `~/.local/share/snapchat-organizer/snapchat.db`

---

## Error Handling Strategy

### Levels of Error Handling
1. **User-facing errors**: Show friendly dialog with actionable message
2. **Recoverable errors**: Log warning, continue operation
3. **Critical errors**: Log error, show dialog, gracefully exit if needed

### Error Dialog Pattern
```python
from PySide6.QtWidgets import QMessageBox

def show_error(parent, title: str, message: str, details: str = None):
    """Show error dialog to user."""
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Critical)
    msg.setWindowTitle(title)
    msg.setText(message)
    if details:
        msg.setDetailedText(details)
    msg.exec()

# Usage
try:
    process_files()
except FileNotFoundError as e:
    show_error(
        self,
        "File Not Found",
        "Could not find the required file.",
        str(e)
    )
```

---

## Testing Guidelines

### Test Structure
- Use `pytest` for testing
- Organize tests in `tests/` directory matching `src/` structure
- Use fixtures for common setup

```python
import pytest
from pathlib import Path
from src.utils.file_processor import process_media_file

@pytest.fixture
def sample_image(tmp_path):
    """Create a sample image file for testing."""
    image_path = tmp_path / "test_image.jpg"
    # Create sample image
    return image_path

def test_process_media_file_success(sample_image):
    """Test successful media file processing."""
    result = process_media_file(sample_image)
    assert result is not None
    assert result['status'] == 'success'

def test_process_media_file_missing_file():
    """Test processing with missing file."""
    with pytest.raises(FileNotFoundError):
        process_media_file(Path("nonexistent.jpg"))
```

### Testing Checklist
- [ ] Unit tests for utility functions
- [ ] Integration tests for database operations
- [ ] GUI tests for critical user workflows
- [ ] Test error handling paths
- [ ] Test with various file formats and edge cases

---

## Performance Optimization

### General Guidelines
- Use generators for large datasets
- Batch database operations
- Cache expensive computations
- Use connection pooling for database
- Profile code before optimizing

### File Processing
```python
from pathlib import Path
from typing import Generator

def get_media_files(directory: Path) -> Generator[Path, None, None]:
    """Yield media files from directory (memory efficient)."""
    for file in directory.rglob("*"):
        if file.suffix.lower() in {'.jpg', '.jpeg', '.png', '.mp4', '.mov'}:
            yield file

# Batch processing
def process_files_batch(files: List[Path], batch_size: int = 100):
    """Process files in batches."""
    for i in range(0, len(files), batch_size):
        batch = files[i:i + batch_size]
        # Process batch
        with db.get_session() as session:
            for file in batch:
                # Process and add to session
                pass
            # Commit batch
```

---

## Git Commit Message Conventions

Follow conventional commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples
```
feat(ui): add progress bar to media processing

Implemented a progress bar that shows real-time status
during media file processing. Updates every 100 files.

Closes #123
```

```
fix(database): prevent duplicate entries in media_files table

Added unique constraint on file_path column to prevent
duplicate media file records.

Fixes #145
```

---

## Code Review Checklist

Before submitting code for review or committing:

- [ ] Code follows PEP 8 style guidelines
- [ ] All functions have type hints
- [ ] All public functions have docstrings
- [ ] Error handling is comprehensive
- [ ] Logging is used appropriately (not print statements)
- [ ] No hardcoded paths or credentials
- [ ] Tests are written and passing
- [ ] No commented-out code
- [ ] No debug print statements
- [ ] Dependencies are documented in requirements.txt
- [ ] Git commit message follows conventions

---

## Development Workflow

### Initial Setup
1. Clone repository
2. Create virtual environment: `python -m venv .venv`
3. Activate environment: `source .venv/bin/activate` (macOS/Linux) or `.venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Run tests: `pytest`

### Feature Development
1. Create feature branch: `git checkout -b feat/feature-name`
2. Implement feature with tests
3. Run tests and linting
4. Commit changes with conventional commit message
5. Push and create pull request

### Before Committing
```bash
# Format code
black src/ tests/

# Check linting
flake8 src/ tests/

# Run tests
pytest

# Check type hints
mypy src/
```

---

## Dependencies & Versions

### Core Dependencies
```txt
PySide6>=6.6.0          # Qt GUI framework
SQLAlchemy>=2.0.0       # ORM
Pillow>=10.0.0          # Image processing
piexif>=1.1.3           # EXIF manipulation
```

### Development Dependencies
```txt
pytest>=7.4.0           # Testing framework
black>=23.0.0           # Code formatter
flake8>=6.0.0           # Linter
mypy>=1.5.0             # Type checker
```

### Python Version
- **Minimum**: Python 3.11
- **Recommended**: Python 3.11 or 3.12

---

## MVP Features Checklist

### Core Features
- [x] Parse Snapchat JSON exports
- [x] Organize media by person/conversation
- [x] Apply EXIF metadata
- [x] Duplicate detection and removal
- [ ] GUI implementation
  - [ ] File selection dialog
  - [ ] Progress tracking
  - [ ] Settings panel
  - [ ] Results display
- [ ] Database integration
  - [ ] Media file tracking
  - [ ] Conversation management
  - [ ] Processing history

### Nice-to-Have Features (Post-MVP)
- [ ] Batch processing
- [ ] Advanced filtering options
- [ ] Export reports
- [ ] Cloud backup integration
- [ ] Auto-update functionality

---

## Resources and Documentation

### Official Documentation
- [PySide6 Documentation](https://doc.qt.io/qtforpython-6/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pillow Documentation](https://pillow.readthedocs.io/)
- [Python Type Hints (PEP 484)](https://peps.python.org/pep-0484/)

### Project-Specific
- [Project README](../README.md)
- [Build Instructions](../docs/BUILD-INSTRUCTIONS.md)
- [Contributing Guidelines](../CONTRIBUTING.md)

### Learning Resources
- [Qt for Python Tutorial](https://doc.qt.io/qtforpython-6/tutorials/index.html)
- [SQLAlchemy ORM Tutorial](https://docs.sqlalchemy.org/en/20/orm/tutorial.html)
- [Real Python - GUI Programming](https://realpython.com/python-pyqt-gui-calculator/)

---

## Notes for GitHub Copilot

When assisting with this project:
1. **Always** suggest type hints and docstrings
2. **Prefer** signals/slots over direct function calls in PySide6
3. **Use** context managers for file and database operations
4. **Follow** the project directory structure
5. **Write** tests alongside implementation code
6. **Log** errors instead of using print statements
7. **Check** for existing similar code before implementing new features
8. **Suggest** performance optimizations when processing large file sets

For questions or clarifications, refer to the project README or ask for specific guidance.

---

**Last Updated**: January 11, 2026
**Version**: 1.0.0
