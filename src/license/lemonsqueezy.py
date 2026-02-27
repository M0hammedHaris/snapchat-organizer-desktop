"""Lemonsqueezy API client for license verification and management.

This module provides integration with Lemonsqueezy for:
- Online license verification
- License activation/deactivation
- Customer management
- Webhook handling

For setup:
1. Create a Lemonsqueezy account at https://lemonsqueezy.com
2. Create a store and product
3. Generate an API key
4. Configure the API key in the application settings
"""

import json
import hashlib
import hmac
from typing import Dict, Optional, Any
from datetime import datetime

import requests

from ..utils.config import APP_DIR
from ..utils.logger import get_logger

logger = get_logger(__name__)

# Lemonsqueezy API configuration
LEMONSQUEEZY_API_URL = "https://api.lemonsqueezy.com/v1"
LEMONSQUEEZY_CONFIG_FILE = APP_DIR / "lemonsqueezy.json"

# Default timeout for API requests (seconds)
API_TIMEOUT = 30


class LemonsqueezyConfig:
    """Configuration for Lemonsqueezy integration."""
    
    def __init__(self):
        self.api_key: Optional[str] = None
        self.store_id: Optional[str] = None
        self.product_id: Optional[str] = None
        self.webhook_secret: Optional[str] = None
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from file."""
        try:
            if LEMONSQUEEZY_CONFIG_FILE.exists():
                with open(LEMONSQUEEZY_CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    self.api_key = config.get('api_key')
                    self.store_id = config.get('store_id')
                    self.product_id = config.get('product_id')
                    self.webhook_secret = config.get('webhook_secret')
                    logger.debug("Lemonsqueezy config loaded")
        except Exception as e:
            logger.warning(f"Failed to load Lemonsqueezy config: {e}")
    
    def save_config(self) -> bool:
        """Save configuration to file.
        
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            config = {
                'api_key': self.api_key,
                'store_id': self.store_id,
                'product_id': self.product_id,
                'webhook_secret': self.webhook_secret,
            }
            with open(LEMONSQUEEZY_CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
            logger.info("Lemonsqueezy config saved")
            return True
        except Exception as e:
            logger.error(f"Failed to save Lemonsqueezy config: {e}")
            return False
    
    @property
    def is_configured(self) -> bool:
        """Check if Lemonsqueezy is configured."""
        return bool(self.api_key and self.store_id)


class LemonsqueezyClient:
    """Client for Lemonsqueezy API interactions."""
    
    def __init__(self, config: Optional[LemonsqueezyConfig] = None):
        """Initialize the client.
        
        Args:
            config: Optional configuration object (creates new if not provided)
        """
        self.config = config or LemonsqueezyConfig()
        self._session = requests.Session()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        return {
            'Accept': 'application/vnd.api+json',
            'Content-Type': 'application/vnd.api+json',
            'Authorization': f'Bearer {self.config.api_key}',
        }
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make an API request to Lemonsqueezy.
        
        Args:
            method: HTTP method (GET, POST, PATCH, DELETE)
            endpoint: API endpoint (without base URL)
            data: Optional request body
            
        Returns:
            JSON response data
            
        Raises:
            LemonsqueezyError: If the request fails
        """
        if not self.config.is_configured:
            raise LemonsqueezyError("Lemonsqueezy is not configured")
        
        url = f"{LEMONSQUEEZY_API_URL}/{endpoint}"
        
        try:
            response = self._session.request(
                method=method,
                url=url,
                headers=self._get_headers(),
                json=data,
                timeout=API_TIMEOUT
            )
            
            logger.debug(f"Lemonsqueezy API {method} {endpoint}: {response.status_code}")
            
            if response.status_code == 404:
                raise LemonsqueezyError("Resource not found")
            
            if response.status_code == 401:
                raise LemonsqueezyError("Invalid API key")
            
            if response.status_code >= 400:
                error_data = response.json() if response.text else {}
                error_msg = error_data.get('errors', [{'detail': 'Unknown error'}])[0].get('detail', 'Unknown error')
                raise LemonsqueezyError(f"API error: {error_msg}")
            
            return response.json() if response.text else {}
            
        except requests.exceptions.Timeout:
            logger.error("Lemonsqueezy API request timed out")
            raise LemonsqueezyError("Request timed out")
        except requests.exceptions.ConnectionError:
            logger.error("Failed to connect to Lemonsqueezy API")
            raise LemonsqueezyError("Connection failed - check your internet connection")
        except requests.exceptions.RequestException as e:
            logger.error(f"Lemonsqueezy API request failed: {e}")
            raise LemonsqueezyError(f"Request failed: {str(e)}")
    
    def verify_license(self, license_key: str) -> Dict[str, Any]:
        """Verify a license key with Lemonsqueezy.
        
        Args:
            license_key: The license key to verify
            
        Returns:
            License verification result
        """
        logger.info(f"Verifying license with Lemonsqueezy: {license_key[:8]}...")
        
        try:
            # Use the licenses validation endpoint
            data = {
                "license_key": license_key
            }
            
            response = self._session.post(
                f"{LEMONSQUEEZY_API_URL}/licenses/validate",
                headers=self._get_headers(),
                json=data,
                timeout=API_TIMEOUT
            )
            
            result = response.json() if response.text else {}
            
            if response.status_code == 200:
                logger.info("License verified successfully")
                return {
                    'valid': True,
                    'license_key': result.get('license_key', {}).get('key'),
                    'status': result.get('license_key', {}).get('status'),
                    'activation_limit': result.get('license_key', {}).get('activation_limit'),
                    'activations_count': result.get('license_key', {}).get('activations_count'),
                    'expires_at': result.get('license_key', {}).get('expires_at'),
                    'meta': result.get('meta', {}),
                }
            else:
                logger.warning("License verification failed")
                return {
                    'valid': False,
                    'error': result.get('error', 'Verification failed'),
                }
                
        except LemonsqueezyError:
            raise
        except Exception as e:
            logger.error(f"License verification error: {e}")
            return {
                'valid': False,
                'error': str(e),
            }
    
    def activate_license(
        self,
        license_key: str,
        instance_name: str
    ) -> Dict[str, Any]:
        """Activate a license key for an instance.
        
        Args:
            license_key: The license key to activate
            instance_name: Name of this device/instance
            
        Returns:
            Activation result
        """
        logger.info(f"Activating license with Lemonsqueezy: {license_key[:8]}...")
        
        try:
            data = {
                "license_key": license_key,
                "instance_name": instance_name
            }
            
            response = self._session.post(
                f"{LEMONSQUEEZY_API_URL}/licenses/activate",
                headers=self._get_headers(),
                json=data,
                timeout=API_TIMEOUT
            )
            
            result = response.json() if response.text else {}
            
            if response.status_code == 200:
                logger.info("License activated successfully")
                return {
                    'activated': True,
                    'instance_id': result.get('instance', {}).get('id'),
                    'instance_name': result.get('instance', {}).get('name'),
                    'created_at': result.get('instance', {}).get('created_at'),
                    'meta': result.get('meta', {}),
                }
            else:
                error_msg = result.get('error', 'Activation failed')
                logger.warning(f"License activation failed: {error_msg}")
                return {
                    'activated': False,
                    'error': error_msg,
                }
                
        except LemonsqueezyError:
            raise
        except Exception as e:
            logger.error(f"License activation error: {e}")
            return {
                'activated': False,
                'error': str(e),
            }
    
    def deactivate_license(
        self,
        license_key: str,
        instance_id: str
    ) -> Dict[str, Any]:
        """Deactivate a license key instance.
        
        Args:
            license_key: The license key
            instance_id: Instance ID to deactivate
            
        Returns:
            Deactivation result
        """
        logger.info(f"Deactivating license instance: {instance_id}")
        
        try:
            data = {
                "license_key": license_key,
                "instance_id": instance_id
            }
            
            response = self._session.post(
                f"{LEMONSQUEEZY_API_URL}/licenses/deactivate",
                headers=self._get_headers(),
                json=data,
                timeout=API_TIMEOUT
            )
            
            result = response.json() if response.text else {}
            
            if response.status_code == 200:
                logger.info("License deactivated successfully")
                return {
                    'deactivated': True,
                }
            else:
                error_msg = result.get('error', 'Deactivation failed')
                logger.warning(f"License deactivation failed: {error_msg}")
                return {
                    'deactivated': False,
                    'error': error_msg,
                }
                
        except LemonsqueezyError:
            raise
        except Exception as e:
            logger.error(f"License deactivation error: {e}")
            return {
                'deactivated': False,
                'error': str(e),
            }
    
    def get_customer(self, customer_id: str) -> Dict[str, Any]:
        """Get customer information.
        
        Args:
            customer_id: Lemonsqueezy customer ID
            
        Returns:
            Customer data
        """
        return self._make_request('GET', f'customers/{customer_id}')
    
    def get_license_keys(self, customer_id: Optional[str] = None) -> Dict[str, Any]:
        """Get license keys, optionally filtered by customer.
        
        Args:
            customer_id: Optional customer ID to filter by
            
        Returns:
            License keys data
        """
        endpoint = 'license-keys'
        if customer_id:
            endpoint += f'?filter[customer_id]={customer_id}'
        
        return self._make_request('GET', endpoint)


class LemonsqueezyError(Exception):
    """Exception raised for Lemonsqueezy API errors."""
    pass


def verify_webhook_signature(
    payload: bytes,
    signature: str,
    secret: str
) -> bool:
    """Verify a webhook signature from Lemonsqueezy.
    
    Args:
        payload: Raw request body
        signature: X-Signature header value
        secret: Webhook secret
        
    Returns:
        True if signature is valid, False otherwise
    """
    expected = hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected)


def parse_webhook_event(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Parse a webhook event from Lemonsqueezy.
    
    Args:
        payload: Webhook payload
        
    Returns:
        Parsed event data
    """
    event_name = payload.get('meta', {}).get('event_name', 'unknown')
    data = payload.get('data', {})
    
    return {
        'event': event_name,
        'data': data,
        'attributes': data.get('attributes', {}),
        'relationships': data.get('relationships', {}),
        'meta': payload.get('meta', {}),
    }


# Webhook event handlers
WEBHOOK_HANDLERS = {}


def webhook_handler(event_name: str):
    """Decorator to register a webhook event handler.
    
    Args:
        event_name: Name of the event to handle
        
    Example:
        @webhook_handler('license_key_created')
        def handle_license_created(event_data):
            # Process the event
            pass
    """
    def decorator(func):
        WEBHOOK_HANDLERS[event_name] = func
        return func
    return decorator


def process_webhook(payload: Dict[str, Any]) -> bool:
    """Process an incoming webhook event.
    
    Args:
        payload: Webhook payload
        
    Returns:
        True if processed successfully, False otherwise
    """
    event = parse_webhook_event(payload)
    event_name = event['event']
    
    logger.info(f"Processing webhook event: {event_name}")
    
    handler = WEBHOOK_HANDLERS.get(event_name)
    if handler:
        try:
            handler(event)
            return True
        except Exception as e:
            logger.error(f"Webhook handler error: {e}")
            return False
    else:
        logger.warning(f"No handler for webhook event: {event_name}")
        return True  # Not an error, just unhandled


# Register default webhook handlers

@webhook_handler('license_key_created')
def _handle_license_created(event: Dict[str, Any]) -> None:
    """Handle license key creation webhook."""
    from .manager import get_license_manager
    from .models import License, get_session
    
    attrs = event.get('attributes', {})
    license_key = attrs.get('key')
    
    if license_key:
        logger.info(f"New license key created: {license_key[:8]}...")
        # The license will be activated when the user enters the key


@webhook_handler('order_created')
def _handle_order_created(event: Dict[str, Any]) -> None:
    """Handle order creation webhook."""
    attrs = event.get('attributes', {})
    order_id = attrs.get('id')
    status = attrs.get('status')
    
    logger.info(f"Order created: {order_id}, status: {status}")


@webhook_handler('subscription_updated')
def _handle_subscription_updated(event: Dict[str, Any]) -> None:
    """Handle subscription update webhook."""
    attrs = event.get('attributes', {})
    status = attrs.get('status')
    
    logger.info(f"Subscription updated: status={status}")
    
    # If subscription is cancelled or expired, we might want to
    # update the local license status


# Global client getter
_client: Optional[LemonsqueezyClient] = None


def get_lemonsqueezy_client() -> LemonsqueezyClient:
    """Get the global Lemonsqueezy client instance.
    
    Returns:
        LemonsqueezyClient instance
    """
    global _client
    if _client is None:
        _client = LemonsqueezyClient()
    return _client
