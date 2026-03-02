"""License manager - handles local license state, device ID, and session persistence.

Manages the license lifecycle on the desktop app side:
- Generates and stores a stable device fingerprint
- Persists session tokens and license data locally
- Validates license on startup via the API
- Provides the current license tier for feature gating
"""

import json
import hashlib
import platform
import uuid
import logging
from typing import Optional, Dict, Any

import sentry_sdk

from ..utils.config import APP_DIR, TIER_FREE, DEVICE_LIMITS
from .api_client import LicenseAPIClient, APIError

logger = logging.getLogger(__name__)

# Local storage file for session/license data
LICENSE_DATA_FILE = APP_DIR / "license_data.json"


class LicenseManager:
    """Manages license state for the desktop application."""

    def __init__(self):
        self._api = LicenseAPIClient()
        self._data: Dict[str, Any] = {}
        self._device_id: Optional[str] = None
        self._load_local_data()

    @property
    def is_logged_in(self) -> bool:
        """Check if user has a valid session token."""
        return bool(self._data.get('token'))

    @property
    def current_tier(self) -> str:
        """Get the current license tier (free/pro/premium)."""
        return self._data.get('tier', TIER_FREE)

    @property
    def is_trial(self) -> bool:
        """Check if the current license is a trial."""
        return self._data.get('is_trial', False)

    @property
    def user_email(self) -> Optional[str]:
        """Get the logged-in user's email."""
        return self._data.get('email')

    @property
    def user_name(self) -> Optional[str]:
        """Get the logged-in user's name."""
        return self._data.get('name')

    @property
    def license_key(self) -> Optional[str]:
        """Get the current license key."""
        return self._data.get('license_key')

    @property
    def expires_at(self) -> Optional[str]:
        """Get the license expiry date."""
        return self._data.get('expires_at')

    @property
    def max_devices(self) -> int:
        """Get the maximum number of devices allowed for this tier."""
        return self._data.get('max_devices', DEVICE_LIMITS.get(self.current_tier, 1))

    @property
    def active_devices(self) -> int:
        """Get the number of currently active devices."""
        return self._data.get('active_devices', 0)

    @property
    def device_id(self) -> str:
        """Get or generate this machine's device fingerprint."""
        if not self._device_id:
            self._device_id = self._generate_device_id()
        return self._device_id

    # ── Authentication ──

    def register(self, email: str, password: str, name: str) -> Dict[str, Any]:
        """Register a new account and store session."""
        response = self._api.register(email, password, name)
        if response.get('success'):
            data = response['data']
            self._store_session(data)
        return response

    def login(self, email: str, password: str) -> Dict[str, Any]:
        """Login and store session."""
        response = self._api.login(email, password, self.device_id)
        if response.get('success'):
            data = response['data']
            self._store_session(data)
            # Set Sentry user context for error attribution (no PII)
            user = data.get('user', {})
            sentry_sdk.set_user({
                "id": str(user.get('id', '')),
            })
            sentry_sdk.set_tag("license.tier", data.get('license', {}).get('tier', TIER_FREE))
        return response

    def logout(self):
        """Logout and clear local session."""
        try:
            if self.is_logged_in:
                self._api.logout()
        except APIError:
            pass  # Clear local data regardless
        sentry_sdk.set_user(None)
        self._clear_local_data()

    # ── License validation ──

    def validate_on_startup(self) -> Dict[str, Any]:
        """Validate license with the server on app startup.

        Returns dict with:
            - valid (bool): Whether license is valid
            - tier (str): Current tier
            - offline (bool): True if server unreachable (uses cached data)
        """
        if not self.is_logged_in:
            return {'valid': False, 'tier': TIER_FREE, 'offline': False}

        self._api.token = self._data.get('token')

        try:
            response = self._api.validate_license(
                device_id=self.device_id,
                device_name=platform.node(),
                platform=f"{platform.system()} {platform.release()}",
            )

            if response.get('success'):
                data = response['data']
                self._data['tier'] = data.get('tier', TIER_FREE)
                self._data['is_trial'] = data.get('is_trial', False)
                self._data['expires_at'] = data.get('expires_at')
                self._data['license_key'] = data.get('license_key')
                self._data['valid'] = data.get('valid', False)
                self._data['max_devices'] = data.get('max_devices', DEVICE_LIMITS.get(data.get('tier', TIER_FREE), 1))
                self._data['active_devices'] = data.get('active_devices', 0)
                self._save_local_data()

                return {
                    'valid': data.get('valid', False),
                    'tier': data.get('tier', TIER_FREE),
                    'is_trial': data.get('is_trial', False),
                    'expires_at': data.get('expires_at'),
                    'reason': data.get('reason'),
                    'offline': False,
                }

            return {'valid': False, 'tier': TIER_FREE, 'offline': False}

        except APIError as e:
            logger.warning(f"License validation failed (offline?): {e}")
            # Use cached data when offline
            return {
                'valid': self._data.get('valid', False),
                'tier': self._data.get('tier', TIER_FREE),
                'offline': True,
            }

    # ── Stripe / Upgrade ──

    def get_checkout_url(self, tier: str) -> Optional[str]:
        """Get Stripe checkout URL for upgrading.

        In mock mode, returns None — use confirm_upgrade() instead.
        """
        self._api.token = self._data.get('token')
        try:
            response = self._api.create_checkout(tier)
            if response.get('success'):
                data = response['data']
                # If mock mode, no browser URL to open
                if data.get('mock'):
                    return None
                return data.get('checkout_url')
        except APIError as e:
            logger.error(f"Failed to create checkout: {e}")
        return None

    def is_mock_stripe(self) -> bool:
        """Check if the server is running in mock Stripe mode."""
        self._api.token = self._data.get('token')
        try:
            response = self._api.create_checkout('pro')
            if response.get('success'):
                return bool(response['data'].get('mock'))
        except APIError:
            pass
        return False

    def confirm_upgrade(self, tier: str) -> Dict[str, Any]:
        """Confirm a subscription upgrade.

        In mock mode, calls the mock-confirm endpoint directly.
        In real mode, the upgrade happens via Stripe webhook — this
        method re-validates the license to pick up changes.

        Returns:
            Dict with success status and license details.
        """
        self._api.token = self._data.get('token')
        try:
            response = self._api.mock_confirm_payment(tier)
            if response.get('success'):
                data = response['data']
                self._data['tier'] = data.get('tier', self._data.get('tier'))
                self._data['license_key'] = data.get('license_key', self._data.get('license_key'))
                self._data['is_trial'] = data.get('is_trial', False)
                self._data['expires_at'] = data.get('expires_at')
                self._data['max_devices'] = data.get('max_devices', DEVICE_LIMITS.get(data.get('tier', self.current_tier), 1))
                self._data['valid'] = True
                self._save_local_data()
            return response
        except APIError as e:
            logger.error(f"Failed to confirm upgrade: {e}")
            return {'success': False, 'error': str(e)}

    # ── Device management ──

    def get_devices(self) -> list:
        """Get list of activated devices."""
        self._api.token = self._data.get('token')
        try:
            response = self._api.list_devices()
            if response.get('success'):
                return response['data'].get('devices', [])
        except APIError as e:
            logger.error(f"Failed to list devices: {e}")
        return []

    def deactivate_device(self, device_id: str) -> bool:
        """Deactivate a device."""
        self._api.token = self._data.get('token')
        try:
            response = self._api.deactivate_device(device_id)
            return response.get('success', False)
        except APIError as e:
            logger.error(f"Failed to deactivate device: {e}")
            return False

    # ── Internal ──

    def _store_session(self, data: Dict[str, Any]):
        """Store session data from login/register response."""
        self._data['token'] = data.get('token')
        self._api.token = data.get('token')

        user = data.get('user', {})
        self._data['email'] = user.get('email')
        self._data['name'] = user.get('name')
        self._data['user_id'] = user.get('id')

        license_info = data.get('license')
        if license_info:
            self._data['license_key'] = license_info.get('key')
            self._data['tier'] = license_info.get('tier', TIER_FREE)
            self._data['is_trial'] = license_info.get('is_trial', False)
            self._data['expires_at'] = license_info.get('expires_at')
            self._data['max_devices'] = license_info.get('max_devices', DEVICE_LIMITS.get(license_info.get('tier', TIER_FREE), 1))

        self._save_local_data()

    def _generate_device_id(self) -> str:
        """Generate a stable device fingerprint based on hardware info."""
        # Combine multiple machine identifiers for stability
        components = [
            platform.node(),          # hostname
            platform.machine(),       # architecture
            platform.processor(),     # processor info
        ]

        # Try to get MAC address (stable across reboots)
        try:
            mac = uuid.getnode()
            components.append(str(mac))
        except Exception:
            pass

        # Try platform-specific identifiers
        try:
            if platform.system() == 'Darwin':
                import subprocess
                result = subprocess.run(
                    ['ioreg', '-rd1', '-c', 'IOPlatformExpertDevice'],
                    capture_output=True, text=True, timeout=5,
                    shell=False,
                )
                for line in result.stdout.split('\n'):
                    if 'IOPlatformSerialNumber' in line:
                        serial = line.split('"')[-2]
                        components.append(serial)
                        break
            elif platform.system() == 'Windows':
                import subprocess
                result = subprocess.run(
                    ['wmic', 'csproduct', 'get', 'UUID'],
                    capture_output=True, text=True, timeout=5,
                    shell=False,
                )
                lines = [line.strip() for line in result.stdout.split('\n') if line.strip()]
                if len(lines) > 1:
                    components.append(lines[1])
        except Exception:
            pass

        fingerprint = '|'.join(components)
        return hashlib.sha256(fingerprint.encode()).hexdigest()[:32]

    def _load_local_data(self):
        """Load persisted license data from disk."""
        try:
            if LICENSE_DATA_FILE.exists():
                with open(LICENSE_DATA_FILE, 'r', encoding='utf-8') as f:
                    self._data = json.load(f)
                if self._data.get('token'):
                    self._api.token = self._data['token']
                logger.debug("Loaded local license data")
        except Exception as e:
            logger.warning(f"Failed to load license data: {e}")
            self._data = {}

    def _save_local_data(self):
        """Persist license data to disk with restricted permissions."""
        import os
        try:
            APP_DIR.mkdir(parents=True, exist_ok=True)
            os.chmod(APP_DIR, 0o700)  # Owner-only access on directory
            with open(LICENSE_DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(self._data, f, indent=2)
            os.chmod(LICENSE_DATA_FILE, 0o600)  # Owner read/write only
            logger.debug("Saved local license data")
        except Exception as e:
            logger.error(f"Failed to save license data: {e}")

    def _clear_local_data(self):
        """Clear all local license/session data."""
        self._data = {}
        self._api.token = None
        try:
            if LICENSE_DATA_FILE.exists():
                LICENSE_DATA_FILE.unlink()
        except Exception as e:
            logger.warning(f"Failed to delete license data file: {e}")
