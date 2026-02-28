"""Snapchat Organizer Desktop - Main application entry point.

This is the main entry point for the Snapchat Organizer Desktop application.
It initializes the Qt application, creates the main window, and starts the event loop.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from src.gui.main_window import MainWindow
from src.gui.download_tab import DownloadTab
from src.gui.organize_tab import OrganizeTab
from src.gui.tools_tab import ToolsTab
from src.gui.license_dialog import LicenseDialog
from src.license.license_manager import LicenseManager
from src.utils.config import APP_NAME, APP_VERSION, TIER_FREE
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

    # Initialize theme manager and start monitoring
    from src.utils.theme import ThemeManager

    theme_manager = ThemeManager()
    theme_manager.apply_theme(app)
    theme_manager.start_monitoring(1000)  # Check every 1 second

    # ── License check ──
    license_manager = LicenseManager()
    current_tier = TIER_FREE

    if license_manager.is_logged_in:
        # Validate existing session with the server
        logger.info("Existing session found, validating license...")
        validation = license_manager.validate_on_startup()
        if validation.get('valid'):
            current_tier = validation.get('tier', TIER_FREE)
            logger.info(f"License valid: tier={current_tier}")
        else:
            # Session expired or invalid — show login dialog
            logger.info("Session invalid, showing license dialog")
            dialog = LicenseDialog(license_manager)
            if dialog.exec():
                current_tier = license_manager.current_tier
            else:
                current_tier = TIER_FREE
    else:
        # No session — show license dialog
        logger.info("No active session, showing license dialog")
        dialog = LicenseDialog(license_manager)
        if dialog.exec():
            current_tier = license_manager.current_tier
        else:
            current_tier = TIER_FREE

    logger.info(f"Proceeding with tier: {current_tier}")

    # Create main window
    window = MainWindow(license_manager=license_manager)

    # Get icons directory
    icons_dir = Path(__file__).parent.parent / "resources" / "icons"

    # Add actual tab implementations
    # Download Tab
    download_tab = DownloadTab()
    window.tab_widget.addTab(
        download_tab, QIcon(str(icons_dir / "tab_download.png")), "Download Memories"
    )

    # Organize Tab
    organize_tab = OrganizeTab()
    window.tab_widget.addTab(
        organize_tab,
        QIcon(str(icons_dir / "tab_organize.png")),
        "Organize Chat Media",
    )

    # Tools Tab
    tools_tab = ToolsTab()
    window.tab_widget.addTab(
        tools_tab, QIcon(str(icons_dir / "tab_tools.png")), "Tools"
    )

    # Set Download tab as default
    window.tab_widget.setCurrentIndex(0)

    # Apply feature gating based on license tier
    download_tab.set_license_tier(current_tier)
    tools_tab.set_license_tier(current_tier)

    # Show window
    window.show()

    logger.info("Application window displayed")

    # Start event loop
    exit_code = app.exec()

    logger.info(f"Application exiting with code {exit_code}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
