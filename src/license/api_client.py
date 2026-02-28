"""API client for communicating with the Cloudflare Workers license server.

Handles all HTTP requests to the license API including auth, license
validation, Stripe checkout, and device management.
"""

import json
import logging
from typing import Optional, Dict, Any
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

logger = logging.getLogger(__name__)

# License API base URL (Cloudflare Worker)
API_BASE_URL = "https://snapchat-organizer-license-api.haris-1ca.workers.dev"


class LicenseAPIClient:
    """Client for the license server API."""

    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url.rstrip('/')
        self._token: Optional[str] = None

    @property
    def token(self) -> Optional[str]:
        return self._token

    @token.setter
    def token(self, value: Optional[str]):
        self._token = value

    def _request(
        self,
        method: str,
        path: str,
        body: Optional[Dict] = None,
        timeout: int = 15,
    ) -> Dict[str, Any]:
        """Make an HTTP request to the API.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: API path (e.g. /api/auth/login)
            body: Request body (JSON-serializable dict)
            timeout: Request timeout in seconds

        Returns:
            Parsed JSON response dict

        Raises:
            APIError: On HTTP or network errors
        """
        url = f"{self.base_url}{path}"
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "SnapchatOrganizer/1.0",
        }

        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"

        data = json.dumps(body).encode('utf-8') if body else None

        req = Request(url, data=data, headers=headers, method=method)

        try:
            with urlopen(req, timeout=timeout) as resp:
                response_data = json.loads(resp.read().decode('utf-8'))
                return response_data
        except HTTPError as e:
            try:
                error_body = json.loads(e.read().decode('utf-8'))
                error_msg = error_body.get('error', str(e))
            except Exception:
                error_msg = str(e)
            logger.error(f"API error {e.code}: {error_msg}")
            raise APIError(error_msg, e.code)
        except URLError as e:
            logger.error(f"Network error: {e.reason}")
            raise APIError(f"Cannot connect to license server: {e.reason}", 0)
        except Exception as e:
            logger.error(f"Unexpected API error: {e}")
            raise APIError(str(e), 0)

    # ── Auth endpoints ──

    def register(self, email: str, password: str, name: str) -> Dict[str, Any]:
        """Register a new user account.

        Returns:
            Response with token, user info, and trial license.
        """
        return self._request('POST', '/api/auth/register', {
            'email': email,
            'password': password,
            'name': name,
        })

    def login(self, email: str, password: str, device_id: str = None) -> Dict[str, Any]:
        """Login and get session token.

        Returns:
            Response with token, user info, and license info.
        """
        body = {'email': email, 'password': password}
        if device_id:
            body['device_id'] = device_id
        return self._request('POST', '/api/auth/login', body)

    def logout(self) -> Dict[str, Any]:
        """Logout and invalidate current session."""
        result = self._request('POST', '/api/auth/logout')
        self._token = None
        return result

    def get_profile(self) -> Dict[str, Any]:
        """Get current user profile and license info."""
        return self._request('GET', '/api/auth/profile')

    # ── License endpoints ──

    def validate_license(
        self,
        device_id: str,
        device_name: str = None,
        platform: str = None,
    ) -> Dict[str, Any]:
        """Validate license for this device (called on startup).

        Returns:
            Response with valid (bool), tier, and license details.
        """
        return self._request('POST', '/api/license/validate', {
            'device_id': device_id,
            'device_name': device_name,
            'platform': platform,
        })

    def get_license_status(self) -> Dict[str, Any]:
        """Get current license status."""
        return self._request('GET', '/api/license/status')

    def activate_license_key(self, license_key: str) -> Dict[str, Any]:
        """Activate a license key."""
        return self._request('POST', '/api/license/activate', {
            'license_key': license_key,
        })

    # ── Stripe endpoints ──

    def create_checkout(self, tier: str) -> Dict[str, Any]:
        """Create a Stripe Checkout session.

        Returns:
            Response with checkout_url to open in browser.
            In mock mode, also returns mock=True.
        """
        return self._request('POST', '/api/stripe/create-checkout', {
            'tier': tier,
        })

    def mock_confirm_payment(self, tier: str) -> Dict[str, Any]:
        """Confirm a mock payment (mock Stripe mode only).

        Simulates a successful subscription purchase.

        Returns:
            Response with new license details.
        """
        return self._request('POST', '/api/stripe/mock-confirm', {
            'tier': tier,
        })

    # ── Device endpoints ──

    def list_devices(self) -> Dict[str, Any]:
        """List active devices for the current license."""
        return self._request('GET', '/api/device/list')

    def deactivate_device(self, device_id: str) -> Dict[str, Any]:
        """Deactivate a device from the license."""
        return self._request('POST', '/api/device/deactivate', {
            'device_id': device_id,
        })

    # ── Health ──

    def health_check(self) -> bool:
        """Check if the API server is reachable."""
        try:
            resp = self._request('GET', '/api/health')
            return resp.get('status') == 'ok'
        except Exception:
            return False


class APIError(Exception):
    """Error from the license API."""

    def __init__(self, message: str, status_code: int = 0):
        super().__init__(message)
        self.status_code = status_code
