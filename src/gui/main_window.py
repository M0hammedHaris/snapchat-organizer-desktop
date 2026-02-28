"""Main application window with tabbed interface.

This module provides the main window for Snapchat Organizer Desktop,
featuring a tabbed interface for Download, Organize, and Tools functionality.
"""

from typing import Optional
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QTabWidget,
    QMessageBox,
)
from PySide6.QtCore import QSize
from PySide6.QtGui import QAction, QIcon
from pathlib import Path

from ..utils.config import (
    APP_NAME,
    APP_VERSION,
    TIER_FREE,
    WINDOW_MIN_WIDTH,
    WINDOW_MIN_HEIGHT,
    WINDOW_DEFAULT_WIDTH,
    WINDOW_DEFAULT_HEIGHT,
    is_first_run,
    mark_first_run_complete,
    should_show_help_on_startup,
    set_show_help_on_startup,
)
from ..utils.logger import get_logger
from .settings_dialog import SettingsDialog
from .help_dialog import HelpDialog

logger = get_logger(__name__)


class MainWindow(QMainWindow):
    """Main application window with tabbed interface."""

    def __init__(self, parent: Optional[QWidget] = None, license_manager=None):
        """Initialize the main window.

        Args:
            parent: Parent widget (optional)
            license_manager: LicenseManager instance for license state
        """
        super().__init__(parent)
        self._license_manager = license_manager

        logger.info(f"Initializing {APP_NAME} v{APP_VERSION}")

        self._setup_ui()
        self._create_menu_bar()

        logger.debug("Main window initialized")

        # Show help dialog on first run (using QTimer to ensure window is shown first)
        from PySide6.QtCore import QTimer

        QTimer.singleShot(500, self._check_first_run)

    def _setup_ui(self):
        """Set up the user interface."""
        # Window properties
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(QSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT))
        self.resize(QSize(WINDOW_DEFAULT_WIDTH, WINDOW_DEFAULT_HEIGHT))

        # Set window icon
        resources_dir = Path(__file__).parent.parent.parent / "resources"
        icon_path = resources_dir / "icons" / "icon.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        # Central widget with layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)

        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(False)
        self.tab_widget.setTabPosition(QTabWidget.North)
        layout.addWidget(self.tab_widget)

        logger.debug("UI setup complete")

    def _create_menu_bar(self):
        """Create the application menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        # Settings action
        settings_action = QAction("&Settings", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self._show_settings)
        file_menu.addAction(settings_action)

        file_menu.addSeparator()

        # Account / License action
        account_action = QAction("&Account && License", self)
        account_action.triggered.connect(self._show_account_dialog)
        file_menu.addAction(account_action)

        file_menu.addSeparator()

        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        # How to Download Data action
        download_help_action = QAction("How to &Download Snapchat Data", self)
        download_help_action.setShortcut("F1")
        download_help_action.triggered.connect(self._show_download_help)
        help_menu.addAction(download_help_action)

        # Documentation action
        docs_action = QAction("&Online Documentation", self)
        docs_action.triggered.connect(self._show_documentation)
        help_menu.addAction(docs_action)

        help_menu.addSeparator()

        # About action
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

        logger.debug("Menu bar created")

    def _show_settings(self):
        """Show settings dialog."""
        logger.info("Opening settings dialog")
        dialog = SettingsDialog(self)
        dialog.settings_changed.connect(self._on_settings_changed)
        dialog.exec()

    def _show_download_help(self):
        """Show help dialog for downloading Snapchat data."""
        logger.info("Opening download help dialog")
        dialog = HelpDialog(self, show_dont_show_again=False)
        dialog.exec()

    def _check_first_run(self):
        """Check if this is the first run and show help dialog if needed."""
        if should_show_help_on_startup():
            logger.info("First run detected, showing help dialog")
            dialog = HelpDialog(self, show_dont_show_again=True)
            dialog.exec()

            # If user checked "don't show again", save the preference
            if hasattr(dialog, "dont_show_again") and dialog.dont_show_again:
                logger.info("User opted not to show help on startup")
                set_show_help_on_startup(False)

            # Mark first run as complete
            if is_first_run():
                mark_first_run_complete()
                logger.info("First run marked as complete")

    def _on_settings_changed(self, settings: dict):
        """Handle settings changes.

        Args:
            settings: Dictionary of updated settings
        """
        logger.info("Settings changed, applying new configuration")
        # TODO: Apply settings to application components
        # For now, just log the changes
        for key, value in settings.items():
            logger.debug(f"Setting changed: {key} = {value}")

    def _show_documentation(self):
        """Show documentation."""
        logger.info("Documentation requested")
        QMessageBox.information(
            self,
            "Documentation",
            f"{APP_NAME} Documentation\n\n"
            "Complete documentation is available at:\n"
            "https://github.com/M0hammedHaris/snapchat-organizer-desktop\n\n"
            "For help downloading Snapchat data, use:\n"
            "Help → How to Download Snapchat Data (F1)",
        )

    def _show_about(self):
        """Show about dialog."""
        logger.info("About dialog requested")

        tier_info = ""
        if self._license_manager:
            tier = self._license_manager.current_tier.upper()
            email = self._license_manager.user_email or "Not logged in"
            trial = " (Trial)" if self._license_manager.is_trial else ""
            tier_info = (
                f"<p><b>License:</b> {tier}{trial}</p>"
                f"<p><b>Account:</b> {email}</p>"
            )

        QMessageBox.about(
            self,
            f"About {APP_NAME}",
            f"<h2>{APP_NAME}</h2>"
            f"<p>Version {APP_VERSION}</p>"
            f"<p>Desktop application for downloading and organizing "
            f"Snapchat memories locally.</p>"
            f"{tier_info}"
            f"<p><b>Features:</b></p>"
            f"<ul>"
            f"<li>Download memories from HTML exports</li>"
            f"<li>Organize chat media by contact</li>"
            f"<li>Apply overlays to recreate Snapchat look</li>"
            f"<li>Preserve GPS metadata</li>"
            f"<li>100% private - all local processing</li>"
            f"</ul>"
            f"<p>© 2026 Mohammed Haris</p>",
        )

    def _show_account_dialog(self):
        """Show the account/license dialog."""
        if self._license_manager:
            from .license_dialog import LicenseDialog
            dialog = LicenseDialog(self._license_manager, parent=self, allow_skip=False)
            dialog.user_logged_out.connect(lambda: self._handle_logout(dialog))
            dialog.exec()

    def _handle_logout(self, open_dialog):
        """Handle user logout — force re-authentication.

        Closes the current account dialog, hides the main window,
        and shows the license dialog. If the user does not log in
        or skip, the application quits.
        """
        open_dialog.reject()  # Close the account dialog

        self.hide()
        logger.info("User logged out, requiring re-authentication")

        from .license_dialog import LicenseDialog
        dialog = LicenseDialog(self._license_manager, parent=None, allow_skip=True)
        if dialog.exec():
            # User logged in or skipped — re-apply feature gating
            tier = self._license_manager.current_tier
            logger.info(f"Re-authenticated with tier: {tier}")
            self._apply_feature_gating(tier)
            self.show()
        else:
            # User closed the dialog — quit the app
            logger.info("User closed login dialog after logout, quitting")
            from PySide6.QtWidgets import QApplication
            QApplication.instance().quit()

    def _apply_feature_gating(self, tier: str):
        """Apply feature gating to all tabs based on license tier.

        Args:
            tier: License tier (free, pro, premium)
        """
        for i in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(i)
            if hasattr(tab, 'set_license_tier'):
                tab.set_license_tier(tier)

    def closeEvent(self, event):
        """Handle window close event.

        Args:
            event: Close event
        """
        logger.info("Application closing")

        # TODO: Check if any operations are in progress
        # For now, just accept the close event
        event.accept()
