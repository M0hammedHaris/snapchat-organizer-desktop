"""License dialog - Login, Register, and License management UI.

This module provides the license dialog that appears on startup when the user
is not logged in. It handles user authentication, registration, license
activation, upgrade via Stripe, and device management.
"""

import logging
import webbrowser
from typing import Optional

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QStackedWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
    QFormLayout,
    QGroupBox,
)
from PySide6.QtCore import Qt, Signal, QThread, QObject, Slot
from PySide6.QtGui import QFont

from ..license.license_manager import LicenseManager
from ..license.api_client import APIError
from ..utils.config import APP_NAME, TIER_FREE, TIER_PRO, TIER_PREMIUM

logger = logging.getLogger(__name__)


class _AuthWorker(QObject):
    """Background worker for auth operations to avoid blocking the UI."""
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, func, *args):
        super().__init__()
        self._func = func
        self._args = args

    @Slot()
    def run(self):
        try:
            result = self._func(*self._args)
            self.finished.emit(result)
        except APIError as e:
            self.error.emit(str(e))
        except Exception as e:
            self.error.emit(f"Unexpected error: {e}")


class LicenseDialog(QDialog):
    """Dialog for login, registration, and license management.

    Shows on startup if user is not authenticated. Provides:
    - Login form
    - Registration form
    - License status display
    - Upgrade buttons (opens Stripe checkout in browser)
    - Skip option (runs as free tier)
    """

    license_validated = Signal(str)  # Emits current tier

    def __init__(
        self,
        license_manager: LicenseManager,
        parent: Optional[QWidget] = None,
        allow_skip: bool = True,
    ):
        super().__init__(parent)
        self._license_manager = license_manager
        self._allow_skip = allow_skip
        self._thread: Optional[QThread] = None
        self._worker: Optional[_AuthWorker] = None

        self.setWindowTitle(f"{APP_NAME} - Account")
        self.setMinimumSize(480, 420)
        self.setMaximumSize(560, 600)
        self.setModal(True)

        self._setup_ui()

    def _setup_ui(self):
        """Set up the stacked widget with login/register/status pages."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        # Title
        title = QLabel(APP_NAME)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Sign in to unlock all features")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: gray; margin-bottom: 8px;")
        layout.addWidget(subtitle)

        # Stacked pages: 0=login, 1=register, 2=status
        self._stack = QStackedWidget()
        self._stack.addWidget(self._create_login_page())
        self._stack.addWidget(self._create_register_page())
        self._stack.addWidget(self._create_status_page())
        layout.addWidget(self._stack)

        # Status label for errors/success
        self._status_label = QLabel("")
        self._status_label.setAlignment(Qt.AlignCenter)
        self._status_label.setWordWrap(True)
        layout.addWidget(self._status_label)

        # If already logged in, show status page
        if self._license_manager.is_logged_in:
            self._refresh_status_page()
            self._stack.setCurrentIndex(2)

    def _create_login_page(self) -> QWidget:
        """Create the login form page."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(10)

        form = QFormLayout()
        form.setSpacing(8)

        self._login_email = QLineEdit()
        self._login_email.setPlaceholderText("you@example.com")
        form.addRow("Email:", self._login_email)

        self._login_password = QLineEdit()
        self._login_password.setEchoMode(QLineEdit.Password)
        self._login_password.setPlaceholderText("Enter your password")
        form.addRow("Password:", self._login_password)

        layout.addLayout(form)

        # Login button
        self._login_btn = QPushButton("Sign In")
        self._login_btn.setMinimumHeight(36)
        self._login_btn.clicked.connect(self._on_login)
        layout.addWidget(self._login_btn)

        # Switch to register
        switch_layout = QHBoxLayout()
        switch_layout.addWidget(QLabel("Don't have an account?"))
        register_link = QPushButton("Create Account")
        register_link.setFlat(True)
        register_link.setStyleSheet("color: #2196F3; text-decoration: underline; border: none;")
        register_link.clicked.connect(lambda: self._stack.setCurrentIndex(1))
        switch_layout.addWidget(register_link)
        switch_layout.addStretch()
        layout.addLayout(switch_layout)

        # Skip button
        if self._allow_skip:
            layout.addSpacing(8)
            skip_btn = QPushButton("Continue without account (Free tier)")
            skip_btn.setFlat(True)
            skip_btn.setStyleSheet("color: gray;")
            skip_btn.clicked.connect(self._on_skip)
            layout.addWidget(skip_btn, alignment=Qt.AlignCenter)

        layout.addStretch()
        return page

    def _create_register_page(self) -> QWidget:
        """Create the registration form page."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(10)

        form = QFormLayout()
        form.setSpacing(8)

        self._reg_name = QLineEdit()
        self._reg_name.setPlaceholderText("Your Name")
        form.addRow("Name:", self._reg_name)

        self._reg_email = QLineEdit()
        self._reg_email.setPlaceholderText("you@example.com")
        form.addRow("Email:", self._reg_email)

        self._reg_password = QLineEdit()
        self._reg_password.setEchoMode(QLineEdit.Password)
        self._reg_password.setPlaceholderText("At least 8 characters")
        form.addRow("Password:", self._reg_password)

        self._reg_confirm = QLineEdit()
        self._reg_confirm.setEchoMode(QLineEdit.Password)
        self._reg_confirm.setPlaceholderText("Confirm your password")
        form.addRow("Confirm:", self._reg_confirm)

        layout.addLayout(form)

        # Register button
        self._register_btn = QPushButton("Create Account")
        self._register_btn.setMinimumHeight(36)
        self._register_btn.clicked.connect(self._on_register)
        layout.addWidget(self._register_btn)

        # Switch to login
        switch_layout = QHBoxLayout()
        switch_layout.addWidget(QLabel("Already have an account?"))
        login_link = QPushButton("Sign In")
        login_link.setFlat(True)
        login_link.setStyleSheet("color: #2196F3; text-decoration: underline; border: none;")
        login_link.clicked.connect(lambda: self._stack.setCurrentIndex(0))
        switch_layout.addWidget(login_link)
        switch_layout.addStretch()
        layout.addLayout(switch_layout)

        layout.addStretch()
        return page

    def _create_status_page(self) -> QWidget:
        """Create the license status page (shown when logged in)."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(12)

        # User info group
        user_group = QGroupBox("Account")
        user_layout = QFormLayout(user_group)
        self._status_email = QLabel("—")
        self._status_name = QLabel("—")
        user_layout.addRow("Email:", self._status_email)
        user_layout.addRow("Name:", self._status_name)
        layout.addWidget(user_group)

        # License info group
        license_group = QGroupBox("License")
        license_layout = QFormLayout(license_group)
        self._status_tier = QLabel("—")
        self._status_key = QLabel("—")
        self._status_key.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self._status_trial = QLabel("—")
        self._status_expires = QLabel("—")
        license_layout.addRow("Tier:", self._status_tier)
        license_layout.addRow("Key:", self._status_key)
        license_layout.addRow("Trial:", self._status_trial)
        license_layout.addRow("Expires:", self._status_expires)
        layout.addWidget(license_group)

        # Action buttons
        btn_layout = QHBoxLayout()

        self._upgrade_btn = QPushButton("Upgrade to Pro")
        self._upgrade_btn.setMinimumHeight(34)
        self._upgrade_btn.clicked.connect(lambda: self._on_upgrade(TIER_PRO))
        btn_layout.addWidget(self._upgrade_btn)

        self._premium_btn = QPushButton("Upgrade to Premium")
        self._premium_btn.setMinimumHeight(34)
        self._premium_btn.clicked.connect(lambda: self._on_upgrade(TIER_PREMIUM))
        btn_layout.addWidget(self._premium_btn)

        layout.addLayout(btn_layout)

        # Continue / Logout buttons
        bottom_layout = QHBoxLayout()

        logout_btn = QPushButton("Logout")
        logout_btn.clicked.connect(self._on_logout)
        bottom_layout.addWidget(logout_btn)

        bottom_layout.addStretch()

        continue_btn = QPushButton("Continue")
        continue_btn.setMinimumHeight(34)
        continue_btn.setDefault(True)
        continue_btn.clicked.connect(self._on_continue)
        bottom_layout.addWidget(continue_btn)

        layout.addLayout(bottom_layout)
        layout.addStretch()
        return page

    # ── Actions ──

    def _on_login(self):
        """Handle login button click."""
        email = self._login_email.text().strip()
        password = self._login_password.text()

        if not email or not password:
            self._show_status("Please enter email and password.", error=True)
            return

        self._set_loading(True, "Signing in...")
        self._run_in_thread(
            self._license_manager.login, email, password,
            on_success=self._on_auth_success,
            on_error=self._on_auth_error,
        )

    def _on_register(self):
        """Handle register button click."""
        name = self._reg_name.text().strip()
        email = self._reg_email.text().strip()
        password = self._reg_password.text()
        confirm = self._reg_confirm.text()

        if not name or not email or not password:
            self._show_status("All fields are required.", error=True)
            return

        if password != confirm:
            self._show_status("Passwords do not match.", error=True)
            return

        if len(password) < 8:
            self._show_status("Password must be at least 8 characters.", error=True)
            return

        self._set_loading(True, "Creating account...")
        self._run_in_thread(
            self._license_manager.register, email, password, name,
            on_success=self._on_auth_success,
            on_error=self._on_auth_error,
        )

    def _on_auth_success(self, result: dict):
        """Handle successful login/register."""
        self._set_loading(False)
        message = result.get('message', 'Success')
        self._show_status(message, error=False)
        self._refresh_status_page()
        self._stack.setCurrentIndex(2)

    def _on_auth_error(self, error_msg: str):
        """Handle login/register error."""
        self._set_loading(False)
        self._show_status(error_msg, error=True)

    def _on_skip(self):
        """User chose to skip login (free tier)."""
        self.license_validated.emit(TIER_FREE)
        self.accept()

    def _on_continue(self):
        """User clicked Continue from status page."""
        self.license_validated.emit(self._license_manager.current_tier)
        self.accept()

    def _on_logout(self):
        """Handle logout."""
        self._license_manager.logout()
        self._show_status("Logged out.", error=False)
        self._stack.setCurrentIndex(0)

    def _on_upgrade(self, tier: str):
        """Handle upgrade button click.

        In mock mode: calls the mock-confirm endpoint directly.
        In real mode: opens Stripe checkout in the browser.
        """
        self._show_status(f"Processing upgrade to {tier}...", error=False)
        self._set_loading(True, f"Upgrading to {tier}...")
        self._run_in_thread(
            self._do_upgrade, tier,
            on_success=self._on_upgrade_success,
            on_error=self._on_auth_error,
        )

    def _do_upgrade(self, tier: str) -> dict:
        """Perform the upgrade operation (runs in background thread)."""
        mgr = self._license_manager

        # Try mock-confirm first (works when MOCK_STRIPE=true)
        response = mgr.confirm_upgrade(tier)
        if response.get('success'):
            return response

        # Fall back to opening Stripe checkout in browser
        url = mgr.get_checkout_url(tier)
        if url:
            webbrowser.open(url)
            return {
                'success': True,
                'message': (
                    "Checkout opened in your browser. "
                    "After payment, restart the app to activate."
                ),
                'data': {'browser': True},
            }

        raise APIError("Could not process upgrade. Please try again later.")

    def _on_upgrade_success(self, result: dict):
        """Handle successful upgrade."""
        self._set_loading(False)
        message = result.get('message', 'Upgrade successful!')
        data = result.get('data', {})

        if data.get('browser'):
            # Stripe checkout opened in browser — no immediate tier change
            self._show_status(message, error=False)
        else:
            # Mock mode — upgrade happened immediately
            self._show_status(message, error=False)
            self._refresh_status_page()

    # ── Helpers ──

    def _refresh_status_page(self):
        """Update the status page with current license data."""
        mgr = self._license_manager
        self._status_email.setText(mgr.user_email or "—")
        self._status_name.setText(mgr.user_name or "—")
        self._status_tier.setText(mgr.current_tier.upper())
        self._status_key.setText(mgr.license_key or "—")
        self._status_trial.setText("Yes" if mgr.is_trial else "No")
        self._status_expires.setText(mgr.expires_at or "Never")

        # Hide upgrade buttons if already on that tier
        tier = mgr.current_tier
        self._upgrade_btn.setVisible(tier == TIER_FREE)
        self._premium_btn.setVisible(tier != TIER_PREMIUM)

    def _show_status(self, message: str, error: bool = False):
        """Show a status message."""
        color = "#f44336" if error else "#4CAF50"
        self._status_label.setStyleSheet(f"color: {color}; padding: 4px;")
        self._status_label.setText(message)

    def _set_loading(self, loading: bool, message: str = ""):
        """Enable/disable form controls during API calls."""
        self._login_btn.setEnabled(not loading)
        self._register_btn.setEnabled(not loading)
        if loading:
            self._show_status(message, error=False)
            self._status_label.setStyleSheet("color: #FFC107; padding: 4px;")

    def _run_in_thread(self, func, *args, on_success, on_error):
        """Run a function in a background thread."""
        self._thread = QThread()
        self._worker = _AuthWorker(func, *args)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(on_success)
        self._worker.finished.connect(self._thread.quit)
        self._worker.error.connect(on_error)
        self._worker.error.connect(self._thread.quit)

        self._thread.start()
