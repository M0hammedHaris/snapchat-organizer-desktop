"""Snapchat Organizer Desktop - Main application entry point.

This is the main entry point for the Snapchat Organizer Desktop application.
It initializes the Qt application, creates the main window, and starts the event loop.

Sentry is initialized FIRST — before all other imports — so that import errors,
missing DLLs on Windows, and any startup crash are captured automatically.
"""

import logging
import platform
import sys
import threading
from pathlib import Path

# ── Sentry must be the FIRST thing initialized ──
# This ensures crashes during import of PySide6, SQLAlchemy, etc. are captured.
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

# Minimal version/name constants so Sentry init doesn't depend on our modules
_APP_NAME = "Snapchat Organizer"
_APP_VERSION = "1.0.0-beta.1"

sentry_logging = LoggingIntegration(
    level=logging.INFO,          # Capture INFO+ as breadcrumbs
    event_level=logging.ERROR,   # Send ERROR+ as Sentry events
)

sentry_sdk.init(
    dsn="https://2f36781c6e05b513d96d8f7f444e0fff@o4510963528237056.ingest.de.sentry.io/4510963531317328",
    send_default_pii=True,
    release=f"{_APP_NAME}@{_APP_VERSION}",
    environment="beta",
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
    enable_tracing=True,
    integrations=[sentry_logging],
)

# Tag every event with OS info so you can filter "Windows" issues in Sentry
sentry_sdk.set_tag("os.name", platform.system())            # Windows / Darwin / Linux
sentry_sdk.set_tag("os.version", platform.version())        # e.g. 10.0.19045
sentry_sdk.set_tag("os.arch", platform.machine())           # AMD64 / arm64
sentry_sdk.set_tag("python.version", platform.python_version())


# ── Global exception hooks — catch crashes EVERYWHERE ──

def _sentry_excepthook(exc_type, exc_value, exc_tb):
    """Catch any unhandled exception in the main thread and send to Sentry."""
    # Ignore KeyboardInterrupt
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_tb)
        return
    sentry_sdk.capture_exception((exc_type, exc_value, exc_tb))
    sys.__excepthook__(exc_type, exc_value, exc_tb)


def _sentry_threading_excepthook(args):
    """Catch any unhandled exception in background threads and send to Sentry."""
    if args.exc_type is not None and not issubclass(args.exc_type, KeyboardInterrupt):
        sentry_sdk.capture_exception((args.exc_type, args.exc_value, args.exc_traceback))


sys.excepthook = _sentry_excepthook
threading.excepthook = _sentry_threading_excepthook


# ── Now import the rest of the application ──
# If any of these imports fail (e.g. missing DLL on Windows), Sentry captures it.

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from src.gui.main_window import MainWindow
from src.gui.download_tab import DownloadTab
from src.gui.organize_tab import OrganizeTab
from src.gui.tools_tab import ToolsTab
from src.gui.license_dialog import LicenseDialog
from src.gui.onboarding_dialog import OnboardingDialog
from src.license.license_manager import LicenseManager
from src.utils.config import APP_NAME, APP_VERSION, TIER_FREE, is_first_run, mark_first_run_complete
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

    # ── Onboarding carousel on first launch ──
    if is_first_run():
        logger.info("First run detected, showing onboarding carousel")
        onboarding = OnboardingDialog()
        onboarding.exec()
        mark_first_run_complete()
        logger.info("First run marked as complete")

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
    window._apply_feature_gating(current_tier)

    # Show window
    window.show()

    logger.info("Application window displayed")

    # Start event loop
    exit_code = app.exec()

    logger.info(f"Application exiting with code {exit_code}")
    return exit_code


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        # Last-resort catch — guarantees Sentry gets the event even if
        # something goes wrong before the Qt event loop starts.
        sentry_sdk.capture_exception(e)
        sentry_sdk.flush(timeout=5)
        raise
