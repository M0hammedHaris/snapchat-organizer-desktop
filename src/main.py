"""Snapchat Organizer Desktop - Main application entry point.

This is the main entry point for the Snapchat Organizer Desktop application.
It initializes the Qt application, creates the main window, and starts the event loop.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from src.gui.main_window import MainWindow
from src.gui.download_tab import DownloadTab
from src.gui.organize_tab import OrganizeTab
from src.gui.tools_tab import ToolsTab
from src.utils.config import APP_NAME, APP_VERSION
from src.utils.logger import get_logger

logger = get_logger(__name__)


def main():
    """Main application entry point."""
    logger.info(f"Starting {APP_NAME} v{APP_VERSION}")
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName("SnapchatOrganizer")
    
    # High DPI scaling is enabled by default in Qt6
    
    # Create main window
    window = MainWindow()
    
    # Initialize theme manager and start monitoring
    from src.utils.theme import ThemeManager
    theme_manager = ThemeManager()
    theme_manager.apply_theme(app)
    theme_manager.start_monitoring(1000)  # Check every 1 second
    
    # Replace placeholder tabs with actual implementations
    # Download Tab
    download_tab = DownloadTab()
    window.remove_tab(0)  # Remove placeholder
    window.add_tab(download_tab, "📥 Download Memories", index=0)
    
    # Organize Tab
    organize_tab = OrganizeTab()
    window.remove_tab(1)  # Remove placeholder
    window.add_tab(organize_tab, "📁 Organize Chat Media", index=1)
    
    # Tools Tab
    tools_tab = ToolsTab()
    window.remove_tab(2)  # Remove placeholder
    window.add_tab(tools_tab, "🔧 Tools", index=2)
    
    # Set Download tab as default
    window.set_current_tab(0)
    
    # Show window
    window.show()
    
    logger.info("Application window displayed")
    
    # Start event loop
    exit_code = app.exec()
    
    logger.info(f"Application exiting with code {exit_code}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
