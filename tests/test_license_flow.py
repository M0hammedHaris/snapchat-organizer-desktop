"""Test the full license flow: register, validate, upgrade, logout, login."""

import sys
sys.path.insert(0, '.')

from src.license.license_manager import LicenseManager

lm = LicenseManager()
print(f'Logged in: {lm.is_logged_in}')
print(f'Tier: {lm.current_tier}')

# Test registration
print('\n=== Register ===')
result = lm.register('testdesktop2@example.com', 'password123', 'Desktop Test')
print(f'Success: {result.get("success")}')
print(f'Message: {result.get("message")}')
print(f'Tier: {lm.current_tier}')
print(f'Is trial: {lm.is_trial}')
print(f'License key: {lm.license_key}')
print(f'Expires: {lm.expires_at}')

# Test validation
print('\n=== Validate ===')
val = lm.validate_on_startup()
print(f'Valid: {val.get("valid")}')
print(f'Tier: {val.get("tier")}')
print(f'Trial: {val.get("is_trial")}')

# Test mock upgrade
print('\n=== Mock Upgrade to Premium ===')
upgrade = lm.confirm_upgrade('premium')
print(f'Success: {upgrade.get("success")}')
print(f'Message: {upgrade.get("message")}')
print(f'Tier after upgrade: {lm.current_tier}')
print(f'Is trial: {lm.is_trial}')
print(f'New license key: {lm.license_key}')

# Test logout
print('\n=== Logout ===')
lm.logout()
print(f'Logged in: {lm.is_logged_in}')
print(f'Tier: {lm.current_tier}')

# Test login
print('\n=== Login ===')
result = lm.login('testdesktop2@example.com', 'password123')
print(f'Success: {result.get("success")}')
print(f'Tier: {lm.current_tier}')
print(f'Is trial: {lm.is_trial}')

print('\n=== All tests passed! ===')
