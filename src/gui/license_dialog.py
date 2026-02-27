"""License dialog for license management.

This module provides a dialog where users can:
- View their current license status
- Enter and activate license keys
- Start a free trial
- View registered devices
- Manage their subscription
"""

import logging
from typing import Optional

from PySide6.QtCore import Qt, Signal, Slot, QTimer
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
    QFormLayout,
    QMessageBox,
    QProgressBar,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QFrame,
    QSpacerItem,
    QSizePolicy,
)
from PySide6.QtGui import QFont

from src.license import (
    LicenseManager,
    get_license_manager,
    LicenseStatus,
    ValidationResult,
    TrialStatus,
)
from src.utils.config import (
    APP_NAME,
    APP_VERSION,
    TIER_FREE,
    TIER_PRO,
    TIER_PREMIUM,
    TRIAL_DURATION_DAYS,
)

logger = logging.getLogger(__name__)


class LicenseDialog(QDialog):
    """Dialog for license management.
    
    Provides tabs for:
    - Status: Current license status and trial information
    - Activate: Enter and activate license keys
    - Devices: View and manage registered devices
    - Features: View feature access by tier
    
    Signals:
        license_changed: Emitted when license status changes
    """

    license_changed = Signal(dict)  # Emits license info dictionary

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize the license dialog.
        
        Args:
            parent: Optional parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("License Management")
        self.setMinimumSize(650, 550)
        
        self._license_manager: LicenseManager = get_license_manager()
        
        self._setup_ui()
        self._refresh_status()
        logger.info("License dialog initialized")

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Create tab widget
        self._tab_widget = QTabWidget()
        self._tab_widget.addTab(self._create_status_tab(), "Status")
        self._tab_widget.addTab(self._create_activate_tab(), "Activate")
        self._tab_widget.addTab(self._create_devices_tab(), "Devices")
        self._tab_widget.addTab(self._create_features_tab(), "Features")

        layout.addWidget(self._tab_widget)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._refresh_status)
        button_layout.addWidget(refresh_btn)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        close_btn.setDefault(True)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

    def _create_status_tab(self) -> QWidget:
        """Create the status tab.
        
        Returns:
            QWidget containing the status tab content
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # Status header
        self._status_header = QLabel()
        self._status_header.setObjectName("status_header")
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        self._status_header.setFont(header_font)
        self._status_header.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._status_header)

        # Status details group
        details_group = QGroupBox("License Details")
        details_layout = QFormLayout(details_group)
        details_layout.setSpacing(10)

        self._tier_label = QLabel()
        self._status_label = QLabel()
        self._expiry_label = QLabel()
        self._key_label = QLabel()

        details_layout.addRow("Tier:", self._tier_label)
        details_layout.addRow("Status:", self._status_label)
        details_layout.addRow("Expires:", self._expiry_label)
        details_layout.addRow("License Key:", self._key_label)

        layout.addWidget(details_group)

        # Trial section
        self._trial_group = QGroupBox("Free Trial")
        trial_layout = QVBoxLayout(self._trial_group)
        trial_layout.setSpacing(10)

        self._trial_status_label = QLabel()
        self._trial_status_label.setWordWrap(True)
        trial_layout.addWidget(self._trial_status_label)

        # Trial progress bar (for active trials)
        self._trial_progress = QProgressBar()
        self._trial_progress.setMinimum(0)
        self._trial_progress.setMaximum(TRIAL_DURATION_DAYS)
        trial_layout.addWidget(self._trial_progress)

        # Start trial button
        self._start_trial_btn = QPushButton(f"Start {TRIAL_DURATION_DAYS}-Day Free Trial")
        self._start_trial_btn.clicked.connect(self._start_trial)
        trial_layout.addWidget(self._start_trial_btn)

        layout.addWidget(self._trial_group)

        # Upgrade button
        upgrade_layout = QHBoxLayout()
        upgrade_layout.addStretch()
        
        self._upgrade_btn = QPushButton("Upgrade to Pro")
        self._upgrade_btn.setObjectName("upgrade_button")
        self._upgrade_btn.setMinimumHeight(40)
        self._upgrade_btn.clicked.connect(self._open_upgrade_page)
        upgrade_layout.addWidget(self._upgrade_btn)
        
        upgrade_layout.addStretch()
        layout.addLayout(upgrade_layout)

        layout.addStretch()

        return widget

    def _create_activate_tab(self) -> QWidget:
        """Create the activate tab.
        
        Returns:
            QWidget containing the activation form
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # Instructions
        instructions = QLabel(
            "Enter your license key below to activate the Pro version.\n"
            "License keys are sent via email after purchase."
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        # License key input group
        key_group = QGroupBox("Enter License Key")
        key_layout = QVBoxLayout(key_group)
        key_layout.setSpacing(10)

        # Key input fields (5 segments)
        input_layout = QHBoxLayout()
        input_layout.setSpacing(5)

        self._key_inputs = []
        for i in range(5):
            key_input = QLineEdit()
            key_input.setMaxLength(5)
            key_input.setPlaceholderText("XXXXX")
            key_input.setAlignment(Qt.AlignCenter)
            key_input.setMinimumWidth(70)
            key_input.setMaximumWidth(90)
            key_input.textChanged.connect(lambda text, idx=i: self._on_key_input_changed(idx, text))
            self._key_inputs.append(key_input)
            input_layout.addWidget(key_input)
            
            if i < 4:
                dash = QLabel("-")
                dash.setAlignment(Qt.AlignCenter)
                input_layout.addWidget(dash)

        key_layout.addLayout(input_layout)

        # Paste button
        paste_layout = QHBoxLayout()
        paste_btn = QPushButton("Paste from Clipboard")
        paste_btn.clicked.connect(self._paste_key)
        paste_layout.addStretch()
        paste_layout.addWidget(paste_btn)
        paste_layout.addStretch()
        key_layout.addLayout(paste_layout)

        layout.addWidget(key_group)

        # Activation button and status
        self._activate_btn = QPushButton("Activate License")
        self._activate_btn.setMinimumHeight(40)
        self._activate_btn.clicked.connect(self._activate_license)
        layout.addWidget(self._activate_btn)

        self._activation_status = QLabel()
        self._activation_status.setWordWrap(True)
        self._activation_status.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._activation_status)

        layout.addStretch()

        # Purchase section
        purchase_group = QGroupBox("Don't have a license?")
        purchase_layout = QVBoxLayout(purchase_group)
        
        purchase_label = QLabel(
            "Purchase a Pro license to unlock all features including "
            "memory downloading, overlay compositing, and more."
        )
        purchase_label.setWordWrap(True)
        purchase_layout.addWidget(purchase_label)
        
        buy_btn = QPushButton("Buy Now")
        buy_btn.clicked.connect(self._open_purchase_page)
        purchase_layout.addWidget(buy_btn)
        
        layout.addWidget(purchase_group)

        return widget

    def _create_devices_tab(self) -> QWidget:
        """Create the devices tab.
        
        Returns:
            QWidget containing the device management interface
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # Info label
        info_label = QLabel(
            "Your license can be activated on multiple devices. "
            "View and manage your registered devices below."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Device table
        self._device_table = QTableWidget()
        self._device_table.setColumnCount(4)
        self._device_table.setHorizontalHeaderLabels([
            "Device Name", "Platform", "Registered", "Status"
        ])
        self._device_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._device_table.setSelectionBehavior(QTableWidget.SelectRows)
        self._device_table.setSelectionMode(QTableWidget.SingleSelection)
        layout.addWidget(self._device_table)

        # Device info
        self._device_info_label = QLabel()
        self._device_info_label.setWordWrap(True)
        layout.addWidget(self._device_info_label)

        # Deactivate button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self._deactivate_btn = QPushButton("Deactivate This Device")
        self._deactivate_btn.clicked.connect(self._deactivate_device)
        button_layout.addWidget(self._deactivate_btn)
        
        layout.addLayout(button_layout)

        return widget

    def _create_features_tab(self) -> QWidget:
        """Create the features tab.
        
        Returns:
            QWidget containing the feature comparison
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # Feature comparison table
        self._feature_table = QTableWidget()
        self._feature_table.setColumnCount(4)
        self._feature_table.setHorizontalHeaderLabels([
            "Feature", "Free", "Pro", "Premium"
        ])
        self._feature_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._feature_table.setSelectionMode(QTableWidget.NoSelection)
        
        # Populate features
        features = [
            ("Organize Chat Media", True, True, True),
            ("Organize by Year", True, True, True),
            ("Fix Timestamps", True, True, True),
            ("Download Memories", False, True, True),
            ("Remove Duplicates", False, True, True),
            ("Verify Files", False, True, True),
            ("GPS Embedding", False, True, True),
            ("Overlay Compositing", False, True, True),
            ("Timezone Conversion", False, True, True),
            ("Advanced Analytics", False, False, True),
            ("Cloud Backup", False, False, True),
            ("Monthly File Limit", "100", "Unlimited", "Unlimited"),
        ]
        
        self._feature_table.setRowCount(len(features))
        for row, (feature, free, pro, premium) in enumerate(features):
            self._feature_table.setItem(row, 0, QTableWidgetItem(feature))
            
            for col, value in enumerate([free, pro, premium], start=1):
                if isinstance(value, bool):
                    text = "✓" if value else "✗"
                else:
                    text = str(value)
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignCenter)
                self._feature_table.setItem(row, col, item)
        
        layout.addWidget(self._feature_table)

        # Current tier indicator
        self._current_tier_label = QLabel()
        self._current_tier_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._current_tier_label)

        return widget

    @Slot()
    def _refresh_status(self):
        """Refresh the license status display."""
        logger.debug("Refreshing license status")
        
        status = self._license_manager.get_current_status()
        trial_status = self._license_manager.get_trial_status()
        
        # Update status tab
        self._update_status_display(status, trial_status)
        
        # Update devices tab
        self._update_devices_display()
        
        # Update features tab
        self._update_features_display()

    def _update_status_display(self, status: ValidationResult, trial_status: TrialStatus):
        """Update the status tab display.
        
        Args:
            status: Current license validation result
            trial_status: Current trial status
        """
        # Status header
        if status.status == LicenseStatus.VALID:
            tier_name = status.tier.capitalize()
            self._status_header.setText(f"🎉 {tier_name} License Active")
            self._status_header.setStyleSheet("color: #27ae60;")
        elif status.status == LicenseStatus.TRIAL_ACTIVE:
            self._status_header.setText("🎁 Trial Active")
            self._status_header.setStyleSheet("color: #3498db;")
        elif status.status in (LicenseStatus.EXPIRED, LicenseStatus.TRIAL_EXPIRED):
            self._status_header.setText("⚠️ License Expired")
            self._status_header.setStyleSheet("color: #e74c3c;")
        else:
            self._status_header.setText("Free Tier")
            self._status_header.setStyleSheet("color: #7f8c8d;")

        # License details
        tier_names = {
            TIER_FREE: "Free",
            TIER_PRO: "Pro",
            TIER_PREMIUM: "Premium",
        }
        self._tier_label.setText(tier_names.get(status.tier, status.tier.capitalize()))
        self._status_label.setText(status.status.value.replace("_", " ").title())
        
        if status.days_remaining is not None:
            if status.days_remaining == 0:
                self._expiry_label.setText("Expires today")
            elif status.days_remaining == 1:
                self._expiry_label.setText("1 day remaining")
            else:
                self._expiry_label.setText(f"{status.days_remaining} days remaining")
        else:
            self._expiry_label.setText("Lifetime" if status.is_paid else "N/A")

        if status.license_key:
            # Mask middle of key
            key = status.license_key
            masked = f"{key[:9]}...{key[-5:]}"
            self._key_label.setText(masked)
        else:
            self._key_label.setText("Not activated")

        # Trial section
        if trial_status.is_active:
            self._trial_status_label.setText(
                f"Your {TRIAL_DURATION_DAYS}-day trial is active!\n"
                f"{trial_status.days_remaining} days remaining.\n"
                f"Files processed: {trial_status.files_processed}"
            )
            self._trial_progress.setValue(TRIAL_DURATION_DAYS - trial_status.days_remaining)
            self._trial_progress.setVisible(True)
            self._start_trial_btn.setVisible(False)
            self._trial_group.setVisible(True)
        elif trial_status.is_available and not status.is_paid:
            self._trial_status_label.setText(
                f"Try all Pro features free for {TRIAL_DURATION_DAYS} days!\n"
                "No credit card required."
            )
            self._trial_progress.setVisible(False)
            self._start_trial_btn.setVisible(True)
            self._trial_group.setVisible(True)
        elif trial_status.is_expired and not status.is_paid:
            self._trial_status_label.setText(
                "Your trial has expired.\n"
                "Upgrade to Pro to continue using all features."
            )
            self._trial_progress.setValue(TRIAL_DURATION_DAYS)
            self._trial_progress.setVisible(True)
            self._start_trial_btn.setVisible(False)
            self._trial_group.setVisible(True)
        else:
            self._trial_group.setVisible(False)

        # Upgrade button visibility
        self._upgrade_btn.setVisible(not status.is_paid)

    def _update_devices_display(self):
        """Update the devices tab display."""
        devices = self._license_manager.get_registered_devices()
        
        self._device_table.setRowCount(len(devices))
        
        for row, device in enumerate(devices):
            self._device_table.setItem(row, 0, QTableWidgetItem(device.get('device_name', 'Unknown')))
            self._device_table.setItem(row, 1, QTableWidgetItem(device.get('platform', 'Unknown')))
            
            registered = device.get('registered_at', '')
            if registered:
                # Format date
                registered = registered[:10]  # Just the date part
            self._device_table.setItem(row, 2, QTableWidgetItem(registered))
            
            status = "Active" if device.get('is_active') else "Inactive"
            if device.get('is_current'):
                status += " (This device)"
            self._device_table.setItem(row, 3, QTableWidgetItem(status))
        
        if not devices:
            self._device_info_label.setText("No devices registered.")
            self._deactivate_btn.setEnabled(False)
        else:
            status = self._license_manager.get_current_status()
            if status.is_paid:
                self._device_info_label.setText(
                    f"{len(devices)} device(s) registered."
                )
                self._deactivate_btn.setEnabled(True)
            else:
                self._device_info_label.setText(
                    "Activate a license to manage devices."
                )
                self._deactivate_btn.setEnabled(False)

    def _update_features_display(self):
        """Update the features tab display."""
        tier = self._license_manager.current_tier
        tier_names = {
            TIER_FREE: "Free",
            TIER_PRO: "Pro", 
            TIER_PREMIUM: "Premium",
        }
        self._current_tier_label.setText(
            f"Your current tier: <b>{tier_names.get(tier, tier.capitalize())}</b>"
        )

    def _on_key_input_changed(self, index: int, text: str):
        """Handle key input field changes.
        
        Args:
            index: Input field index
            text: New text value
        """
        # Auto-uppercase
        self._key_inputs[index].blockSignals(True)
        self._key_inputs[index].setText(text.upper())
        self._key_inputs[index].blockSignals(False)
        
        # Auto-advance to next field
        if len(text) == 5 and index < 4:
            self._key_inputs[index + 1].setFocus()

    @Slot()
    def _paste_key(self):
        """Paste license key from clipboard."""
        from PySide6.QtWidgets import QApplication
        
        clipboard = QApplication.clipboard()
        text = clipboard.text().strip().upper()
        
        # Remove dashes and spaces
        clean = ''.join(c for c in text if c.isalnum())
        
        # Fill in segments
        for i, input_field in enumerate(self._key_inputs):
            start = i * 5
            end = start + 5
            segment = clean[start:end] if start < len(clean) else ""
            input_field.setText(segment)

    def _get_entered_key(self) -> str:
        """Get the full license key from input fields.
        
        Returns:
            License key string
        """
        segments = [inp.text().strip().upper() for inp in self._key_inputs]
        return '-'.join(segments)

    @Slot()
    def _activate_license(self):
        """Activate the entered license key."""
        key = self._get_entered_key()
        
        if not key or len(key.replace('-', '')) != 25:
            self._activation_status.setText("Please enter a complete license key.")
            self._activation_status.setStyleSheet("color: #e74c3c;")
            return
        
        self._activation_status.setText("Activating...")
        self._activation_status.setStyleSheet("color: #7f8c8d;")
        self._activate_btn.setEnabled(False)
        
        # Activate in the next event loop iteration
        QTimer.singleShot(100, lambda: self._do_activation(key))

    def _do_activation(self, key: str):
        """Perform the actual activation.
        
        Args:
            key: License key to activate
        """
        result = self._license_manager.activate(key)
        
        if result.is_valid:
            self._activation_status.setText("✓ License activated successfully!")
            self._activation_status.setStyleSheet("color: #27ae60;")
            self.license_changed.emit(self._license_manager.get_license_info())
            
            # Refresh status
            self._refresh_status()
            
            # Switch to status tab
            QTimer.singleShot(1000, lambda: self._tab_widget.setCurrentIndex(0))
        else:
            self._activation_status.setText(f"✗ {result.message}")
            self._activation_status.setStyleSheet("color: #e74c3c;")
        
        self._activate_btn.setEnabled(True)

    @Slot()
    def _start_trial(self):
        """Start a free trial."""
        reply = QMessageBox.question(
            self,
            "Start Free Trial",
            f"Start your {TRIAL_DURATION_DAYS}-day free trial?\n\n"
            "You'll get full access to all Pro features.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply == QMessageBox.Yes:
            trial_status = self._license_manager.start_trial()
            
            if trial_status.is_active:
                QMessageBox.information(
                    self,
                    "Trial Started",
                    f"Your {TRIAL_DURATION_DAYS}-day trial has started!\n"
                    "Enjoy full access to all Pro features."
                )
                self.license_changed.emit(self._license_manager.get_license_info())
                self._refresh_status()
            else:
                QMessageBox.warning(
                    self,
                    "Trial Unavailable",
                    "Unable to start trial. You may have already used your trial period."
                )

    @Slot()
    def _deactivate_device(self):
        """Deactivate the current device."""
        reply = QMessageBox.question(
            self,
            "Deactivate Device",
            "Are you sure you want to deactivate this device?\n\n"
            "You will need to re-enter your license key to use Pro features.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self._license_manager.deactivate():
                QMessageBox.information(
                    self,
                    "Device Deactivated",
                    "This device has been deactivated.\n"
                    "You can activate it again or use another device."
                )
                self.license_changed.emit(self._license_manager.get_license_info())
                self._refresh_status()
            else:
                QMessageBox.warning(
                    self,
                    "Deactivation Failed",
                    "Failed to deactivate device. Please try again."
                )

    @Slot()
    def _open_upgrade_page(self):
        """Open the upgrade/purchase page in browser."""
        import webbrowser
        # TODO: Replace with actual purchase URL
        webbrowser.open("https://snapchat-organizer.com/upgrade")

    @Slot()
    def _open_purchase_page(self):
        """Open the purchase page in browser."""
        import webbrowser
        # TODO: Replace with actual purchase URL
        webbrowser.open("https://snapchat-organizer.com/buy")
